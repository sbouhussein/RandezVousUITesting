from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SignInOverlayHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # --- Element Locators (Full Word Formatting) ---
    quests_header_text = (AppiumBy.ACCESSIBILITY_ID, "Quests")
    info_button = (AppiumBy.ACCESSIBILITY_ID, "info.circle")
    trophy_button = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")

    # Tab Bar / Filter Buttons
    active_quests_tab = (AppiumBy.ACCESSIBILITY_ID, "Active")
    past_quests_tab = (AppiumBy.ACCESSIBILITY_ID, "Past")
    custom_quests_tab = (AppiumBy.ACCESSIBILITY_ID, "Custom")

    # Custom Quest Entry (The middle section of your XML)
    joining_custom_quest_header = (AppiumBy.ACCESSIBILITY_ID, "Joining a Custom Quest?")
    custom_code_input_field = (AppiumBy.CLASS_NAME, "XCUIElementTypeTextField")

    # Account Actions
    sign_up_button = (AppiumBy.ACCESSIBILITY_ID, "Sign Up")
    log_in_button = (AppiumBy.ACCESSIBILITY_ID, "Log In")

    # --- Actions ---
    def verify_dashboard_is_displayed(self):
        """Checks if the 'Quests' header is visible."""
        try:
            return self.wait.until(EC.visibility_of_element_located(self.quests_header_text)).is_displayed()
        except Exception:
            return False

    def enter_custom_quest_code(self, code):
        """Types the custom quest code into the text field."""
        field = self.wait.until(EC.element_to_be_clickable(self.custom_code_input_field))
        field.click()
        field.send_keys(code + "\n")  # Adding \n usually dismisses the keyboard
        if self.driver.is_keyboard_shown():
            self.driver.hide_keyboard()

    def click_sign_up(self):
        """Navigates to the Sign Up flow."""
        self.wait.until(EC.element_to_be_clickable(self.sign_up_button)).click()

    def click_log_in(self):
        """Navigates to the Log In flow."""
        self.wait.until(EC.element_to_be_clickable(self.log_in_button)).click()

    def switch_to_tab(self, tab_name):
        """
        Switches between Active, Past, and Custom tabs.
        Usage: helper.switch_to_tab("Past")
        """
        locator = (AppiumBy.ACCESSIBILITY_ID, tab_name)
        self.wait.until(EC.element_to_be_clickable(locator)).click()