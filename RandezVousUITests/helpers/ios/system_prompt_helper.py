from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (NoSuchElementException, StaleElementReferenceException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helpers.common.device_helper_base import APP_STATE_FOREGROUND
from helpers.ios.device_helper import RV_BUNDLE_ID


class SystemPromptHelper:
    """Dismisses iOS-owned prompts that the app doesn't control ("Save Password?", the App Store
    rating card)."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 5)

    # "Never for ..." variants appear on some builds.
    dismiss_labels = ["Not Now", "Not now", "Never for This App", "Never for This Website"]
    save_password_dismiss_button = (
        AppiumBy.IOS_PREDICATE,
        "type == 'XCUIElementTypeButton' AND label IN {"
        + ", ".join(f"'{label}'" for label in dismiss_labels) + "}",
    )
    # SKStoreReviewController's "Enjoying RandezVous?" card; non-App Store builds show it on every request.
    rating_not_now_button = (AppiumBy.ACCESSIBILITY_ID, "Not Now")

    def _tap_until_gone(self, locator, timeout, attempts=3):
        """Taps `locator` until it leaves the screen; returns whether it appeared within `timeout`.
        A tap during the present animation is swallowed, and the prompt can auto-dismiss between
        find and tap, so neither a stale element nor a no-op tap counts as done."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            return False
        for _ in range(attempts):
            try:
                self.driver.find_element(*locator).click()
            except (StaleElementReferenceException, NoSuchElementException):
                pass
            try:
                WebDriverWait(self.driver, 3).until(EC.invisibility_of_element_located(locator))
                return True
            except TimeoutException:
                continue
        raise AssertionError(f"Prompt {locator} still on screen after {attempts} taps")

    def dismiss_save_password_prompt(self, timeout=5):
        """Dismisses "Save Password?" if it appears within `timeout`; returns whether it did."""
        # The sheet is usually in the app's own hierarchy...
        if self._tap_until_gone(self.save_password_dismiss_button, timeout):
            print("Dismissed iOS Save Password prompt.")
            return True

        # ...but when iOS presents it as a SpringBoard alert it's only reachable this way.
        try:
            buttons = self.driver.execute_script('mobile: alert', {'action': 'getButtons'})
        except WebDriverException:
            return False
        for label in self.dismiss_labels:
            if label in buttons:
                self.driver.execute_script('mobile: alert', {'action': 'dismiss', 'buttonLabel': label})
                print(f"Dismissed iOS system alert via '{label}'.")
                return True
        return False

    def dismiss_rating_prompt(self, timeout=10):
        """Dismisses the App Store rating card if it appears within `timeout`; returns whether it did."""
        if self._tap_until_gone(self.rating_not_now_button, timeout):
            print("System Alert: Dismissed the 'Enjoying RandezVous?' rating popup.")
            return True
        return False

    def ensure_app_in_foreground(self, bundle_id=RV_BUNDLE_ID):
        """Reactivates the app if a system prompt tap bounced the session out to Settings."""
        if self.driver.query_app_state(bundle_id) != APP_STATE_FOREGROUND:
            print(f"{bundle_id} left the foreground after a system prompt; reactivating it.")
            self.driver.activate_app(bundle_id)
