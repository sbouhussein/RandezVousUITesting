from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class QuestHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        # Locators
        self.quests_header = (AppiumBy.ACCESSIBILITY_ID, "Quests")
        self.trophy_button = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
        self.active_badge = (AppiumBy.ACCESSIBILITY_ID, "Active")
        self.exit_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Exit Quest")
        self.hide_requirements_button = (AppiumBy.ACCESSIBILITY_ID, "Hide Requirements")

        # Content (Using Class Chain for the redundant automation2 layers)
        self.quest_title = (AppiumBy.IOS_CLASSCHAIN, "**/XCUIElementTypeStaticText[`label == 'automation2'`][1]")
        self.quest_date_range = (AppiumBy.ACCESSIBILITY_ID, "March 9, 2026 - March 3, 2027")
        self.quest_feed_button = (AppiumBy.ACCESSIBILITY_ID, "Quest Feed, : Hello")

        # Tab Bar
        self.quests_tab = (AppiumBy.ACCESSIBILITY_ID, " Quests ")
        self.explore_tab = (AppiumBy.ACCESSIBILITY_ID, " Explore ")
        self.home_tab = (AppiumBy.ACCESSIBILITY_ID, "house")
        self.participants_tab = (AppiumBy.ACCESSIBILITY_ID, " Participants ")
        self.profile_tab = (AppiumBy.ACCESSIBILITY_ID, " Profile ")

    def click_exit_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.exit_quest_button)).click()

    def get_quest_title(self):
        element = self.wait.until(EC.presence_of_element_located(self.quest_title))
        return element.text

    def click_hide_requirements(self):
        self.wait.until(EC.element_to_be_clickable(self.hide_requirements_button)).click()

    def click_quests_tab(self):
        self.wait.until(EC.element_to_be_clickable(self.quests_tab)).click()

    def is_active(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.active_badge)).is_displayed()
        except:
            return False