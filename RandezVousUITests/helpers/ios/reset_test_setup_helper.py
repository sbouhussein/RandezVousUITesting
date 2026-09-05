import logging
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .device_helper import RV_BUNDLE_ID


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
        self.profile.log_out_if_logged_in()

    def clear_simulator_cache(self, skip_quest_intro=True):
        self.driver.execute_script('mobile: clearAppLibrary')
        if skip_quest_intro:
            self._set_show_quest_intro(True)

    def _set_show_quest_intro(self, value):
        udid = self.driver.capabilities.get('udid')
        subprocess.run(
            ["xcrun", "simctl", "spawn", udid, "defaults", "write",
             RV_BUNDLE_ID, "showQuestIntro", "-bool", str(value).lower()],
            check=True,
        )
