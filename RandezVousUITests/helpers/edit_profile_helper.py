from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class EditProfileHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    # --- Locators ---
    edit_profile_header = (AppiumBy.ACCESSIBILITY_ID, "Edit Profile")
    done_button = (AppiumBy.ACCESSIBILITY_ID, "Done")
    profile_icon = (AppiumBy.ACCESSIBILITY_ID, "icon30")
    choose_icon_button = (AppiumBy.ACCESSIBILITY_ID, "Choose Icon")
    display_name_label = (AppiumBy.ACCESSIBILITY_ID, "Display Name")
    display_name_field = (AppiumBy.XPATH, "//XCUIElementTypeTextField[@value='Display Name' or @placeholderValue='Display Name']")

    def click_done(self):
        self.wait.until(EC.element_to_be_clickable(self.done_button)).click()

    def change_profile_icon(self):
        self.wait.until(EC.element_to_be_clickable(self.choose_icon_button)).click()

    def set_display_name(self, name):
        field = self.wait.until(EC.presence_of_element_located(self.display_name_field))
        field.clear()
        field.send_keys(name)

    def get_current_display_name(self):
        return self.wait.until(EC.presence_of_element_located(self.display_name_field)).get_attribute("value")
