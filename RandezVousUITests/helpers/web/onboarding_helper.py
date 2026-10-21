from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.web.base_helper import BaseHelper


class OnboardingPageHelper(BaseHelper):
    """QuestOnboarding's action cards: AppActionCard (mobile) and DefaultActionCard (desktop), both rendering AccessErrorPanel on failure."""

    open_in_app_link = (By.XPATH, "//a[contains(normalize-space(), 'Open in App')]")
    continue_on_web_button = (
        By.XPATH,
        "//button[contains(normalize-space(), 'Prefer the web? Continue here.') "
        "or normalize-space()='Checking access…']",
    )
    start_quest_button = (
        By.XPATH,
        "//button[contains(normalize-space(), 'Start Quest') or normalize-space()='Checking access…']",
    )

    def get_open_in_app_href(self, custom_timeout=30):
        """Fallback href for an app that isn't installed; generous timeout for the lazy chunk after a Vite restart."""
        wait = WebDriverWait(self.driver, custom_timeout)
        element = wait.until(EC.visibility_of_element_located(self.open_in_app_link))
        return element.get_attribute("href")

    def click_continue_on_web(self, custom_timeout=30):
        """Triggers handleStart(), the only path that populates accessError/isBanned onto AppActionCard."""
        self.click(self.continue_on_web_button, custom_timeout=custom_timeout)

    def click_start_quest(self, custom_timeout=30):
        """Desktop equivalent of click_continue_on_web -- both trigger handleStart()."""
        self.click(self.start_quest_button, custom_timeout=custom_timeout)

    def click_open_in_app(self, custom_timeout=30):
        """A real click, since on iOS the 1500ms fallback timer only starts from a click event."""
        self.click(self.open_in_app_link, custom_timeout=custom_timeout)

    def wait_for_app_fallback_redirect(self, from_url, custom_timeout=10):
        """Waits out the 1500ms no-blur fallback and returns the URL it lands on; custom_timeout must exceed it."""
        wait = WebDriverWait(self.driver, custom_timeout)
        wait.until(EC.url_changes(from_url))
        return self.driver.current_url
