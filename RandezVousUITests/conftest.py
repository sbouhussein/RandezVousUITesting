import datetime
import os
import time
import subprocess
import firebase_admin
import pytest
from appium.options.common import AppiumOptions
from dotenv import load_dotenv
from firebase_admin import credentials
from pathlib import Path

from selenium.common import InvalidSessionIdException
from selenium import webdriver
from appium import webdriver as appium_webdriver

from helpers.ios.firebase_cleanup_helper import cleanup_user_data
import socket

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

APPIUM_PORT = os.getenv("APPIUM_PORT", "4723")
APPIUM_SERVER_URL = f"http://127.0.0.1:{APPIUM_PORT}"
DEVICE_NAME = "iPhone 17 Pro"
PLATFORM_VERSION = "26.2"
#UDID = "02702BB3-0AE0-4167-9651-39F68787A375"
RV_BUNDLE_ID = os.getenv("RV_BUNDLE_ID", "sbouhussein.github.io-rvsite.RandezVous")
SAFARI_BUNDLE_ID = os.getenv("SAFARI_BUNDLE_ID", "com.apple.mobilesafari")

def pytest_addoption(parser):
    parser.addoption("--udid", action="store", default="booted", help="UDID of the iOS Simulator")
    # This creates the toggle. Usage: pytest --headless
    parser.addoption("--headless", action="store_true", help="Run the simulator in headless mode")

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

    log_dir = os.path.join(os.path.dirname(__file__), "RandezVousUITests/Tests/logs")
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

    log_dir = os.path.join(os.path.dirname(__file__), "RandezVousUITests/Tests/logs")
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
    options.set_capability("appium:isHeadless", is_headless)
    options.set_capability("appium:launchTimeout", 90000)
    options.set_capability("appium:wdaLaunchTimeout", 90000)
    options.set_capability("appium:appPushTimeout", 60000)
    options.set_capability("appium:waitForIdleTimeout", 500)
    return options


@pytest.fixture
def rv_driver(request, appium_server):
    target_udid = request.config.getoption("--udid")
    target_headless = request.config.getoption("--headless")

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


@pytest.fixture
def desktop_safari_driver():
    """Launches the native Desktop Safari browser on macOS."""
    driver = webdriver.Safari()

    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.fixture
def rv_driver_no_reset(appium_server):
    driver = webdriver.Remote(APPIUM_SERVER_URL, options=_build_options(RV_BUNDLE_ID, no_reset=True))
    yield driver
    driver.quit()


@pytest.fixture
def safari_driver(request, appium_server):
    target_udid = request.config.getoption("--udid")
    target_headless = request.config.getoption("--headless")

    driver = webdriver.Remote(
        APPIUM_SERVER_URL,
        options=_build_options(SAFARI_BUNDLE_ID, target_udid, is_headless=target_headless)
    )

    yield driver

    try:
        driver.quit()
    except Exception as e:
        print(f"\n Ignored driver teardown error: {e}")


@pytest.fixture(scope="session", autouse=True)
def firebase_init():
    """Initializes Firebase using the verified absolute path."""
    project_root = Path(__file__).parent.parent.resolve()
    key_path = project_root / "private" / "service-account-key.json"

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

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Captures test results, aggregated logs, and screenshots across all phases"""
    outcome = yield
    report = outcome.get_result()

    nodeid = item.nodeid
    if nodeid not in _compiled_test_results:
        _compiled_test_results[nodeid] = {
            "name": item.name,
            "status": "PASSED",
            "logs": "",
            "error_msg": "",
            "failure_line": "",
            "screenshot_b64": "",
            "duration": 0.0
        }

    test_entry = _compiled_test_results[nodeid]
    test_entry["duration"] += report.duration

    if report.capstdout:
        phase_header = f"--- [{report.when.upper()} PHASE] ---\n"
        test_entry["logs"] += phase_header + report.capstdout.strip() + "\n\n"

    if report.failed:
        test_entry["status"] = "FAILED"

        if call.excinfo:
            test_entry["error_msg"] = str(call.excinfo.value)
            try:
                # 🎯 NEW LOGIC: Walk backwards through the stacktrace
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

                test_entry["failure_line"] = f"📍 File: {file_name} | Line: {line_number}\n➔ Code: {offending_code}"
            except Exception:
                test_entry["failure_line"] = "⚠️ Could not parse the exact line of failure."

        driver = item.funcargs.get('rv_driver') or item.funcargs.get('driver')
        if driver and not test_entry["screenshot_b64"]:
            try:
                test_entry["screenshot_b64"] = driver.get_screenshot_as_base64()
            except Exception as e:
                print(f"Failed to capture frame: {e}")


def pytest_sessionfinish(session, exitstatus):
    """Compiles results and saves the dashboard into a dedicated reports directory"""
    # 📁 Requirement 3: Change directory to an isolated 'reports' folder
    reports_dir = os.path.join(session.config.rootdir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

    report_path = os.path.join(reports_dir, f"Execution_Report_{file_timestamp}.html")

    # Generate html card blocks dynamically from our data dictionary
    html_cards = []
    total_passed = 0
    total_failed = 0

    for nodeid, data in _compiled_test_results.items():
        is_failed = data["status"] == "FAILED"
        if is_failed:
            total_failed += 1
            status_icon, border_color, bg_color = "❌ FAILED", "#d32f2f", "#ffebee"
        else:
            total_passed += 1
            status_icon, border_color, bg_color = "✅ PASSED", "#388e3c", "#e8f5e9"

        error_block = ""
        if is_failed:
            error_block = f"""
            <h4 style="color:#d32f2f; margin: 12px 0 4px 0;">🔴 Traceback Error Message:</h4>
            <pre style="color:#c62828; background: #fff; padding: 12px; border-radius: 6px; border-left: 5px solid #d32f2f; font-family: monospace; white-space: pre-wrap;">{data['error_msg']}</pre>

            <h4 style="color:#d32f2f; margin: 12px 0 4px 0;">🎯 Last Line Executed Before Crash:</h4>
            <pre style="color:#1a1a1a; background: #fff3cd; padding: 12px; border-radius: 6px; border-left: 5px solid #ffb300; font-family: monospace; font-weight: bold;">{data['failure_line']}</pre>
            """

        screenshot_block = ""
        if data["screenshot_b64"]:
            screenshot_block = f"""
            <h4 style="margin: 12px 0 4px 0;">📸 Screen Capture At Failure:</h4>
            <img src="data:image/png;base64,{data['screenshot_b64']}" style="max-width:340px; border: 2px solid {border_color}; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.15);">
            """

        card = f"""
        <div style="border: 1px solid {border_color}; background-color: {bg_color}; margin: 20px 0; padding: 18px; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,0,0,0.1); padding-bottom: 8px;">
                <h2 style="margin: 0; color: {border_color}; font-size: 20px;">{status_icon}: {data['name']}</h2>
                <span style="font-size: 13px; color: #555; background: rgba(0,0,0,0.05); padding: 4px 8px; border-radius: 12px;">⏳ Duration: {data['duration']:.2f}s</span>
            </div>

            <h4 style="margin: 12px 0 4px 0; color: #333;">📝 All Aggregated Console Output (Prints):</h4>
            <pre style="background: #23241f; color: #f8f8f2; padding: 14px; border-radius: 6px; overflow-x: auto; font-family: 'Courier New', Courier, monospace; font-size: 13px; line-height: 1.4;">{data['logs'].strip() or "No print statements caught in this execution."}</pre>

            {error_block}
            {screenshot_block}
        </div>
        """
        html_cards.append(card)

    # Compile the final document layout
    html_layout = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Automation Execution Report</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif; background-color: #f4f6f9; padding: 30px; margin: 0;">
        <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); max-width: 1050px; margin: 0 auto;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #ecf0f1; padding-bottom: 12px; margin-top: 0;">🧪 Automation Run Summary</h1>

            <div style="display: flex; gap: 40px; background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 10px; font-size: 15px;">
                <div><strong>📅 Run Date:</strong> {timestamp}</div>
                <div><strong>📊 Total Tests Executed:</strong> {len(_compiled_test_results)}</div>
                <div style="color: #388e3c;"><strong>🟢 Passed:</strong> {total_passed}</div>
                <div style="color: #d32f2f;"><strong>🔴 Failed:</strong> {total_failed}</div>
            </div>

            {''.join(html_cards)}
        </div>
    </body>
    </html>
    """

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_layout)

    print(f"\n📊 Refined Dashboard Summary Generated At: {report_path}")