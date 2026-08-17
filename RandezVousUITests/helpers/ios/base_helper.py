# helpers/base_helper.py

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BaseHelper:
    def __init__(self, driver, default_timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, default_timeout)

    def is_visible(self, locator, custom_timeout=None) -> bool:
        """Generic method to check if any element is visible."""
        wait = WebDriverWait(self.driver, custom_timeout) if custom_timeout else self.wait

        try:
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def click(self, locator, custom_timeout=None):
        """Waits for an element to be clickable, then clicks it."""
        wait = (
            WebDriverWait(self.driver, custom_timeout)
            if custom_timeout
            else self.wait
        )
        element = wait.until(EC.element_to_be_clickable(locator))
        element.click()
        return element