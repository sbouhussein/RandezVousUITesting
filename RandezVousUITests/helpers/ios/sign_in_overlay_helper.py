from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DashboardOverlay:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    quests_header_text = (AppiumBy.ACCESSIBILITY_ID, "Quests")
    info_button = (AppiumBy.IOS_PREDICATE, "label == 'Quest rules'")
    trophy_button = (AppiumBy.IOS_PREDICATE, "label == 'Leaderboard'")
    active_quests_tab = (AppiumBy.ACCESSIBILITY_ID, "Active")
    past_quests_tab = (AppiumBy.ACCESSIBILITY_ID, "Past")
    custom_quests_tab = (AppiumBy.ACCESSIBILITY_ID, "Find")
    joining_custom_quest_header = (AppiumBy.ACCESSIBILITY_ID, "Joining a Custom Quest?")
    custom_code_input_field = (AppiumBy.CLASS_NAME, "XCUIElementTypeTextField")
    sign_up_button = (AppiumBy.ACCESSIBILITY_ID, "Sign Up")
    log_in_button = (AppiumBy.ACCESSIBILITY_ID, "Log In")

    def verify_dashboard_is_displayed(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.quests_header_text)).is_displayed()
        except Exception:
            return False

    def enter_custom_quest_code(self, code):
        field = self.wait.until(EC.element_to_be_clickable(self.custom_code_input_field))
        field.click()
        field.send_keys(code + "\n")
        if self.driver.is_keyboard_shown():
            self.driver.hide_keyboard()

    def click_sign_up(self):
        self.wait.until(EC.element_to_be_clickable(self.sign_up_button)).click()

    def click_log_in(self):
        self.wait.until(EC.element_to_be_clickable(self.log_in_button)).click()

    def switch_to_tab(self, tab_name):
        self.wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, tab_name))).click()
