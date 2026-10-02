from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.web.base_helper import BaseHelper


class OnboardingPageHelper(BaseHelper):
    """QuestOnboarding's action cards: AppActionCard (mobile, see conftest.mobile_chrome_driver
    / safari_driver) and DefaultActionCard (desktop_safari_driver) -- both call handleStart()
    via a different button, and both render the shared AccessErrorPanel on failure."""

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
        """Fallback href for an app that isn't installed. Generous default timeout: often the first
        hit on QuestOnboarding's lazy chunk after a Vite restart."""
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
        """Real click, not just reading the href -- on iOS, openAppOrFallback (appLinks.js) only
        starts its 1500ms no-blur fallback timer from an actual click event."""
        self.click(self.open_in_app_link, custom_timeout=custom_timeout)

    def wait_for_app_fallback_redirect(self, from_url, custom_timeout=10):
        """Waits out openAppOrFallback's 1500ms fallback (appLinks.js: no 'blur' event means the
        deep link's custom scheme wasn't handled, i.e. the app isn't installed) and returns the
        URL it lands on. custom_timeout must clear 1500ms with room for the navigation itself."""
        wait = WebDriverWait(self.driver, custom_timeout)
        wait.until(EC.url_changes(from_url))
        return self.driver.current_url
