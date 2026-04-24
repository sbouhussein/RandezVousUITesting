from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProfileHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    # --- Locators ---
    profile_tab = (AppiumBy.ACCESSIBILITY_ID, " Profile ")
    # Using the name from your XML (oalson) as the header indicator
    profile_header = (AppiumBy.ACCESSIBILITY_ID, "oalson")
    # Usually, sign out is at the bottom or behind a settings icon
    # Based on standard iOS patterns for the "square.and.arrow.up" context:
    sign_out_button = (AppiumBy.ACCESSIBILITY_ID, "Sign Out")

    def navigate_to_profile(self):
        self.wait.until(EC.element_to_be_clickable(self.profile_tab)).click()

    def sign_out_if_logged_in(self):
        """Checks if a user is logged in and signs them out to clean the state"""
        try:
            self.navigate_to_profile()
            # If sign out button exists, click it
            sign_out = self.wait.until(EC.element_to_be_clickable(self.sign_out_button))
            sign_out.click()
            print("✅ User signed out successfully.")
        except:
            print("ℹ️ No active session found or already signed out.")