import time

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

    def _wait_for_stable_position(self, element, timeout=1.0, poll=0.05):
        """Waits until the element's rect stops changing -- guards against
        clicking mid-CSS-transition (e.g. an accordion still opening),
        which element_to_be_clickable's displayed+enabled check misses."""
        end_time = time.time() + timeout
        last_rect = None
        while time.time() < end_time:
            try:
                rect = element.rect
            except Exception:
                return  # gone stale -- let the caller's own click/retry handle it
            if rect == last_rect:
                return
            last_rect = rect
            time.sleep(poll)

    def click(self, locator, custom_timeout=None):
        """Waits for an element, scrolls it into view, and clicks it. Falls back to JS click if blocked."""
        wait = (
            WebDriverWait(self.driver, custom_timeout)
            if custom_timeout
            else self.wait
        )
        element = wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
        self._wait_for_stable_position(element)

        try:
            element.click()
        except Exception:
            # Fallback for when sticky headers, footers, or overlays intercept the native click event
            self.driver.execute_script("arguments[0].click();", element)

        return element