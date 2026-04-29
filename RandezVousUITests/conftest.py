import os
import time
import subprocess
import pytest
from dotenv import load_dotenv
from appium import webdriver
from appium.options.ios import XCUITestOptions

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Required environment variable '{name}' is not set. See .env.example.")
    return value

APPIUM_PORT = os.getenv("APPIUM_PORT", "4723")
APPIUM_SERVER_URL = f"http://127.0.0.1:{APPIUM_PORT}"
DEVICE_NAME = _require_env("DEVICE_NAME")
PLATFORM_VERSION = _require_env("PLATFORM_VERSION")
UDID = _require_env("UDID")
RV_BUNDLE_ID = os.getenv("RV_BUNDLE_ID", "sbouhussein.github.io-rvsite.RandezVous")
SAFARI_BUNDLE_ID = os.getenv("SAFARI_BUNDLE_ID", "com.apple.mobilesafari")


@pytest.fixture(scope="session")
def appium_server():
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_fd = open(os.path.join(log_dir, "appium_server.log"), "w")
    process = subprocess.Popen(
        ["appium", "--port", APPIUM_PORT, "--log-level", "info"],
        stdout=log_fd,
        stderr=log_fd,
        preexec_fn=os.setsid,
    )
    time.sleep(5)
    yield process
    os.killpg(os.getpgid(process.pid), 9)
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
