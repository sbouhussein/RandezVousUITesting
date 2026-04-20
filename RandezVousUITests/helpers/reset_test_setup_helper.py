import logging
from selenium.webdriver.support.ui import WebDriverWait


class TestSetupHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        from .profile_helper import ProfileHelper
        from .quest_feed_helper import QuestFeedHelper

        self.profile = ProfileHelper(self.driver)
        self.quest_feed = QuestFeedHelper(self.driver)

    def reset_to_default_state(self):
        """
        Ensure the simulator is signed out
        and application data is cleared.
        """
        logging.info("Starting simulator reset to default state...")
        self.driver.terminate_app("sbouhussein.github.io-rvsite.RandezVous")
        self.driver.activate_app("sbouhussein.github.io-rvsite.RandezVous")

        try:
            if self._is_signed_in():
                self.sign_out_flow()
            logging.info("App is in a signed-out state.")
        except Exception as e:
            logging.warning(f"Error during sign-out check: {e}")
            # Fallback: Force clear app data if supported by the environment
            self.driver.reset()

    def _is_signed_in(self):
        """Checks the UI to see if a session is active."""
        # Check for the existence of the Tab Bar (which appears post-login)
        return len(self.driver.find_elements(By.ACCESSIBILITY_ID, "Tab Bar")) > 0

    def sign_out_flow(self):
        """Navigates to profile and performs logout."""
        logging.info("Executing sign-out flow...")

        # Navigate to Profile Tab
        profile_tab = self.driver.find_element(By.ACCESSIBILITY_ID, " Profile ")
        profile_tab.click()

        self.profile.wait_for_screen_load()
        self.profile.tap_logout()

        try:
            confirm = self.driver.find_element(By.ACCESSIBILITY_ID, "Confirm Logout")
            confirm.click()
        except:
            pass

    def clear_simulator_cache(self):
        """Optional: Deep reset of the iOS Simulator settings."""
        self.driver.execute_script('mobile: clearAppLibrary')