import datetime
import os
import time
import subprocess
import firebase_admin
import pytest
from dotenv import load_dotenv
from appium import webdriver
from appium.options.ios import XCUITestOptions
from firebase_admin import credentials
from pathlib import Path
from helpers.firebase_cleanup_helper import cleanup_user_data
import socket

load_dotenv(os.path.join(os.path.dirname(__file__), "../..", ".env"))

APPIUM_PORT = os.getenv("APPIUM_PORT", "4723")
APPIUM_SERVER_URL = f"http://127.0.0.1:{APPIUM_PORT}"
DEVICE_NAME = "iPhone 17 Pro"
PLATFORM_VERSION = "26.2"
UDID = "02702BB3-0AE0-4167-9651-39F68787A375"
RV_BUNDLE_ID = os.getenv("RV_BUNDLE_ID", "sbouhussein.github.io-rvsite.RandezVous")
SAFARI_BUNDLE_ID = os.getenv("SAFARI_BUNDLE_ID", "com.apple.mobilesafari")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', int(port))) == 0


@pytest.fixture(scope="session")
def appium_server():
    # 1. FORCE CLEANUP: If something is on 4723, kill it first
    if is_port_in_use(APPIUM_PORT):
        print(f"Port {APPIUM_PORT} in use. Cleaning up...")
        os.system(f"lsof -P | grep ':{APPIUM_PORT}' | awk '{{print $2}}' | xargs kill -9")
        time.sleep(2)

    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_fd = open(os.path.join(log_dir, "appium_server.log"), "w")

    # 2. START SERVER
    process = subprocess.Popen(
        ["appium", "--port", APPIUM_PORT, "--log-level", "info"],
        stdout=log_fd,
        stderr=log_fd,
        preexec_fn=os.setsid,
    )

    # 3. VERIFY: Wait and check if it crashed
    time.sleep(5)
    if process.poll() is not None:
        raise RuntimeError("Appium failed to start! Check Tests/logs/appium_server.log")

    yield process

    # 4. SAFER TEARDOWN
    try:
        os.killpg(os.getpgid(process.pid), 9)
    except ProcessLookupError:
        pass
    finally:
        log_fd.close()
def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Required environment variable '{name}' is not set. See .env.example.")
    return value


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', int(port))) == 0


@pytest.fixture(scope="session")
def appium_server():
    # 1. FORCE CLEANUP: If something is on 4723, kill it first
    if is_port_in_use(APPIUM_PORT):
        print(f"Port {APPIUM_PORT} in use. Cleaning up...")
        os.system(f"lsof -P | grep ':{APPIUM_PORT}' | awk '{{print $2}}' | xargs kill -9")
        time.sleep(2)

    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_fd = open(os.path.join(log_dir, "appium_server.log"), "w")

    # 2. START SERVER
    process = subprocess.Popen(
        ["appium", "--port", APPIUM_PORT, "--log-level", "info"],
        stdout=log_fd,
        stderr=log_fd,
        preexec_fn=os.setsid,
    )

    # 3. VERIFY: Wait and check if it crashed
    time.sleep(5)
    if process.poll() is not None:
        raise RuntimeError("Appium failed to start! Check Tests/logs/appium_server.log")

    yield process

    # 4. SAFER TEARDOWN
    try:
        os.killpg(os.getpgid(process.pid), 9)
    except ProcessLookupError:
        pass
    finally:
        log_fd.close()

def _build_options(bundle_id, no_reset=False):
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.automation_name = "XCUITest"
    options.device_name = DEVICE_NAME
    options.platform_version = PLATFORM_VERSION
    options.udid = UDID
    options.bundle_id = bundle_id
    options.no_reset = no_reset
    options.set_capability("appium:forceAppLaunch", True)
    options.set_capability("appium:shouldTerminateApp", True)
    options.set_capability("appium:useNewWDA", False)
    options.set_capability("appium:showXcodeLog", True)
    options.set_capability("appium:resetKeychain", True)
    return options


@pytest.fixture
def rv_driver(appium_server):
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=_build_options(RV_BUNDLE_ID))
    yield driver
    driver.quit()


@pytest.fixture
def rv_driver_no_reset(appium_server):
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=_build_options(RV_BUNDLE_ID, no_reset=True))
    yield driver
    driver.quit()


@pytest.fixture
def safari_driver(appium_server):
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=_build_options(SAFARI_BUNDLE_ID))
    yield driver
    driver.quit()


@pytest.fixture(scope="session", autouse=True)
def firebase_init():
    """Initializes Firebase using the verified absolute path."""
    # Based on your screenshot, this is the exact physical path on your Mac
    key_path = Path("/Users/omar/workspace/RandezVousUITesting/private/randezvousbeta-82ea6-firebase-adminsdk-3y9u9-382d940bea.json")

    if not key_path.exists():
        # If this still fails, we will search the whole computer for that file
        pytest.exit(f"ABSOLUTE PATH FAIL: Is the disk named something other than /Users/omar/? \nTried: {key_path}")

    if not firebase_admin._apps:
        cred = credentials.Certificate(str(key_path))
        firebase_admin.initialize_app(cred)


@pytest.fixture(autouse=True)
def setup_teardown(request,rv_driver):
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

   # print(f"Factory resetting: {RV_BUNDLE_ID}")
   # try:
   #     rv_driver.terminate_app(RV_BUNDLE_ID)
   #     rv_driver.execute_script('mobile: clearApp', {'bundleId': RV_BUNDLE_ID})
   #     rv_driver.activate_app(RV_BUNDLE_ID)
   # except Exception as e:
   #     print(f"App reset failed: {e}")

#work on reset simulator function and run whole suite
#test core functionality:
    #make sure we can complete activities and all different validation types: photo submission, honor, location(assert user is outside of radius so they can't click button to complete the quest), trivia, prompt
        #for each one validate
    #in admin dashboard create a new quest and have 1 activity of each type. Make sure the user can complete the activity. For non based tests.
    #do the same as the line above for point based quests
    #do we want to test all cases at once or seperate?
    #come up with a strategies

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """"Condenses errors when a failure occurs"""
    outcome = yield
    report = outcome.get_result()

    if report.when == 'call' and report.failed:
        driver = item.funcargs.get('rv_driver')

        if driver:
            print("\n" + "=" * 60)
            print("🚨 TEST FAILURE DETECTED 🚨")
            print(f"Test Name: {item.name}")
            print("-" * 60)

            failed_file = "Unknown"
            failed_line = "Unknown"
            error_msg = str(call.excinfo.value) if call.excinfo else "Unknown Error"

            if call.excinfo:
                for frame in call.excinfo.traceback:
                    path_str = str(frame.path)
                    if ".venv" not in path_str and "site-packages" not in path_str:
                        failed_file = path_str
                        failed_line = frame.lineno + 1

            print(f"📍 Failed at: {failed_file}:{failed_line}")

            clean_error = error_msg.splitlines()[0] if error_msg else "Unknown"
            print(f"💥 Error:     {clean_error}")
            print("-" * 60)

            failures_dir = os.path.join(item.config.rootdir, "failures")
            os.makedirs(failures_dir, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base_filename = f"{item.name}_{timestamp}"

            screenshot_path = os.path.join(failures_dir, f"{base_filename}.png")
            try:
                driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot: {screenshot_path}")
            except Exception as e:
                print(f"Failed to take screenshot: {e}")

            xml_path = os.path.join(failures_dir, f"{base_filename}.xml")
            try:
                with open(xml_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"📄 DOM State:  {xml_path}")
            except Exception as e:
                print(f"Failed to save page source: {e}")

            print("=" * 60 + "\n")