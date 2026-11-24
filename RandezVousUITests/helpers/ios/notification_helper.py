import html
import re
import time

from appium.webdriver.common.appiumby import AppiumBy

from helpers.common.notification_data_helper import sent_item
from helpers.ios.base_helper import BaseHelper


class NotificationHelper(BaseHelper):
    """The Quest Feed's notification bell menu, and reading delivered notifications from the lock screen (iOS shows none while the app is open)."""

    menu_button = (AppiumBy.ACCESSIBILITY_ID, "Notification settings")
    SETTINGS = {0: "No Notifications", 1: "Announcements Only", 2: "All Notifications"}

    def _option(self, name):
        return (AppiumBy.IOS_PREDICATE, f"label == '{name}' AND type IN {{'XCUIElementTypeButton', 'XCUIElementTypeMenuItem'}}")

    def choose_setting(self, setting):
        """Picks 0 (none), 1 (announcements only) or 2 (all) from the bell menu."""
        self.click(self.menu_button)
        self.click(self._option(self.SETTINGS[setting]))

    def lock_device(self):
        """Puts the app in the background on the lock screen, where delivered notifications are listed."""
        self.driver.execute_script("mobile: pressButton", {"name": "home"})
        self.driver.lock()
        time.sleep(2)

    def unlock_device(self):
        """Unlocks and returns to the app, which lock_device left in the background."""
        self.driver.unlock()
        self.driver.activate_app(self.driver.capabilities["bundleId"])

    def _lock_screen_label(self, tag):
        """The lock-screen notification whose text contains `tag`, e.g. "RANDEZVOUS, now, <title>, <message>", else None.
        Read from the page source: element queries don't see SpringBoard's notification list."""
        for label in re.findall(r'label="([^"]*)"', self.driver.page_source):
            label = html.unescape(label)
            if tag in label and label.startswith(("RANDEZVOUS", "now")):
                return label
        return None

    def lock_screen_notification(self, org_id, qid, kind, expected, shown_wait=40, absent_wait=15):
        """Sends an announcement or feed post while the device is locked and returns (item, label): the notification that
        reached the lock screen (None if none did). A notification is waited for up to `shown_wait` seconds when `expected`,
        otherwise `absent_wait` seconds after the backend has handled the item."""
        with sent_item(org_id, qid, kind) as item:
            item.wait_processed()
            tag = item.body.split("(")[-1].rstrip(")")  # the time stamp, unique to this send
            deadline = time.monotonic() + (shown_wait if expected else absent_wait)
            while time.monotonic() < deadline:
                label = self._lock_screen_label(tag)
                if label:
                    return item, label
                time.sleep(2)
            return item, None
