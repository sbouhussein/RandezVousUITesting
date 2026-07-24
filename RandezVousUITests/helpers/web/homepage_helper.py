from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class HomepageHelper:
    def __init__(self, driver):
        self.driver = driver
        self.button_locator = (By.XPATH, "//*[contains(text(), 'Find Quest')]")

    def is_button_visible(self, timeout=10):
        """Waits up to 10 seconds for the button to appear."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.button_locator)
            )
            return True
        except TimeoutException:
            return False

    def click_find_quest(self):
        """Waits for the button to be clickable, then clicks it."""
        assert self.is_button_visible()
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(EC.element_to_be_clickable(self.button_locator))
        button.click()

    def get_button_text(self):
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(EC.visibility_of_element_located(self.button_locator))
        return button.text