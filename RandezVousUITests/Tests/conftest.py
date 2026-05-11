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



load_dotenv(os.path.join(os.path.dirname(__file__), "../..", ".env"))
import socket


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

APPIUM_PORT = os.getenv("APPIUM_PORT", "4723")
APPIUM_SERVER_URL = f"http://127.0.0.1:{APPIUM_PORT}"
DEVICE_NAME = "iPhone 17 Pro"
PLATFORM_VERSION = "26.2"
UDID = "02702BB3-0AE0-4167-9651-39F68787A375"
RV_BUNDLE_ID = os.getenv("RV_BUNDLE_ID", "sbouhussein.github.io-rvsite.RandezVous")
SAFARI_BUNDLE_ID = os.getenv("SAFARI_BUNDLE_ID", "com.apple.mobilesafari")

import socket


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
    options.set_capability("appium:showXcodeLog", False)
    options.set_capability("appium:useNewWDA", False)
    if no_reset:
        options.no_reset = True
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
    key_path = Path("/Users/omar/RandezVousUITesting/private/randezvousbeta-82ea6-firebase-adminsdk-3y9u9-382d940bea.json")

    if not key_path.exists():
        # If this still fails, we will search the whole computer for that file
        pytest.exit(f"❌ ABSOLUTE PATH FAIL: Is the disk named something other than /Users/omar/? \nTried: {key_path}")

    if not firebase_admin._apps:
        cred = credentials.Certificate(str(key_path))
        firebase_admin.initialize_app(cred)
    yield