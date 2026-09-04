from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class QuestFeedHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        # Header & Navigation
        self.back_button = (AppiumBy.IOS_PREDICATE, "label == 'Back'")
        self.megaphone_button = (AppiumBy.ACCESSIBILITY_ID, "megaphone.fill")
        self.filter_button = (AppiumBy.ACCESSIBILITY_ID, "All Posts")

        # Feed Interaction
        self.comment_field = (AppiumBy.ACCESSIBILITY_ID, "Add a comment...")
        self.send_comment_button = (AppiumBy.ACCESSIBILITY_ID, "arrow.up.circle.fill")

        # Scrollable Content (Common Dates/Users in Feed)
        self.latest_date_header = (AppiumBy.ACCESSIBILITY_ID, "March 10, 2026")
        self.omar_user_text = (AppiumBy.ACCESSIBILITY_ID, "Omar")

        # Tab Bar
        self.quests_tab = (AppiumBy.ACCESSIBILITY_ID, " Quests ")
        self.explore_tab = (AppiumBy.ACCESSIBILITY_ID, " Explore ")
        self.home_tab = (AppiumBy.ACCESSIBILITY_ID, "house")
        self.participants_tab = (AppiumBy.ACCESSIBILITY_ID, " Participants ")
        self.profile_tab = (AppiumBy.ACCESSIBILITY_ID, " Profile ")

    def click_back(self):
        self.wait.until(EC.element_to_be_clickable(self.back_button)).click()

    def click_filter(self):
        self.wait.until(EC.element_to_be_clickable(self.filter_button)).click()

    def add_comment(self, text):
        field = self.wait.until(EC.presence_of_element_located(self.comment_field))
        field.send_keys(text)
        # Note: XML shows send button is 'enabled="false"' until text is entered
        self.wait.until(EC.element_to_be_clickable(self.send_comment_button)).click()

    def get_latest_post_date(self):
        element = self.wait.until(EC.presence_of_element_located(self.latest_date_header))
        return element.text

    def navigate_to_profile(self):
        self.wait.until(EC.element_to_be_clickable(self.profile_tab)).click()