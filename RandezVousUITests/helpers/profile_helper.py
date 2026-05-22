from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProfileHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    profile_tab = (AppiumBy.ACCESSIBILITY_ID, "person")
    show_menu_button = (AppiumBy.ACCESSIBILITY_ID, "Show Menu")
    logout_button = (AppiumBy.ACCESSIBILITY_ID, "Log out")

    def navigate_to_profile(self):
        self.wait.until(EC.element_to_be_clickable(self.profile_tab)).click()

    def sign_out_if_logged_in(self):
        """Checks if a user is logged in and signs them out to clean the state"""
        try:
            self.navigate_to_profile()
            menu=self.wait.until(EC.element_to_be_clickable(self.show_menu_button))
            menu.click()
            sign_out = self.wait.until(EC.element_to_be_clickable(self.logout_button))
            sign_out.click()
            sign_out.click()
            print("User signed out successfully.")
        except:
            print("No active session found or already signed out.")