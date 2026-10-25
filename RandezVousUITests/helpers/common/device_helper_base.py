import time

import pytest

# query_app_state codes (iOS and Android): 0 not installed, 1 not running, 2/3 backgrounded, 4 foreground.
APP_STATE_FOREGROUND = 4


class DeviceHelperBase:
    """Install-state and foreground checks shared by the iOS and Android DeviceHelpers."""

    default_app_id = None

    def __init__(self, driver):
        self.driver = driver

    def require_app_installed(self, installed, app_id=None):
        """Skips the test with a clear message if the RV app's install state doesn't match what it needs."""
        app_id = app_id or self.default_app_id
        is_installed = self.driver.is_app_installed(app_id)
        if is_installed != installed:
            wanted = "installed" if installed else "not installed"
            actual = "installed" if is_installed else "not installed"
            pytest.skip(f"Requires the RV app ({app_id}) to be {wanted}, but it is currently {actual}.")

    def wait_for_app_foreground(self, app_id=None, timeout=10):
        """Polls until the app is foregrounded, which shows a deep/intent link handed off to it."""
        app_id = app_id or self.default_app_id
        end_time = time.time() + timeout
        state = self.driver.query_app_state(app_id)
        while state != APP_STATE_FOREGROUND and time.time() < end_time:
            time.sleep(0.2)
            state = self.driver.query_app_state(app_id)
        return state
