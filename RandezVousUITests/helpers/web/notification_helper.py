import time
from datetime import datetime, timezone

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common.notification_data_helper import sent_item, wait_for_web_token
from helpers.web.base_helper import BaseHelper
from helpers.web.quest_test_data import BASE_URL


class NotificationSettingHelper(BaseHelper):
    """The quest page's "Notifications" dropdown (shown to signed-in members of a quest with a feed)."""

    toggle = (By.XPATH, "//button[starts-with(@aria-label, 'Notifications:')]")
    LABELS = {0: "None", 1: "Announcements only", 2: "All activity"}

    def grant_browser_permission(self):
        """Allows notifications for the app's origin, as the browser's permission prompt would; turning a setting on needs it."""
        self.driver.execute_cdp_cmd("Browser.grantPermissions", {"origin": BASE_URL, "permissions": ["notifications"]})
        self.opened_at = datetime.now(timezone.utc)
        self.token_ready = False

    def current_label(self):
        self.wait.until(EC.visibility_of_element_located(self.toggle))
        return self.driver.find_element(*self.toggle).get_attribute("aria-label").split(": ", 1)[1]

    def choose_setting(self, setting, on_prompt=None):
        """Opens the dropdown and picks 0 (none), 1 (announcements only) or 2 (all activity).
        `on_prompt` runs after the pick, for a browser permission prompt that blocks the change (real Android Chrome)."""
        self.current_label()  # the quest page can still be loading
        for _ in range(3):  # the toggle re-renders as the quest data finishes loading
            try:
                self.click(self.toggle, custom_timeout=30)
                break
            except StaleElementReferenceException:
                time.sleep(1)
        self.click((By.XPATH, f"//button[@role='option'][contains(., '{self.LABELS[setting]}')]"))
        if on_prompt:
            on_prompt()
        WebDriverWait(self.driver, 45).until(lambda d: self.current_label() == self.LABELS[setting])  # a first pick also fetches and registers a push token

    def allow_android_prompt(self):
        """Taps Allow on Android Chrome's native "wants to send you notifications" prompt, then returns to the page."""
        page_context = self.driver.current_context
        self.driver.switch_to.context("NATIVE_APP")
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((AppiumBy.XPATH, '//*[@text="Allow"]'))).click()
        except TimeoutException:  # already allowed on an earlier pick
            pass
        finally:
            self.driver.switch_to.context(page_context)

    def shown_notifications(self):
        """(title, body) of every notification the service worker has shown and not yet closed, read from the browser."""
        return [tuple(n) for n in self.driver.execute_async_script(
            "const done = arguments[arguments.length - 1];"
            "navigator.serviceWorker.ready.then(r => r.getNotifications())"
            ".then(list => done(list.map(n => [n.title, n.body]))).catch(() => done([]));")]

    def hide_page(self):
        """Puts the app in a background tab: FCM hands pushes to a visible page instead of the service worker, which shows nothing."""
        self.page_tab = self.driver.current_window_handle
        self.driver.switch_to.new_window("tab")
        self.driver.get("about:blank")

    def wait_for_notification(self, title, body, timeout=60):
        """After hide_page(): True once the browser shows a notification with this title and body, False if none arrives in time."""
        blank_tab = self.driver.current_window_handle
        deadline = time.monotonic() + timeout
        while True:
            time.sleep(5)
            self.driver.switch_to.window(self.page_tab)
            found = (title, body) in self.shown_notifications()
            if found or time.monotonic() > deadline:
                return found
            self.driver.switch_to.window(blank_tab)

    def push_arrives(self, org_id, qid, email, kind, expected):
        """Sends an announcement or post ("announcement" / "post") and returns whether the browser shows the push for it.
        Waits up to 60 s when one is expected, 10 s when not (the function is known to have run by then)."""
        if not self.token_ready:  # the page registers its push token a moment after the setting is saved
            self.token_ready = wait_for_web_token(email, self.opened_at)
        self.hide_page()
        blank_tab = self.driver.current_window_handle
        try:
            with sent_item(org_id, qid, kind) as item:
                item.wait_processed()
                return self.wait_for_notification(item.title, item.body, timeout=60 if expected else 10)
        finally:
            self.driver.switch_to.window(blank_tab)
            self.driver.close()
            self.driver.switch_to.window(self.page_tab)

    def error_text(self):
        els = self.driver.find_elements(By.XPATH, "//button[starts-with(@aria-label, 'Notifications:')]/following-sibling::p")
        return els[0].text if els else None
