from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class QuestsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # --- Element Identifiers ---
    # Tab Bar at the bottom
    quests_tab_icon = (AppiumBy.ACCESSIBILITY_ID, "scroll.fill")
    explore_tab_icon = (AppiumBy.ACCESSIBILITY_ID, "sparkle.magnifyingglass")

    # Buttons in the top Navigation Bar
    top_info_button = (AppiumBy.ACCESSIBILITY_ID, "info.circle")
    top_trophy_button = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")

    # Buttons on the main screen
    custom_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Custom")
    start_daily_quest_button = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name CONTAINS "Start!"`]')

    # Text headers
    main_header_title = (AppiumBy.ACCESSIBILITY_ID, "Quests")
    daily_challenge_section_label = (AppiumBy.ACCESSIBILITY_ID, "DAILY CHALLENGE")

    # --- Actions (What the user does) ---
    def switch_to_quests_tab(self):
        """Clicks the Quests icon in the bottom navigation bar"""
        element = self.wait.until(EC.element_to_be_clickable(self.quests_tab_icon))
        element.click()

    def click_info_icon(self):
        """Clicks the small 'i' icon in the top left"""
        element = self.wait.until(EC.element_to_be_clickable(self.top_info_button))
        element.click()

    def start_the_daily_challenge(self):
        """Clicks the large 'Start!' button for the daily challenge"""
        element = self.wait.until(EC.element_to_be_clickable(self.start_daily_quest_button))
        element.click()