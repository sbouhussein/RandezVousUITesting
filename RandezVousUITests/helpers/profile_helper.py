import time
from lib2to3.pgen2 import driver

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.login_page_helper import LoginPageHelper

class ProfileHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    login_page = LoginPageHelper(driver)

    profile_header_locator = (AppiumBy.ACCESSIBILITY_ID, "Profile")
    profile_tab = (AppiumBy.ACCESSIBILITY_ID, "person")
    show_menu_button = (AppiumBy.ACCESSIBILITY_ID, "Show Menu")
    logout_button = (AppiumBy.ACCESSIBILITY_ID, "Log out")

    def navigate_to_profile(self):
        self.wait.until(EC.element_to_be_clickable(self.profile_tab)).click()

    def test_dynamic_score(self, expected_score):
        """""Checks that users score is equal to a certain score"""
        expected_score_str = str(expected_score)
        score_locator = (AppiumBy.XPATH, '(//XCUIElementTypeStaticText[@name="score"]/../*)[3]')
        score_element = self.wait.until(EC.visibility_of_element_located(score_locator))
        actual_score = score_element.text
        print(f"Users score is {actual_score}")
        assert actual_score == expected_score_str, f"Expected score to be 125, but got {actual_score}"

    def log_out_if_logged_in(self, check_score = False, expected_score = None):
        """Checks if a user is logged in and signs them out to clean the state"""
        self.navigate_to_profile()
        if check_score:
            self.test_dynamic_score(expected_score)
        menu=self.wait.until(EC.element_to_be_clickable(self.show_menu_button))
        menu.click()
        log_out = self.wait.until(EC.element_to_be_clickable(self.logout_button))
        log_out.click()
        self.wait.until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()
        time.sleep(2)
        print("User logged out successfully.")