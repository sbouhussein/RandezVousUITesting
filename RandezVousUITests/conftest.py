import datetime
import os
import re
import shutil
import signal
import socket
import subprocess
import time
from pathlib import Path

import firebase_admin
import pytest
import requests
from appium import webdriver as appium_webdriver
from appium.options.common import AppiumOptions
from dotenv import load_dotenv
from firebase_admin import credentials
from selenium import webdriver
from selenium.common import InvalidSessionIdException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from helpers.ios.device_helper import DEFAULT_SIM_LOCATION
from helpers.ios.firebase_cleanup_helper import cleanup_user_data
from helpers.web import quest_test_data
from helpers.web.homepage_helper import HomepageHelper

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
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests", "logs")


def pytest_addoption(parser):
    parser.addoption("--udid", action="store", default="booted", help="UDID of the iOS Simulator")
    parser.addoption("--headless", action="store_true", help="Run the simulator/browser in headless mode")
    parser.addoption("--browser", action="store", default="safari", choices=["safari", "chrome", "firefox"],
                      help="Desktop browser for web tests (Safari has no headless mode)")


def _quit_driver_safely(driver):
    """Closes every window, then quits. Each step is best-effort so one failure can't leave the
    browser open."""
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
    """driver.quit() leaves the session's `Safari --automation` process running, and the next
    session then fails with "already paired with a different session". Waits for `pids` to exit,
    then SIGTERMs, then SIGKILLs them."""
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
    """Kills Safari automation sessions orphaned by killed or crashed runs (which skip fixture
    teardown). The user's own Safari runs without --automation and is never touched."""
    subprocess.run(["pkill", "-x", "safaridriver"], capture_output=True)
    subprocess.run(["pkill", "-f", _SAFARI_AUTOMATION_PATTERN], capture_output=True)


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', int(port))) == 0


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

    os.makedirs(LOG_DIR, exist_ok=True)
    log_fd = open(os.path.join(LOG_DIR, "appium_server.log"), "w")

    appium_env = os.environ.copy()
    # UiAutomator2 needs ANDROID_HOME on the Appium server process itself (adb on PATH isn't
    # enough), so default it to Android Studio's standard macOS install location.
    if "ANDROID_HOME" not in appium_env and "ANDROID_SDK_ROOT" not in appium_env:
        default_sdk = os.path.expanduser("~/Library/Android/sdk")
        if os.path.isdir(default_sdk):
            appium_env["ANDROID_HOME"] = default_sdk
            appium_env["ANDROID_SDK_ROOT"] = default_sdk

    process = subprocess.Popen(
        # Without this, android_chrome_driver's chromedriverAutodownload capability is silently
        # ignored ("No Chromedriver found"). Appium 3 requires the "uiautomator2:" prefix.
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
    """Adds a photo to the simulator's library once per session, for complete_photo_activity()'s
    picker step."""
    target_udid = request.config.getoption("--udid")
    sample_photo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "sample_photo.png")
    subprocess.run(
        ["xcrun", "simctl", "addmedia", target_udid, sample_photo],
        capture_output=True, text=True,
    )
    yield


def _build_options(bundle_id, udid, no_reset=False, is_headless=False, show_quest_intro=False):
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

    # Skips the Quests onboarding overlay; must be "<false/>" since "NO" parses as a string.
    process_arguments = {"args": [] if show_quest_intro else ["-showQuestIntro", "<false/>"]}
    if APP_CHECK_DEBUG_TOKEN:
        # Debug token pre-registered in Firebase Console.
        process_arguments["env"] = {"FIRAAppCheckDebugToken": APP_CHECK_DEBUG_TOKEN}
    options.set_capability("appium:processArguments", process_arguments)

    return options


# Device log lines echoed into the test's output: evidence for auth/App Check failures.
_NETWORK_LOG_PATTERN = re.compile(
    r"CFNetwork|cloudfunctions|\.run\.app|firebaseappcheck|googleapis\.com|"
    r"AppCheck|Unauthenticated|Must be signed in|status \d{3}|response_status=\d+",
    re.IGNORECASE,
)


@pytest.fixture
def ios_device_log(request):
    """Saves the RandezVous process's simulator console log for the test's duration to
    Tests/logs/device_console/<test_name>.log and echoes the network-relevant lines. That's where
    an App Check rejection can be told apart from a Cloud Function's own auth check (both surface
    client-side as "Unauthenticated").

    Reads back with `log show --last` after the test: a live `log stream` attached unreliably, and
    `--start` is interpreted as local time."""
    target_udid = request.config.getoption("--udid")
    start = time.time()

    yield

    elapsed_seconds = int(time.time() - start) + 5  # small buffer for log-write lag
    log_dir = os.path.join(LOG_DIR, "device_console")
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

    # Pin, don't clear: no location fix makes the app raise an alert autoAcceptAlerts sends to Settings.
    lat, lon = DEFAULT_SIM_LOCATION
    subprocess.run(["xcrun", "simctl", "location", target_udid, "set", f"{lat},{lon}"], capture_output=True)
    # iOS 27 silently ignores a "location" grant but honors "location-always".
    for service in ("location", "location-always"):
        subprocess.run(["xcrun", "simctl", "privacy", target_udid, "grant", service, RV_BUNDLE_ID],
                       capture_output=True)
    time.sleep(3)  # locationd applies the location asynchronously

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
            # Headless has no screen to maximize to; pin a desktop size so the layout matches.
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


# rvsite's detectPlatform() reads navigator.userAgent, which only Chrome lets Selenium override.
# Android rather than iOS because only on Android does the "Open in App" href hold the fallback URL.
MOBILE_ANDROID_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
)


@pytest.fixture
def mobile_chrome_driver(request):
    """Chrome with an Android user-agent, so rvsite renders its phone layout. Doesn't wait for
    hydration like desktop_safari_driver: tests navigate straight to a quest URL."""
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
    """The desktop browser selected via --browser (default: safari), on rvsite's landing page."""
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
    safari_pids_before = _safari_automation_pids() if browser == "safari" else set()
    driver = _build_desktop_driver(browser, headless)
    safari_session_pids = (_safari_automation_pids() - safari_pids_before) if browser == "safari" else set()
    try:
        if headless:
            driver.set_window_size(1920, 1080)
        else:
            driver.maximize_window()

        print(f"\nNavigating to {quest_test_data.BASE_URL}")
        driver.get(quest_test_data.BASE_URL)

        wait = WebDriverWait(driver, 10)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        driver.refresh()

        # The landing page's only email input is a hidden lead field, so wait for a *visible*
        # "Login" link or email input as the hydration signal.
        wait_for_react = WebDriverWait(driver, 30)
        print("Waiting for React to hydrate...")
        wait_for_react.until(lambda d: any(
            e.is_displayed() for e in d.find_elements(
                By.XPATH, "//a[normalize-space()='Login'] | //input[@type='email']")))

        yield driver
    finally:
        _quit_driver_safely(driver)
        if safari_session_pids:
            _end_safari_automation(safari_session_pids)
            print(f"Safari automation processes left after teardown: {len(_safari_automation_pids())}")


@pytest.fixture
def rv_driver_no_reset(request, appium_server, ios_device_log, seed_simulator_photos):
    target_udid = request.config.getoption("--udid")
    driver = appium_webdriver.Remote(
        APPIUM_SERVER_URL,
        options=_build_options(RV_BUNDLE_ID, target_udid, no_reset=True)
    )
    yield driver
    driver.quit()


@pytest.fixture
def safari_driver(request, appium_server):
    target_udid = request.config.getoption("--udid")
    target_headless = request.config.getoption("--headless")

    # Appium's Remote, not Selenium's: BaseHelper.switch_to_webview needs .contexts.
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
    """adb from PATH, else from the Android SDK's platform-tools."""
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
    """Forwards the emulator's localhost ports to the host's dev servers, so BASE_URL works there."""
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
    options.set_capability("appium:chromedriverAutodownload", True)
    options.set_capability("appium:newCommandTimeout", 120)
    return options


@pytest.fixture
def android_chrome_driver(appium_server):
    """Real Chrome on an Android emulator/device, the Android counterpart to safari_driver. Unlike
    mobile_chrome_driver, it exercises real intent-link resolution."""
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
    """Initializes the Admin SDK against randezvous-qa. Prod is never used by this suite."""
    key_path = Path(__file__).parent.parent.resolve() / "private" / "service-account-key-qa.json"
    if not key_path.exists():
        pytest.exit(f"Firebase service account key not found at {key_path}")

    if not firebase_admin._apps:
        firebase_admin.initialize_app(credentials.Certificate(str(key_path)))


@pytest.fixture(autouse=True)
def setup_teardown(request):
    """Wipes test-user data named by the test's @pytest.mark.cleanup marker before it runs."""
    marker = request.node.get_closest_marker("cleanup")
    if marker:
        cleanup_type = marker.kwargs.get("type")
        identifier = marker.kwargs.get("value")
        score = marker.kwargs.get("score")

        if cleanup_type == "username":
            cleanup_user_data(target_username=identifier, target_score=score)
        elif cleanup_type == "email":
            cleanup_user_data(target_email=identifier, target_score=score)


# Per-test results aggregated across setup/call/teardown, for the HTML report.
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
    nodeid = nodeid.lower()
    if "tests/ios/" in nodeid:
        return "iOS"
    if "tests/web/" in nodeid:
        return "Web"
    return "Other"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Captures each test's result, output, and end-state screenshot for the HTML report."""
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
                # Innermost frame in our own code, skipping the stdlib and installed packages.
                target_frame = None
                for frame in reversed(call.excinfo.traceback):
                    frame_path = str(frame.path)
                    if "site-packages" not in frame_path and ".venv" not in frame_path and "lib/python" not in frame_path:
                        target_frame = frame
                        break

                if not target_frame:
                    target_frame = call.excinfo.traceback[-1]

                file_name = os.path.basename(str(target_frame.path))
                line_number = target_frame.lineno + 1
                offending_code = str(target_frame.statement).strip()

                test_entry["failure_line"] = f"File: {file_name} | Line: {line_number}\nCode: {offending_code}"
            except Exception:
                test_entry["failure_line"] = "Could not parse the exact line of failure."

    # Screenshot every test, pass or fail, before teardown quits the driver.
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
    """Keeps only the newest `keep_count` reports (each embeds screenshots, so they're large)."""
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
    """Writes the HTML execution report to reports/."""
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

                // In-page lightbox: browsers block top-level navigation to data: URLs.
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
    """Starts rvsite's backend and Vite dev server once per session via `npm start`, its QA
    target. Never `start:prod`: web tests must not touch the prod Firebase project. Output goes to
    a log file; an unread PIPE fills up and blocks the dev server."""
    web_port = quest_test_data.WEB_PORT

    if request.config.getoption("--browser") == "safari":
        _sweep_leaked_safari_windows()

    print("\n--- [Web Test] Cleaning up Node processes on ports 3000, 5173, 5174 (5173 = stale prod-mode servers) ---")
    subprocess.run(["npx", "kill-port", "3000", "5173", "5174"], capture_output=True)

    os.makedirs(LOG_DIR, exist_ok=True)
    web_log_path = os.path.join(LOG_DIR, "web_servers.log")
    web_log_fd = open(web_log_path, "w")

    print(f"--- [Web Test] Starting backend and React servers via npm start (logs: {web_log_path}) ---")
    backend_process = subprocess.Popen(
        ["npm", "start"],
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

    # Warm up Vite's transform for the routes tests hit first.
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


def _restart_web_backend():
    """Restarts only rvsite's backend (port 3000), which clears its in-memory caches (quest definitions live 10 minutes).
    The Vite frontend keeps running: restarting it repeatedly is what makes sign-in stall."""
    subprocess.run(["npx", "kill-port", "3000"], capture_output=True)
    log_fd = open(os.path.join(LOG_DIR, "web_servers.log"), "a")
    subprocess.Popen(["npm", "run", "dev:qa"], cwd=os.path.join(WEB_APP_PATH, "backend"),
                     stdout=log_fd, stderr=subprocess.STDOUT)
    url = f"{quest_test_data.BACKEND_URL}/api/user/profile"
    deadline = time.time() + 60
    while True:
        try:
            if requests.get(url).status_code < 500:
                return
        except requests.exceptions.ConnectionError:
            pass
        if time.time() > deadline:
            raise RuntimeError(f"The backend did not come back after a restart. See {LOG_DIR}/web_servers.log")
        time.sleep(0.5)


@pytest.fixture
def fresh_web_backend(web_servers):
    """For web tests that edit a QA quest (edited_quest / edited_activity): the session's rvsite backend caches quest
    definitions, so restart it before the test (to see the edit) and after (so the edited quest isn't served to later tests)."""
    _restart_web_backend()
    yield
    _restart_web_backend()


@pytest.fixture(scope="function", autouse=True)
def restart_node_server_for_web(request):
    """Ensures the shared web servers are running for any test under Tests/web/."""
    test_path = str(request.node.fspath)
    if "/web/" not in test_path:
        yield
        return

    request.getfixturevalue("web_servers")
    yield


@pytest.fixture(scope="function", autouse=True)
def retry_web_login(request, monkeypatch):
    """Retries HomepageHelper.login() for web tests on TimeoutException, reloading the homepage
    first."""
    test_path = str(request.node.fspath)
    if "/web/" not in test_path:
        yield
        return

    original_login = HomepageHelper.login

    def login_with_retry(self, email, password, attempts=3):
        for attempt in range(1, attempts + 1):
            try:
                return original_login(self, email, password)
            except TimeoutException:
                if attempt == attempts:
                    raise
                print(f"Sign-in appears stuck (attempt {attempt}/{attempts}); reloading and retrying...")
                self.driver.get(quest_test_data.BASE_URL)

    monkeypatch.setattr(HomepageHelper, "login", login_with_retry)
    yield