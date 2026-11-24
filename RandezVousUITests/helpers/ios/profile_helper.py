from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ProfileHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    profile_header_locator = (AppiumBy.ACCESSIBILITY_ID, "Profile")
    profile_tab = (AppiumBy.ACCESSIBILITY_ID, "person")
    show_menu_button = (AppiumBy.ACCESSIBILITY_ID, "Show Menu")
    logout_button = (AppiumBy.ACCESSIBILITY_ID, "Log out")

    profile_tab_label = (AppiumBy.IOS_PREDICATE, 'label == "Profile" AND type == "XCUIElementTypeButton"')

    def navigate_to_profile(self):
        # The tab bar sometimes exposes the icon id late; its "Profile" label is the fallback.
        def visible_tab(driver):
            for locator in (self.profile_tab, self.profile_tab_label):
                found = driver.find_elements(*locator)
                if found and found[0].is_displayed():
                    return found[0]
            return False
        WebDriverWait(self.driver, 20).until(visible_tab).click()

    def test_dynamic_score(self, expected_score):
        """Asserts the profile shows `expected_score`."""
        expected_score_str = str(expected_score)
        score_locator = (AppiumBy.XPATH, '(//XCUIElementTypeStaticText[@name="score"]/../*)[3]')
        score_element = self.wait.until(EC.visibility_of_element_located(score_locator))
        actual_score = score_element.text
        print(f"Users score is {actual_score}")
        assert actual_score == expected_score_str, f"Expected score {expected_score_str}, but got {actual_score}"

    def log_out_if_logged_in(self, check_score=False, expected_score=None):
        """Signs the user out from the profile menu, scrolling to the Log out button if needed."""
        self.navigate_to_profile()
        if check_score:
            self.test_dynamic_score(expected_score)

        menu = self.wait.until(EC.element_to_be_clickable(self.show_menu_button))
        menu.click()

        try:
            log_out = self.driver.find_element(*self.logout_button)
            if not log_out.is_displayed():
                raise Exception("Not visible")
        except Exception:
            print("Logout button not visible, scrolling to find it...")
            self.driver.execute_script('mobile: scroll', {
                'direction': 'down',
                'element': self.driver.find_element(AppiumBy.CLASS_NAME, "XCUIElementTypeCollectionView").id,
                'predicateString': 'label == "Log out"'
            })

        log_out = self.wait.until(EC.element_to_be_clickable(self.logout_button))
        log_out.click()

        # The driver's autoAcceptAlerts may confirm the dialog before we see it.
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except (TimeoutException, NoAlertPresentException):
            pass
        self.wait.until(EC.invisibility_of_element_located(self.show_menu_button))
        print("User logged out successfully.")