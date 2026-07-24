import logging
from selenium.webdriver.common.by import By
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
        logging.info("Starting simulator reset to default state...")
        self.driver.terminate_app("sbouhussein.github.io-rvsite.RandezVous")
        self.driver.activate_app("sbouhussein.github.io-rvsite.RandezVous")

        try:
            if self._is_signed_in():
                self.sign_out_flow()
            logging.info("App is in a signed-out state.")
        except Exception as e:
            logging.warning(f"Error during sign-out check: {e}")
            self.driver.reset()

    def _is_signed_in(self):
        return len(self.driver.find_elements(By.ACCESSIBILITY_ID, "Tab Bar")) > 0

    def sign_out_flow(self):
        logging.info("Executing sign-out flow...")
        self.driver.find_element(By.ACCESSIBILITY_ID, " Profile ").click()
        self.profile.wait_for_screen_load()
        self.profile.tap_logout()
        try:
            self.driver.find_element(By.ACCESSIBILITY_ID, "Confirm Logout").click()
        except Exception:
            pass

    def clear_simulator_cache(self):
        self.driver.execute_script('mobile: clearAppLibrary')
