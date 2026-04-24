from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EditProfileHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    # --- Locators ---
    # Navigation & Header
    self.edit_profile_header = (AppiumBy.ACCESSIBILITY_ID, "Edit Profile")
    self.done_button = (AppiumBy.ACCESSIBILITY_ID, "Done")

    # Profile Image Section
    self.profile_icon = (AppiumBy.ACCESSIBILITY_ID, "icon30")
    self.choose_icon_button = (AppiumBy.ACCESSIBILITY_ID, "Choose Icon")

    # Form Fields
    self.display_name_label = (AppiumBy.ACCESSIBILITY_ID, "Display Name")
    # Using XPath for the text field as it lacks a unique accessibility ID in this XML snippet
    self.display_name_field = (AppiumBy.XPATH, "//XCUIElementTypeTextField[@value='Display Name' or @placeholderValue='Display Name']")

    # --- Methods ---

    def click_done(self):
        """Clicks the Done button to save changes."""
        self.wait.until(EC.element_to_be_clickable(self.done_button)).click()

    def change_profile_icon(self):
        """Clicks the Choose Icon button."""
        self.wait.until(EC.element_to_be_clickable(self.choose_icon_button)).click()

    def set_display_name(self, name):
        """Clears and sets a new display name."""
        field = self.wait.until(EC.presence_of_element_located(self.display_name_field))
        field.clear()
        field.send_keys(name)

    def get_current_display_name(self):
        """Returns the current value of the display name field."""
        return self.wait.until(EC.presence_of_element_located(self.display_name_field)).get_attribute("value")