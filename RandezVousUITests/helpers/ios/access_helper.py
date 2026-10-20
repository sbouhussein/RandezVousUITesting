from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.ios.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.ios.ios_test_data import TEST_EMAIL, TEST_PASSWORD
from helpers.ios.login_page_helper import LoginPageHelper


class AccessHelper(CustomQuestPage):
    """The join flow from the Quests tab, driven up to (not past) the point where the app or backend refuses."""

    def sign_in(self, email=TEST_EMAIL, password=TEST_PASSWORD):
        QuestHelper(self.driver).sign_out_if_signed_in()
        LoginPageHelper(self.driver).login_with_credentials(email, password)

    def find_quest(self, quest_code):
        """Quests tab -> custom quest -> enter the code -> Find Quest, leaving the quest card on screen."""
        quest_helper = QuestHelper(self.driver)
        quest_helper.navigate_to_quests_tab()
        quest_helper.click_custom_quest_button()
        self.enter_quest_code(quest_code)
        self.click_find_quest()

    def attempt_join(self, quest_code):
        self.find_quest(quest_code)
        self.click_start_quest()

    def try_join(self, quest_code, email=TEST_EMAIL, password=TEST_PASSWORD):
        """Signs in and attempts to join, stopping at whatever the app shows."""
        self.sign_in(email, password)
        self.attempt_join(quest_code)

    def wait_for_text(self, fragment, timeout=15):
        """The first on-screen text containing `fragment`, or None if it doesn't appear in time."""
        locator = (AppiumBy.IOS_PREDICATE, f'label CONTAINS "{fragment}"')
        try:
            return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator)).get_attribute("label")
        except TimeoutException:
            return None

    def is_joined(self, timeout=5):
        """True once the quest detail screen (with its exit button) is showing."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.primary_exit_quest_button)).is_displayed()
        except TimeoutException:
            return False
