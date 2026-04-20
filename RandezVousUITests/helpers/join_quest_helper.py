from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CustomQuestPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # --- Element Identifiers ---
    # Navigation & Input
    back_button = (AppiumBy.ACCESSIBILITY_ID, "BackButton")
    quest_code_input_field = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeTextField[`value == "Custom Code"`]')

    # Search Actions
    find_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Find Quest")
    clear_search_button = (AppiumBy.ACCESSIBILITY_ID, "Clear Search")

    # Result Elements (Visible after a successful search)
    found_quest_title_label = (AppiumBy.ACCESSIBILITY_ID, "Found a Custom Quest")
    specific_quest_name_text = (AppiumBy.ACCESSIBILITY_ID, "Welcome Terp Quest")
    start_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Start Quest")

    # Footer
    create_own_quest_link = (AppiumBy.ACCESSIBILITY_ID, "Want to create a quest of your own?")

    # --- Actions ---
    def enter_quest_code(self, code):
        """Types the secret code into the input field"""
        field = self.wait.until(EC.element_to_be_clickable(self.quest_code_input_field))
        field.clear()
        field.send_keys(code)

    def click_find_quest(self):
        """Clicks the Search button"""
        self.wait.until(EC.element_to_be_clickable(self.find_quest_button)).click()

    def verify_quest_is_found(self):
        """Checks if the 'Found a Custom Quest' message appeared"""
        element = self.wait.until(EC.visibility_of_element_located(self.found_quest_title_label))
        return element.is_displayed()

    def click_start_quest(self):
        """Clicks the final 'Start Quest' button to begin the adventure"""
        self.wait.until(EC.element_to_be_clickable(self.start_quest_button)).click()
        print("Quest started!")

    def click_clear_search(self):
        """Clicks 'Clear Search' to try a different code"""
        self.wait.until(EC.element_to_be_clickable(self.clear_search_button)).click()