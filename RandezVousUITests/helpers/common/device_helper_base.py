import time

import pytest

# query_app_state's return codes -- same scale for Appium's XCUITest (iOS) and
# UiAutomator2 (Android) drivers: 0 not installed, 1 not running, 2/3 backgrounded,
# 4 running in the foreground.
APP_STATE_FOREGROUND = 4


class DeviceHelperBase:
    """Install-state / foreground checks shared by the iOS and Android DeviceHelpers --
    is_app_installed/query_app_state behave identically under Appium regardless of
    platform, keyed by whatever app identifier each subclass defaults to (bundle ID on
    iOS, package name on Android)."""

    default_app_id = None

    def __init__(self, driver):
        self.driver = driver

    def require_app_installed(self, installed, app_id=None):
        """Guards a test whose outcome depends on the RV app's install state instead of
        assuming it, skipping with a clear message rather than silently exercising the
        wrong branch."""
        app_id = app_id or self.default_app_id
        is_installed = self.driver.is_app_installed(app_id)
        if is_installed != installed:
            wanted = "installed" if installed else "not installed"
            actual = "installed" if is_installed else "not installed"
            pytest.skip(f"Requires the RV app ({app_id}) to be {wanted}, but it is currently {actual}.")

    def wait_for_app_foreground(self, app_id=None, timeout=10):
        """Polls query_app_state until the app is foregrounded -- the signal a deep/intent
        link actually handed off to it, mirroring appLinks.js's own 'blur' check from the
        web side."""
        app_id = app_id or self.default_app_id
        end_time = time.time() + timeout
        state = self.driver.query_app_state(app_id)
        while state != APP_STATE_FOREGROUND and time.time() < end_time:
            time.sleep(0.2)
            state = self.driver.query_app_state(app_id)
        return state
