import datetime
import os
import re
import shutil
import signal
import time
import subprocess
import firebase_admin
import pytest
import requests
from appium.options.common import AppiumOptions
from dotenv import load_dotenv
from firebase_admin import credentials
from pathlib import Path

from selenium.common import InvalidSessionIdException, TimeoutException
from selenium import webdriver
from appium import webdriver as appium_webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from helpers.ios.firebase_cleanup_helper import cleanup_user_data
from helpers.web import quest_test_data
from helpers.web.homepage_helper import HomepageHelper
import socket
import subprocess

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

APPIUM_PORT = os.getenv("APPIUM_PORT", "4723")
APPIUM_SERVER_URL = f"http://127.0.0.1:{APPIUM_PORT}"
DEVICE_NAME = os.getenv("DEVICE_NAME", "iPhone 17 Pro")
PLATFORM_VERSION = os.getenv("PLATFORM_VERSION", "26.4")
RV_BUNDLE_ID = os.getenv("RV_BUNDLE_ID", "sbouhussein.github.io-rvsite.RandezVous")
SAFARI_BUNDLE_ID = os.getenv("SAFARI_BUNDLE_ID", "com.apple.mobilesafari")
ANDROID_DEVICE_NAME = os.getenv("ANDROID_DEVICE_NAME", "Pixel_8_API_34")
ANDROID_PLATFORM_VERSION = os.getenv("ANDROID_PLATFORM_VERSION", "14")
APP_CHECK_DEBUG_TOKEN = os.getenv("FIREBASE_APP_CHECK_DEBUG_TOKEN")
WEB_APP_PATH = os.getenv("WEB_APP_PATH", "../../RandezVousSite/rvsite")
REPORT_RETENTION_COUNT = int(os.getenv("REPORT_RETENTION_COUNT", "20"))

def pytest_addoption(parser):
    parser.addoption("--udid", action="store", default="booted", help="UDID of the iOS Simulator")
    parser.addoption("--headless", action="store_true", help="Run the simulator/browser in headless mode")
    parser.addoption("--browser", action="store", default="safari", choices=["safari", "chrome", "firefox"],
                      help="Desktop browser for web tests (Safari has no headless mode)")

def _quit_driver_safely(driver):
    """Close every window, then quit -- each step best-effort so one failure can't leave the
    browser (and its tabs) open. Safari leaves its automation windows behind if the session
    isn't ended cleanly."""
    try:
        for handle in list(driver.window_handles):
            driver.switch_to.window(handle)
            driver.close()
    except Exception:
        pass
    try:
        driver.quit()
    except Exception:
        pass


_SAFARI_AUTOMATION_PATTERN = "Safari.app/Contents/MacOS/Safari --automation"


def _safari_automation_pids():
    out = subprocess.run(["pgrep", "-f", _SAFARI_AUTOMATION_PATTERN], capture_output=True, text=True).stdout
    return {int(p) for p in out.split()}


def _end_safari_automation(pids, grace=3.0, term_wait=5.0):
    """driver.quit() ends the WebDriver session but leaves its `Safari --automation` process
    running indefinitely; the next session then fails with "Safari instance is already paired
    with a different session". Give `pids` (this session's own process) a moment to exit by
    itself, then SIGTERM, then SIGKILL. Never touches any other Safari process."""
    def alive(pid):
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True

    def wait_gone(timeout):
        end = time.time() + timeout
        while time.time() < end and any(alive(p) for p in pids):
            time.sleep(0.25)
        return not any(alive(p) for p in pids)

    if wait_gone(grace):
        return
    for sig, wait in ((signal.SIGTERM, term_wait), (signal.SIGKILL, 2.0)):
        for pid in pids:
            try:
                os.kill(pid, sig)
            except ProcessLookupError:
                pass
        if wait_gone(wait):
            return


def _sweep_leaked_safari_windows():
    """Ends orphaned Safari automation sessions (left by killed or crashed runs, which skip fixture
    teardown). Each safaridriver session is its own `Safari --automation` process -- a leaked one
    keeps a whole Safari instance and its tabs alive -- so kill exactly those. The user's own
    Safari is a different process without --automation and is never touched."""
    subprocess.run(["pkill", "-x", "safaridriver"], capture_output=True)
    subprocess.run(["pkill", "-f", "Safari.app/Contents/MacOS/Safari --automation"], capture_output=True)


def _web_target(request):
    """(npm script, port) for rvsite's dev servers. `npm start` is rvsite's QA target:
    Vite --mode qa on 5174 plus the backend on 3000 (backend/.env.qa), both against
    randezvous-qa -- the same project firebase_init and the seeded fixtures use. Never
    `start:prod`: web tests must not touch the prod Firebase project."""
    return "start", quest_test_data.WEB_PORT

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', int(port))) == 0

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Required environment variable '{name}' is not set. See .env.example.")
    return value

@pytest.fixture(scope="session")
def appium_server():
    if is_port_in_use(APPIUM_PORT):
        print(f"Port {APPIUM_PORT} in use. Cleaning up...")
        pids = subprocess.run(
            ["lsof", "-ti", f":{APPIUM_PORT}"],
            capture_output=True, text=True,
        ).stdout.split()
        if pids:
            subprocess.run(["kill", "-9", *pids])
        time.sleep(2)

    log_dir = os.path.join(os.path.dirname(__file__), "RandezVousUITests/Tests/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_fd = open(os.path.join(log_dir, "appium_server.log"), "w")

    appium_env = os.environ.copy()
    # The UiAutomator2 driver needs ANDROID_HOME/ANDROID_SDK_ROOT set on the Appium
    # *server* process itself -- adb being on PATH isn't enough. Default to Android
    # Studio's standard macOS install location so android_chrome_driver works without
    # every machine needing its own shell profile edit.
    if "ANDROID_HOME" not in appium_env and "ANDROID_SDK_ROOT" not in appium_env:
        default_sdk = os.path.expanduser("~/Library/Android/sdk")
        if os.path.isdir(default_sdk):
            appium_env["ANDROID_HOME"] = default_sdk
            appium_env["ANDROID_SDK_ROOT"] = default_sdk

    process = subprocess.Popen(
        # --allow-insecure uiautomator2:chromedriver_autodownload: chromedriver
        # auto-download is an "insecure feature" Appium disables by default -- without
        # this flag, the appium:chromedriverAutodownload capability (android_chrome_driver)
        # is silently ignored and Chrome sessions fail with "No Chromedriver found".
        # Appium 3.x requires the driver name (or '*') prefix -- the bare feature name
        # is rejected at startup ("must include ... automation name or the '*' wildcard").
        ["appium", "--port", APPIUM_PORT, "--log-level", "info",
         "--allow-insecure", "uiautomator2:chromedriver_autodownload"],
        stdout=log_fd,
        stderr=log_fd,
        preexec_fn=os.setsid,
        env=appium_env,
    )

    time.sleep(5)
    if process.poll() is not None:
        raise RuntimeError("Appium failed to start! Check Tests/logs/appium_server.log")

    yield process

    try:
        os.killpg(os.getpgid(process.pid), 9)
    except ProcessLookupError:
        pass
    finally:
        log_fd.close()


@pytest.fixture(scope="session")
def seed_simulator_photos(request):
    """Ensures the simulator's Photos library has at least one image, once
    per session. complete_photo_activity()'s picker step depends on a real
    photo existing -- previously it relied on whatever screenshots happened
    to already be in the camera roll on someone's machine. simctl addmedia
    is idempotent to call repeatedly (just adds another photo), so this is
    safe to run every session regardless of what's already there."""
    target_udid = request.config.getoption("--udid")
    sample_photo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "sample_photo.png")
    subprocess.run(
        ["xcrun", "simctl", "addmedia", target_udid, sample_photo],
        capture_output=True, text=True,
    )
    yield


def _build_options(bundle_id, udid, no_reset=False, is_headless=False):
    options = AppiumOptions()
    options.set_capability("platformName", "iOS")
    options.set_capability("appium:automationName", "XCUITest")
    options.set_capability("appium:deviceName", DEVICE_NAME)
    options.set_capability("appium:platformVersion", PLATFORM_VERSION)
    options.set_capability("appium:bundleId", bundle_id)
    options.set_capability("appium:noReset", no_reset)

    if udid and udid.lower() != "booted":
        options.set_capability("appium:udid", udid)

    options.set_capability("appium:forceAppLaunch", True)
    options.set_capability("appium:shouldTerminateApp", True)
    options.set_capability("appium:useNewWDA", False)
    options.set_capability("appium:showXcodeLog", True)
    options.set_capability("appium:resetKeychain", True)
    options.set_capability("appium:autoAcceptAlerts", True)
    options.set_capability("appium:isHeadless", is_headless)
    options.set_capability("appium:launchTimeout", 90000)
    options.set_capability("appium:wdaLaunchTimeout", 90000)
    options.set_capability("appium:appPushTimeout", 60000)
    options.set_capability("appium:waitForIdleTimeout", 500)

    if APP_CHECK_DEBUG_TOKEN:
        # Pins App Check's debug provider to a token pre-registered in Firebase Console.
        options.set_capability("appium:processArguments", {
            "env": {"FIRAAppCheckDebugToken": APP_CHECK_DEBUG_TOKEN}
        })

    return options


# Lines worth surfacing straight into the test's own captured output --
# network-level evidence for auth/App Check failures (status codes, the
# request URL, and any server error body) without having to go dig through
# the saved log file by hand.
_NETWORK_LOG_PATTERN = re.compile(
    r"CFNetwork|cloudfunctions|\.run\.app|firebaseappcheck|googleapis\.com|"
    r"AppCheck|Unauthenticated|Must be signed in|status \d{3}|response_status=\d+",
    re.IGNORECASE,
)


@pytest.fixture
def ios_device_log(request):
    """Pulls the simulator's console log (os_log) covering an iOS test's
    duration, filtered to the RandezVous process -- this is where CFNetwork
    request/response status lines live, useful for telling an App Check
    rejection apart from a Cloud Function's own auth check (both surface as
    the same generic "Unauthenticated" error client-side -- see memory:
    project_qa_unauthenticated_join).

    Uses `log show --last <Ns>` *after* the test finishes rather than a live
    `log stream` -- streaming proved unreliable (attached too late or not at
    all); `--last` reads back from the persisted log and has been verified
    to reliably return matching entries. `--start <timestamp>` was tried
    first and silently returned zero rows because `log show` interprets
    --start as local time -- a UTC-computed timestamp pointed hours off.

    Saved regardless of pass/fail to Tests/logs/device_console/<test_name>.log;
    network-relevant lines are also echoed into this test's own captured
    output so they show up directly in a PyCharm/CLI run without opening a
    separate file."""
    target_udid = request.config.getoption("--udid")
    start = time.time()

    yield

    elapsed_seconds = int(time.time() - start) + 5  # small buffer for log-write lag
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests", "logs", "device_console")
    os.makedirs(log_dir, exist_ok=True)
    safe_name = re.sub(r"[^\w.-]", "_", request.node.name)
    log_path = os.path.join(log_dir, f"{safe_name}.log")

    result = subprocess.run(
        ["xcrun", "simctl", "spawn", target_udid, "log", "show",
         "--debug", "--info",  # "log show" (unlike "log stream") takes these as bare flags, not --level
         "--predicate", 'process == "RandezVous"',
         "--style", "compact",
         "--last", f"{elapsed_seconds}s"],
        capture_output=True, text=True,
    )
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    network_lines = [line for line in result.stdout.splitlines() if _NETWORK_LOG_PATTERN.search(line)]

    print(f"\n📱 Device console log saved to: {log_path}")
    if network_lines:
        print("📡 Network-relevant lines from this test:")
        for line in network_lines:
            print(f"    {line}")
    else:
        print("📡 No network-relevant lines found in this test's window.")


@pytest.fixture
def rv_driver(request, appium_server, ios_device_log, seed_simulator_photos):
    target_udid = request.config.getoption("--udid")
    target_headless = request.config.getoption("--headless")

    # Simulated location persists on the simulator after a test ends. The
    # out-of-range location tests leave it far from every quest, and the next
    # test then fails at Quests-tab navigation -- so start each test clean.
    subprocess.run(["xcrun", "simctl", "location", target_udid, "clear"], capture_output=True)
    time.sleep(3)  # locationd needs a moment to apply the clear before the app launches

    # Pass the extracted UDID into your options builder
    driver = appium_webdriver.Remote(
        APPIUM_SERVER_URL,
        options=_build_options(RV_BUNDLE_ID, udid=target_udid, is_headless=target_headless)
    )

    yield driver
    try:
        driver.quit()
    except InvalidSessionIdException:
        print("\n⚠️ Note: Appium session was already terminated before driver.quit() was called.")
    except Exception as e:
        print(f"\n⚠️ Ignored driver teardown error: {e}")


def _build_desktop_driver(browser, headless):
    if browser == "safari":
        if headless:
            raise RuntimeError("Safari has no headless mode -- use --browser=chrome or firefox with --headless.")
        return webdriver.Safari()
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            # maximize_window() has no real screen to expand to headless, so
            # it leaves Chrome at its small default viewport (~800x600),
            # which triggers a different responsive layout than every other
            # mode runs against -- pin a real desktop size instead.
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        return webdriver.Chrome(options=options)
    if browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        return webdriver.Firefox(options=options)
    raise ValueError(f"Unknown browser: {browser}")


# rvsite's detectPlatform() (src/utils/platformUtils.js) reads navigator.userAgent,
# which Selenium can only override on Chrome -- Safari/Firefox don't expose a
# capability for it. Android is used (not iOS) because QuestOnboarding's
# AppActionCard puts the fallback URL we test directly in the "Open in App"
# link's href only on Android; iOS uses the raw custom-scheme deep link there
# instead and only consults the fallback URL inside a blur-timeout callback.
MOBILE_ANDROID_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
)


@pytest.fixture
def mobile_chrome_driver(request):
    """Chrome pinned to a mobile user-agent, so rvsite treats it as a phone
    browser (QuestOnboarding's AppActionCard) instead of desktop. Unlike
    desktop_safari_driver, doesn't wait for a login form on load -- tests
    using this fixture navigate straight to a quest URL, signed in or not."""
    headless = request.config.getoption("--headless")
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-agent={MOBILE_ANDROID_USER_AGENT}")
    options.add_argument("--window-size=430,932")
    if headless:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(quest_test_data.BASE_URL)
        wait = WebDriverWait(driver, 10)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")

        yield driver
    finally:
        _quit_driver_safely(driver)


@pytest.fixture
def desktop_safari_driver(request):
    """Launches the desktop browser selected via --browser (default: safari).
    Selenium Manager auto-provisions chromedriver/geckodriver -- Chrome or
    Firefox just need to be installed."""
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    safari_pids_before = _safari_automation_pids() if browser == "safari" else set()
    driver = _build_desktop_driver(browser, headless)
    # The Safari process this session just started (diffed against what already existed).
    safari_session_pids = (_safari_automation_pids() - safari_pids_before) if browser == "safari" else set()
    try:
        if headless:
            # maximize_window() has no real screen to expand to headless and can
            # override the --window-size startup arg with something tiny --
            # the fixed size set at launch is already what we want.
            driver.set_window_size(1920, 1080)
        else:
            driver.maximize_window()

        # 2. Perform the initial navigation
        _, web_port = _web_target(request)
        print(f"\nNavigating to http://localhost:{web_port}")
        driver.get(f"http://localhost:{web_port}")

        # 3. Wait for the base HTML to load
        wait = WebDriverWait(driver, 10)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        driver.refresh()

        # 4. Wait for React to hydrate. The root route is the marketing landing page (its only
        #    email input is a hidden "Work Email" lead field), so a visible header "Login" link or a
        #    visible email input (when a test lands on /login) is the hydration signal, not the
        #    first email input in the DOM.
        wait_for_react = WebDriverWait(driver, 30)
        print("Waiting for React to hydrate...")
        wait_for_react.until(lambda d: any(
            e.is_displayed() for e in d.find_elements(
                By.XPATH, "//a[normalize-space()='Login'] | //input[@type='email']")))

        # 5. Hand the ready-to-use driver over to the test
        yield driver

    finally:
        # Runs even if setup/hydration raised before the yield -- otherwise the browser
        # (and its tabs) leaked, which is how Safari instances piled up.
        _quit_driver_safely(driver)
        if safari_session_pids:
            _end_safari_automation(safari_session_pids)
            print(f"Safari automation processes left after teardown: {len(_safari_automation_pids())}")

@pytest.fixture
def rv_driver_no_reset(appium_server, ios_device_log, seed_simulator_photos):
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=_build_options(RV_BUNDLE_ID, no_reset=True))
    yield driver
    driver.quit()


@pytest.fixture
def safari_driver(request, appium_server):
    target_udid = request.config.getoption("--udid")
    target_headless = request.config.getoption("--headless")

    # appium_webdriver.Remote (not plain selenium.webdriver.Remote) -- hybrid/webview
    # interaction needs the .contexts / switch_to.context() extensions it adds; see
    # BaseHelper.switch_to_webview.
    driver = appium_webdriver.Remote(
        APPIUM_SERVER_URL,
        options=_build_options(SAFARI_BUNDLE_ID, target_udid, is_headless=target_headless)
    )

    yield driver

    try:
        driver.quit()
    except Exception as e:
        print(f"\n Ignored driver teardown error: {e}")


def _adb_path():
    """adb from PATH if present, else the Android SDK's platform-tools (the standard
    macOS location, or ANDROID_HOME/ANDROID_SDK_ROOT) -- so a fresh clone that ran
    setup.sh works without editing a shell profile, same as appium_server's
    ANDROID_HOME default."""
    on_path = shutil.which("adb")
    if on_path:
        return on_path
    for root in (os.environ.get("ANDROID_HOME"), os.environ.get("ANDROID_SDK_ROOT"),
                 os.path.expanduser("~/Library/Android/sdk")):
        candidate = os.path.join(root, "platform-tools", "adb") if root else None
        if candidate and os.path.isfile(candidate):
            return candidate
    return "adb"


def _get_android_serial():
    """Resolves which adb-visible emulator/device to target. ANDROID_UDID pins a specific
    one; otherwise falls back to whichever single device `adb devices` reports."""
    env_serial = os.getenv("ANDROID_UDID")
    if env_serial:
        return env_serial

    try:
        output = subprocess.run([_adb_path(), "devices"], capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        raise RuntimeError(
            "adb not found -- run ./setup.sh to install the Android SDK (platform-tools), or "
            "install it via Android Studio and set ANDROID_HOME."
        )

    serials = [
        line.split()[0] for line in output.strip().splitlines()[1:]
        if line.strip().endswith("device")
    ]
    if not serials:
        raise RuntimeError(
            "No Android emulator/device detected by adb. Start an AVD from Android "
            "Studio's Device Manager (or `emulator -avd <name>`) before running Android "
            "web tests."
        )
    if len(serials) > 1:
        raise RuntimeError(
            f"Multiple adb devices detected ({', '.join(serials)}) -- set ANDROID_UDID "
            "in .env to pick one."
        )
    return serials[0]


def _adb_reverse_web_ports(serial, remove=False):
    """Android emulators treat 'localhost' as themselves, not the host machine -- forward
    the emulator's loopback ports to the host's Vite/backend servers so BASE_URL
    (quest_test_data.BASE_URL) resolves the same as every other web
    driver."""
    if remove:
        subprocess.run([_adb_path(), "-s", serial, "reverse", "--remove-all"], capture_output=True)
        return
    for port in (quest_test_data.BACKEND_PORT, quest_test_data.WEB_PORT):
        subprocess.run([_adb_path(), "-s", serial, "reverse", f"tcp:{port}", f"tcp:{port}"], check=True)


def _build_android_chrome_options(serial):
    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("appium:automationName", "UiAutomator2")
    options.set_capability("appium:deviceName", ANDROID_DEVICE_NAME)
    options.set_capability("appium:platformVersion", ANDROID_PLATFORM_VERSION)
    options.set_capability("appium:udid", serial)
    options.set_capability("browserName", "Chrome")
    # Auto-fetches the chromedriver build matching the emulator image's system Chrome --
    # avoids hand-pinning a chromedriver version per AVD.
    options.set_capability("appium:chromedriverAutodownload", True)
    options.set_capability("appium:newCommandTimeout", 120)
    return options


@pytest.fixture
def android_chrome_driver(appium_server):
    """Real mobile Chrome on an Android emulator/device via Appium's UiAutomator2 driver --
    the Android counterpart to safari_driver. Unlike mobile_chrome_driver's user-agent
    trick on desktop Chrome, this is an actual Android browser, so it exercises real
    intent-link resolution for QuestOnboarding's "Open in App" behavior. RV's TWA
    (com.randezvous.RandezVous, live on Google Play -- see
    rvsite/public/.well-known/assetlinks.json) could later be driven directly by swapping
    the browserName capability for appPackage/appActivity.

    appium_webdriver.Remote (not plain selenium.webdriver.Remote) -- hybrid/webview
    interaction needs the .contexts / switch_to.context() extensions it adds; see
    BaseHelper.switch_to_webview.
    """
    serial = _get_android_serial()
    _adb_reverse_web_ports(serial)

    driver = appium_webdriver.Remote(
        APPIUM_SERVER_URL,
        options=_build_android_chrome_options(serial)
    )

    yield driver

    try:
        driver.quit()
    except Exception as e:
        print(f"\n Ignored driver teardown error: {e}")
    _adb_reverse_web_ports(serial, remove=True)


@pytest.fixture(scope="session", autouse=True)
def firebase_init():
    """Initializes Firebase using the verified absolute path. Always points
    at randezvous-qa (service-account-key-qa.json, matching rvsite's own
    QA key naming) -- prod is never used by this suite."""
    key_filename = "service-account-key-qa.json"

    project_root = Path(__file__).parent.parent.resolve()
    key_path = project_root / "private" / key_filename

    print(f"Checking key at absolute path: {key_path.resolve()}")
    if not key_path.exists():
        pytest.exit(
            f"ABSOLUTE PATH FAIL: \nTried: {key_path.resolve()}"
        )

    if not firebase_admin._apps:
        cred = credentials.Certificate(str(key_path))
        firebase_admin.initialize_app(cred)

@pytest.fixture(autouse=True)
def setup_teardown(request):
    """SETUP: Runs before every test """
    marker = request.node.get_closest_marker("cleanup")
    if marker:
        cleanup_type = marker.kwargs.get("type")
        identifier = marker.kwargs.get("value")
        score = marker.kwargs.get("score")

        if cleanup_type == "username":
            cleanup_user_data(target_username = identifier, target_score = score)
        elif cleanup_type == "email":
            cleanup_user_data(target_email = identifier, target_score = score)

html_results = []

# Global storage to aggregate logs, statuses, and steps across ALL test phases
_compiled_test_results = {}

_DRIVER_FIXTURE_NAMES = (
    "rv_driver",
    "rv_driver_no_reset",
    "safari_driver",
    "desktop_safari_driver",
    "mobile_chrome_driver",
    "android_chrome_driver",
    "driver",
)


def _get_active_driver(item):
    for fixture_name in _DRIVER_FIXTURE_NAMES:
        driver = item.funcargs.get(fixture_name)
        if driver:
            return driver
    return None


def _platform_for_nodeid(nodeid):
    if "/tests/ios/" in nodeid or "\\tests\\ios\\" in nodeid:
        return "iOS"
    if "/tests/web/" in nodeid or "\\tests\\web\\" in nodeid:
        return "Web"
    return "Other"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Captures test results, aggregated logs, and screenshots across all phases"""
    outcome = yield
    report = outcome.get_result()

    nodeid = item.nodeid
    if nodeid not in _compiled_test_results:
        _compiled_test_results[nodeid] = {
            "name": item.name,
            "platform": _platform_for_nodeid(nodeid),
            "status": "PASSED",
            "logs": "",
            "error_msg": "",
            "failure_line": "",
            "screenshot_b64": "",
            "screenshot_label": "End State",
            "duration": 0.0
        }

    test_entry = _compiled_test_results[nodeid]
    test_entry["duration"] += report.duration

    if report.capstdout:
        phase_header = f"--- [{report.when.upper()} PHASE] ---\n"
        test_entry["logs"] += phase_header + report.capstdout.strip() + "\n\n"

    if report.skipped and test_entry["status"] == "PASSED":
        test_entry["status"] = "SKIPPED"

    if report.failed:
        test_entry["status"] = "FAILED"

        if call.excinfo:
            test_entry["error_msg"] = str(call.excinfo.value)
            try:
                # Walk backwards through the stacktrace to find the first frame in our own code
                target_frame = None
                for frame in reversed(call.excinfo.traceback):
                    frame_path = str(frame.path)

                    # Ignore standard library and virtual environment folders
                    if "site-packages" not in frame_path and ".venv" not in frame_path and "lib/python" not in frame_path:
                        target_frame = frame
                        break

                # Fallback to the absolute last frame if everything was library code
                if not target_frame:
                    target_frame = call.excinfo.traceback[-1]

                file_name = os.path.basename(str(target_frame.path))
                line_number = target_frame.lineno + 1
                offending_code = str(target_frame.statement).strip()

                test_entry["failure_line"] = f"File: {file_name} | Line: {line_number}\nCode: {offending_code}"
            except Exception:
                test_entry["failure_line"] = "Could not parse the exact line of failure."

    # Capture a screenshot of the app/page state at the end of the "call" phase,
    # regardless of outcome, so passing runs are visually verifiable too, not
    # just failures. This runs before teardown fixtures tear the driver down.
    if report.when == "call":
        driver = _get_active_driver(item)
        if driver:
            try:
                test_entry["screenshot_b64"] = driver.get_screenshot_as_base64()
                test_entry["screenshot_label"] = "State At Failure" if report.failed else "End State"
            except Exception as e:
                print(f"Failed to capture end-state screenshot: {e}")


def _git(*args):
    try:
        return subprocess.check_output(
            ["git", *args], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return ""


def _prune_old_reports(reports_dir, keep_count):
    """Reports embed screenshots as base64, so each file can run 1-2MB+.
    Keep only the most recent `keep_count` reports; delete the rest."""
    reports = sorted(
        Path(reports_dir).glob("Execution_Report_*.html"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for stale in reports[keep_count:]:
        try:
            stale.unlink()
        except OSError:
            pass


def pytest_sessionfinish(session, exitstatus):
    """Compiles results and saves the dashboard into a dedicated reports directory"""
    reports_dir = os.path.join(session.config.rootdir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

    report_path = os.path.join(reports_dir, f"Execution_Report_{file_timestamp}.html")

    git_branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    git_commit = _git("rev-parse", "--short", "HEAD")

    STATUS_STYLE = {
        "PASSED": {"label": "PASSED", "color": "#1a7f37", "bg": "#e9f7ee", "border": "#1a7f37"},
        "FAILED": {"label": "FAILED", "color": "#c92a2a", "bg": "#fdecec", "border": "#c92a2a"},
        "SKIPPED": {"label": "SKIPPED", "color": "#8a6d00", "bg": "#fdf7e3", "border": "#d4a800"},
    }

    total_passed = sum(1 for d in _compiled_test_results.values() if d["status"] == "PASSED")
    total_failed = sum(1 for d in _compiled_test_results.values() if d["status"] == "FAILED")
    total_skipped = sum(1 for d in _compiled_test_results.values() if d["status"] == "SKIPPED")
    total_tests = len(_compiled_test_results)
    total_duration = sum(d["duration"] for d in _compiled_test_results.values())
    pass_rate = (total_passed / total_tests * 100) if total_tests else 0.0
    all_green = total_failed == 0 and total_skipped == 0

    # Failed first, then skipped, then passed; alphabetical within each group.
    status_order = {"FAILED": 0, "SKIPPED": 1, "PASSED": 2}
    sorted_results = sorted(
        _compiled_test_results.items(),
        key=lambda kv: (status_order[kv[1]["status"]], kv[1]["name"])
    )

    def _slug(nodeid):
        return "test-" + "".join(c if c.isalnum() else "-" for c in nodeid)

    failed_jump_links = "".join(
        f'<a class="jump-link" href="#{_slug(nodeid)}">{data["name"]}</a>'
        for nodeid, data in sorted_results if data["status"] == "FAILED"
    )

    html_cards = []
    for nodeid, data in sorted_results:
        style = STATUS_STYLE[data["status"]]
        anchor_id = _slug(nodeid)
        is_open = "open" if (data["status"] != "PASSED" or all_green) else ""

        error_block = ""
        if data["status"] == "FAILED":
            error_block = f"""
            <h4 class="section-label error">Error Message</h4>
            <pre class="code-block error-block">{data['error_msg']}</pre>

            <h4 class="section-label warn">Last Line Executed Before Crash</h4>
            <pre class="code-block warn-block">{data['failure_line']}</pre>
            """

        screenshot_block = ""
        if data["screenshot_b64"]:
            screenshot_block = f"""
            <h4 class="section-label">{data['screenshot_label']} Screenshot</h4>
            <img class="screenshot lightbox-trigger" style="border-color:{style['border']};" src="data:image/png;base64,{data['screenshot_b64']}">
            <div class="screenshot-hint">Click to enlarge</div>
            """
        else:
            screenshot_block = '<div class="no-screenshot">No screenshot captured for this test.</div>'

        card = f"""
        <details class="test-card" id="{anchor_id}" data-status="{data['status']}" data-name="{data['name'].lower()}" {is_open}>
            <summary style="border-left-color:{style['border']};">
                <span class="status-pill" style="color:{style['color']}; background:{style['bg']};">{style['label']}</span>
                <span class="platform-pill">{data['platform']}</span>
                <span class="test-name">{data['name']}</span>
                <span class="duration-pill">{data['duration']:.2f}s</span>
            </summary>
            <div class="test-body">
                {screenshot_block}
                {error_block}
                <h4 class="section-label">Console Output</h4>
                <pre class="code-block log-block">{data['logs'].strip() or "No print statements caught in this execution."}</pre>
            </div>
        </details>
        """
        html_cards.append(card)

    meta_line = f"Branch <code>{git_branch}</code> @ <code>{git_commit}</code>" if git_branch else ""

    html_layout = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Automation Execution Report — {timestamp}</title>
        <style>
            :root {{
                --bg: #f4f6f9;
                --card-bg: #ffffff;
                --text: #1c2530;
                --text-muted: #5b6b7c;
                --border: #e3e8ee;
                --accent: #2c3e50;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
                background: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 32px 16px;
            }}
            .container {{
                max-width: 1100px;
                margin: 0 auto;
                background: var(--card-bg);
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.06);
                padding: 28px 32px;
            }}
            h1 {{
                font-size: 20px;
                margin: 0 0 4px 0;
                color: var(--accent);
            }}
            .run-meta {{
                font-size: 13px;
                color: var(--text-muted);
                margin-bottom: 20px;
            }}
            .stat-bar {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-bottom: 20px;
            }}
            .stat {{
                flex: 1;
                min-width: 110px;
                background: #f8f9fb;
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 10px 14px;
            }}
            .stat .value {{ font-size: 20px; font-weight: 600; }}
            .stat .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); }}
            .stat.pass .value {{ color: #1a7f37; }}
            .stat.fail .value {{ color: #c92a2a; }}
            .stat.skip .value {{ color: #8a6d00; }}

            .toolbar {{
                display: flex;
                align-items: center;
                gap: 8px;
                margin: 4px 0 18px 0;
                flex-wrap: wrap;
            }}
            .filter-btn {{
                border: 1px solid var(--border);
                background: #fff;
                color: var(--text);
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                cursor: pointer;
            }}
            .filter-btn.active {{
                background: var(--accent);
                color: #fff;
                border-color: var(--accent);
            }}
            .search-input {{
                border: 1px solid var(--border);
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                flex: 1;
                min-width: 160px;
                max-width: 280px;
            }}

            .jump-panel {{
                background: #fdecec;
                border: 1px solid #f3c9c9;
                border-radius: 8px;
                padding: 10px 14px;
                margin-bottom: 18px;
                font-size: 13px;
            }}
            .jump-panel .jump-title {{ font-weight: 600; color: #c92a2a; margin-bottom: 6px; }}
            .jump-link {{
                display: inline-block;
                color: #c92a2a;
                text-decoration: none;
                background: #fff;
                border: 1px solid #f3c9c9;
                border-radius: 5px;
                padding: 3px 8px;
                margin: 2px 4px 2px 0;
                font-size: 12px;
            }}
            .jump-link:hover {{ text-decoration: underline; }}

            .test-card {{
                border: 1px solid var(--border);
                border-radius: 8px;
                margin-bottom: 10px;
                overflow: hidden;
            }}
            .test-card > summary {{
                list-style: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 14px;
                border-left: 4px solid;
                background: #fafbfc;
            }}
            .test-card > summary::-webkit-details-marker {{ display: none; }}
            .status-pill {{
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.03em;
                padding: 3px 8px;
                border-radius: 10px;
            }}
            .platform-pill {{
                font-size: 11px;
                color: var(--text-muted);
                border: 1px solid var(--border);
                border-radius: 10px;
                padding: 2px 8px;
            }}
            .test-name {{ font-size: 14px; font-weight: 600; flex: 1; }}
            .duration-pill {{ font-size: 12px; color: var(--text-muted); }}

            .test-body {{ padding: 16px 18px; }}
            .section-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin: 14px 0 6px 0; }}
            .section-label.error {{ color: #c92a2a; }}
            .section-label.warn {{ color: #8a6d00; }}
            .code-block {{
                font-family: "SF Mono", "Courier New", monospace;
                font-size: 12.5px;
                line-height: 1.5;
                padding: 12px 14px;
                border-radius: 6px;
                overflow-x: auto;
                white-space: pre-wrap;
                word-break: break-word;
                margin: 0;
            }}
            .log-block {{ background: #1e2228; color: #e6e6e6; }}
            .error-block {{ background: #fdecec; color: #8a1f1f; border-left: 3px solid #c92a2a; }}
            .warn-block {{ background: #fdf7e3; color: #5c4600; border-left: 3px solid #d4a800; font-weight: 600; }}

            .screenshot {{
                max-width: 320px;
                border: 2px solid;
                border-radius: 6px;
                display: block;
                cursor: zoom-in;
            }}
            .screenshot-hint {{ font-size: 11px; color: var(--text-muted); margin-top: 4px; }}
            .no-screenshot {{ font-size: 12px; color: var(--text-muted); font-style: italic; }}

            .test-card[data-status="PASSED"] > summary {{ border-left-color: #1a7f37; }}
            .test-card[data-status="FAILED"] > summary {{ border-left-color: #c92a2a; }}
            .test-card[data-status="SKIPPED"] > summary {{ border-left-color: #d4a800; }}

            .test-card.is-hidden {{ display: none; }}

            .lightbox-overlay {{
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(10, 14, 20, 0.88);
                z-index: 1000;
                align-items: center;
                justify-content: center;
                padding: 40px;
                cursor: zoom-out;
            }}
            .lightbox-overlay.is-visible {{ display: flex; }}
            .lightbox-overlay img {{
                max-width: 100%;
                max-height: 100%;
                border-radius: 6px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.4);
            }}
            .lightbox-close {{
                position: fixed;
                top: 20px;
                right: 28px;
                color: #fff;
                font-size: 28px;
                line-height: 1;
                cursor: pointer;
                opacity: 0.85;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Automation Run Summary</h1>
            <div class="run-meta">{timestamp}{" &middot; " + meta_line if meta_line else ""}</div>

            <div class="stat-bar">
                <div class="stat"><div class="value">{total_tests}</div><div class="label">Total</div></div>
                <div class="stat pass"><div class="value">{total_passed}</div><div class="label">Passed</div></div>
                <div class="stat fail"><div class="value">{total_failed}</div><div class="label">Failed</div></div>
                <div class="stat skip"><div class="value">{total_skipped}</div><div class="label">Skipped</div></div>
                <div class="stat"><div class="value">{pass_rate:.0f}%</div><div class="label">Pass Rate</div></div>
                <div class="stat"><div class="value">{total_duration:.1f}s</div><div class="label">Duration</div></div>
            </div>

            {f'<div class="jump-panel"><div class="jump-title">Failed Tests</div>{failed_jump_links}</div>' if total_failed else ''}

            <div class="toolbar">
                <button class="filter-btn active" data-filter="ALL">All</button>
                <button class="filter-btn" data-filter="FAILED">Failed</button>
                <button class="filter-btn" data-filter="PASSED">Passed</button>
                <button class="filter-btn" data-filter="SKIPPED">Skipped</button>
                <input class="search-input" type="text" placeholder="Filter by test name...">
            </div>

            {''.join(html_cards)}
        </div>

        <div class="lightbox-overlay" id="lightbox">
            <span class="lightbox-close">&times;</span>
            <img id="lightbox-img" src="" alt="Full resolution screenshot">
        </div>

        <script>
            (function() {{
                var cards = Array.prototype.slice.call(document.querySelectorAll('.test-card'));
                var buttons = Array.prototype.slice.call(document.querySelectorAll('.filter-btn'));
                var search = document.querySelector('.search-input');
                var activeFilter = 'ALL';

                function applyFilters() {{
                    var term = search.value.trim().toLowerCase();
                    cards.forEach(function(card) {{
                        var matchesStatus = activeFilter === 'ALL' || card.dataset.status === activeFilter;
                        var matchesSearch = !term || card.dataset.name.indexOf(term) !== -1;
                        card.classList.toggle('is-hidden', !(matchesStatus && matchesSearch));
                    }});
                }}

                buttons.forEach(function(btn) {{
                    btn.addEventListener('click', function() {{
                        buttons.forEach(function(b) {{ b.classList.remove('active'); }});
                        btn.classList.add('active');
                        activeFilter = btn.dataset.filter;
                        applyFilters();
                    }});
                }});

                search.addEventListener('input', applyFilters);

                // Lightbox: click a screenshot thumbnail to view it full-size in-page.
                // (A data: URI cannot be opened via target="_blank" -- browsers block
                // top-level navigation to data: URLs, so this stays in-page instead.)
                var lightbox = document.getElementById('lightbox');
                var lightboxImg = document.getElementById('lightbox-img');

                document.querySelectorAll('.lightbox-trigger').forEach(function(img) {{
                    img.addEventListener('click', function(e) {{
                        e.preventDefault();
                        e.stopPropagation();
                        lightboxImg.src = img.src;
                        lightbox.classList.add('is-visible');
                    }});
                }});

                lightbox.addEventListener('click', function() {{
                    lightbox.classList.remove('is-visible');
                    lightboxImg.src = '';
                }});

                document.addEventListener('keydown', function(e) {{
                    if (e.key === 'Escape') {{
                        lightbox.classList.remove('is-visible');
                        lightboxImg.src = '';
                    }}
                }});
            }})();
        </script>
    </body>
    </html>
    """

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_layout)

    _prune_old_reports(reports_dir, REPORT_RETENTION_COUNT)

    print(f"\nDashboard Summary Generated At: {report_path}")


@pytest.fixture(scope="session")
def web_servers(request):
    """Starts the rvsite backend + Vite dev server once per session. Output
    goes to a log file, not an unread PIPE (that used to fill up and block
    the dev server mid-request)."""
    npm_script, web_port = _web_target(request)

    if request.config.getoption("--browser") == "safari":
        _sweep_leaked_safari_windows()

    print("\n--- [Web Test] Cleaning up Node processes on ports 3000, 5173, 5174 (5173 = stale prod-mode servers) ---")
    subprocess.run(["npx", "kill-port", "3000", "5173", "5174"], capture_output=True)

    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests", "logs")
    os.makedirs(log_dir, exist_ok=True)
    web_log_path = os.path.join(log_dir, "web_servers.log")
    web_log_fd = open(web_log_path, "w")

    print(f"--- [Web Test] Starting backend and React servers via npm run {npm_script} (logs: {web_log_path}) ---")
    backend_process = subprocess.Popen(
        ["npm", "run", npm_script],
        cwd=WEB_APP_PATH,
        stdout=web_log_fd,
        stderr=subprocess.STDOUT,
    )

    def wait_until_up(url, timeout=45):
        start = time.time()
        while time.time() - start < timeout:
            try:
                if requests.get(url).status_code < 500:
                    return True
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(0.5)
        return False

    print("--- [Web Test] Waiting for backend on port 3000... ---")
    if not wait_until_up(f"{quest_test_data.BACKEND_URL}/api/user/profile"):
        backend_process.terminate()
        web_log_fd.close()
        raise RuntimeError(f"Backend failed to start on port 3000 within timeout. See {web_log_path}")

    print(f"--- [Web Test] Backend ready. Waiting for React frontend on port {web_port}... ---")
    if not wait_until_up(f"http://localhost:{web_port}"):
        backend_process.terminate()
        web_log_fd.close()
        raise RuntimeError(f"Vite frontend failed to start on port {web_port} within timeout. See {web_log_path}")

    # Best-effort warm-up: pull the index shell for the routes the tests hit
    # first so Vite's dev-time transform has a head start before test one.
    for path in ("/", "/login", "/find-quest"):
        try:
            requests.get(f"http://localhost:{web_port}{path}", timeout=10)
        except requests.exceptions.RequestException:
            pass

    print("--- [Web Test] Both servers are ready! ---\n")

    yield backend_process

    print("\n--- [Web Test] Teardown: Killing background servers ---")
    backend_process.terminate()
    backend_process.wait()
    web_log_fd.close()
    subprocess.run(["npx", "kill-port", "3000", "5173", "5174"], capture_output=True)
    if request.config.getoption("--browser") == "safari":
        _sweep_leaked_safari_windows()


@pytest.fixture(scope="function", autouse=True)
def restart_node_server_for_web(request):
    """Ensure the shared web servers are running for any test under Tests/web/."""
    test_path = str(request.node.fspath)
    if "/web/" not in test_path:
        yield
        return

    request.getfixturevalue("web_servers")
    yield


@pytest.fixture(scope="function", autouse=True)
def retry_web_login(request, monkeypatch):
    """Retries HomepageHelper.login() for web tests if sign-in gets stuck
    (raises TimeoutException), reloading the homepage before each retry.
    Wraps login() only for the test's duration -- the method itself is
    untouched."""
    test_path = str(request.node.fspath)
    if "/web/" not in test_path:
        yield
        return

    original_login = HomepageHelper.login
    _, web_port = _web_target(request)

    def login_with_retry(self, email, password, attempts=3):
        for attempt in range(1, attempts + 1):
            try:
                return original_login(self, email, password)
            except TimeoutException:
                if attempt == attempts:
                    raise
                print(f"Sign-in appears stuck (attempt {attempt}/{attempts}); reloading and retrying...")
                self.driver.get(f"http://localhost:{web_port}")

    monkeypatch.setattr(HomepageHelper, "login", login_with_retry)
    yield