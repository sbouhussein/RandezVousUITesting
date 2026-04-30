from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class QuestHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        # Tab Bar
        self.quests_tab = (AppiumBy.ACCESSIBILITY_ID, "scroll.fill")
        self.home_tab = (AppiumBy.ACCESSIBILITY_ID, "house")
        self.explore_tab = (AppiumBy.ACCESSIBILITY_ID, " Explore ")
        self.participants_tab = (AppiumBy.ACCESSIBILITY_ID, " Participants ")
        self.profile_tab = (AppiumBy.ACCESSIBILITY_ID, " Profile ")

        # Quests Page
        self.quests_header = (AppiumBy.ACCESSIBILITY_ID, "Quests")
        self.trophy_button = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
        self.active_badge = (AppiumBy.ACCESSIBILITY_ID, "Active")
        self.custom_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Custom")
        self.join_quest_page = (AppiumBy.ACCESSIBILITY_ID, "Join a Quest")

        # Active Quest Controls
        self.primary_exit_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Exit Quest")
        self.secondary_exit_confirm_button = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeSheet/**/XCUIElementTypeButton[`name == "Exit Quest"`]')
        self.hide_requirements_button = (AppiumBy.ACCESSIBILITY_ID, "Hide Requirements")
        self.quest_title = (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeStaticText[`label == 'automation2'`][1]")
        self.quest_date_range = (AppiumBy.ACCESSIBILITY_ID, "March 9, 2026 - March 3, 2027")
        self.quest_feed_button = (AppiumBy.ACCESSIBILITY_ID, "Quest Feed, : Hello")

    def navigate_to_quests_tab(self):
        self.wait.until(EC.element_to_be_clickable(self.quests_tab)).click()
        assert self.wait.until(EC.visibility_of_element_located(self.quests_header)).is_displayed(), \
            "Quests page header not visible after clicking tab"

    def click_custom_quest_button(self):
        self.wait.until(EC.element_to_be_clickable(self.custom_quest_button)).click()
        assert self.wait.until(EC.visibility_of_element_located(self.join_quest_page)).is_displayed(), \
            "Custom Quest overlay did not appear"

    def click_exit_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.primary_exit_quest_button)).click()
        self.wait.until(EC.element_to_be_clickable(self.secondary_exit_confirm_button)).click()

    def get_quest_title(self):
        return self.wait.until(EC.presence_of_element_located(self.quest_title)).text

    def click_hide_requirements(self):
        self.wait.until(EC.element_to_be_clickable(self.hide_requirements_button)).click()

    def is_active(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.active_badge)).is_displayed()
        except Exception:
            return False


class CustomQuestPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # --- Element Identifiers ---
    back_button = (AppiumBy.ACCESSIBILITY_ID, "BackButton")
    quest_code_input_field = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeTextField[`value == "Custom Code"`]')
    find_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Find Quest")
    clear_search_button = (AppiumBy.ACCESSIBILITY_ID, "Clear Search")
    found_quest_title_label = (AppiumBy.ACCESSIBILITY_ID, "Found a Custom Quest")
    specific_quest_name_text = (AppiumBy.ACCESSIBILITY_ID, "Welcome Terp Quest")
    start_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Start Quest")
    create_own_quest_link = (AppiumBy.ACCESSIBILITY_ID, "Want to create a quest of your own?")

    def enter_quest_code(self, code):
        field = self.wait.until(EC.element_to_be_clickable(self.quest_code_input_field))
        field.clear()
        field.send_keys(code)

    def click_find_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.find_quest_button)).click()

    def verify_quest_is_found(self):
        return self.wait.until(EC.visibility_of_element_located(self.found_quest_title_label)).is_displayed()

    def click_start_quest(self):
        # Native tap required — standard click is unreliable on this button
        start_btn = self.wait.until(EC.presence_of_element_located(self.start_quest_button))
        self.driver.execute_script('mobile: tap', {'element': start_btn.id, 'x': 10, 'y': 10})

    def click_clear_search(self):
        self.wait.until(EC.element_to_be_clickable(self.clear_search_button)).click()
