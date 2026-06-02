from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPageHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    logo_image = (AppiumBy.ACCESSIBILITY_ID, "rvLogoGreen")
    welcome_slogan_text = (AppiumBy.ACCESSIBILITY_ID, "Your date with destiny awaits")
    create_new_account_button = (AppiumBy.ACCESSIBILITY_ID, "Create new account")
    already_have_account_button = (AppiumBy.ACCESSIBILITY_ID, "I already have an account")
    continue_with_apple_button = (AppiumBy.ACCESSIBILITY_ID, "Continue with Apple")
    continue_with_google_button = (AppiumBy.ACCESSIBILITY_ID, "Continue with Google")
    login_with_code_button = (AppiumBy.ACCESSIBILITY_ID, "Log in with code")
    skip_authentication_button = (AppiumBy.ACCESSIBILITY_ID, "Skip")
    email_input_field = (AppiumBy.XPATH, "//XCUIElementTypeTextField[@placeholderValue='Email']")
    password_input_field = (AppiumBy.CLASS_NAME, "XCUIElementTypeSecureTextField")
    sign_in_button = (AppiumBy.ACCESSIBILITY_ID, "Sign In")

    def verify_login_page_is_displayed(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.logo_image)).is_displayed()
        except Exception:
            return False

    def click_create_new_account(self):
        self.wait.until(EC.element_to_be_clickable(self.create_new_account_button)).click()

    def click_i_already_have_an_account(self):
        self.wait.until(EC.element_to_be_clickable(self.already_have_account_button)).click()

    def click_continue_with_google(self):
        google_button = self.wait.until(EC.element_to_be_clickable(self.continue_with_google_button))
        self.driver.execute_script('mobile: tap', {'element': google_button.id, 'x': 10, 'y': 10})

    def click_login_with_code(self):
        self.wait.until(EC.element_to_be_clickable(self.login_with_code_button)).click()

    def click_skip_authentication(self):
        self.wait.until(EC.element_to_be_clickable(self.skip_authentication_button)).click()

    def verify_sign_in_page_is_displayed(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.sign_in_button)).is_displayed()
        except Exception:
            return False

    def enter_email(self, email_text):
        field = self.wait.until(EC.element_to_be_clickable(self.email_input_field))
        field.click()
        field.clear()
        field.send_keys(email_text)

    def enter_password(self, password_text):
        field = self.wait.until(EC.element_to_be_clickable(self.password_input_field))
        field.click()
        field.clear()
        field.send_keys(password_text)

    def click_sign_in(self):
        sign_in = self.wait.until(EC.element_to_be_clickable(self.sign_in_button))
        sign_in.click()

    def login_with_credentials(self, email_text, password_text):
        self.click_i_already_have_an_account()
        self.verify_sign_in_page_is_displayed()
        self.enter_email(email_text)
        self.enter_password(password_text + "\n")
        if self.driver.is_keyboard_shown():
            self.driver.hide_keyboard()

class WelcomeToQuestHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    trophy_icon_image = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
    welcome_header_text = (AppiumBy.ACCESSIBILITY_ID, "Welcome to automation2!")
    guest_onboarding_description_text = (AppiumBy.ACCESSIBILITY_ID,
                                         "Let's get you set up with a temporary guest profile so you can join the fun. You can create a full account later to save your progress.")
    lets_go_button = (AppiumBy.ACCESSIBILITY_ID, "Let's Go")
    close_modal_button = (AppiumBy.ACCESSIBILITY_ID, "xmark.circle.fill")

    def verify_welcome_modal_is_displayed(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.welcome_header_text)).is_displayed()
        except Exception:
            return False

    def click_lets_go(self):
        self.wait.until(EC.element_to_be_clickable(self.lets_go_button)).click()

    def click_close_modal(self):
        self.wait.until(EC.element_to_be_clickable(self.close_modal_button)).click()

    def get_welcome_message(self):
        return self.wait.until(EC.presence_of_element_located(self.welcome_header_text)).text


class ChooseUsernameHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    trophy_icon_image = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
    choose_username_header_text = (AppiumBy.ACCESSIBILITY_ID, "Choose a Username")
    leaderboard_description_text = (AppiumBy.ACCESSIBILITY_ID, "This will be your name on the quest leaderboard.")
    username_input_field = (AppiumBy.CLASS_NAME, "XCUIElementTypeTextField")
    join_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Join Quest")
    close_modal_button = (AppiumBy.ACCESSIBILITY_ID, "xmark.circle.fill")

    def verify_choose_username_page_is_displayed(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.choose_username_header_text)).is_displayed()
        except Exception:
            return False

    def enter_username(self, username_text):
        field = self.wait.until(EC.element_to_be_clickable(self.username_input_field))
        field.click()
        field.send_keys(username_text + "\n")
        if self.driver.is_keyboard_shown():
            self.driver.hide_keyboard()

    def click_join_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.join_quest_button)).click()

    def click_close_modal(self):
        self.wait.until(EC.element_to_be_clickable(self.close_modal_button)).click()

    def is_join_button_enabled(self):
        return self.driver.find_element(*self.join_quest_button).is_enabled()


class StartAdventureHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    trophy_icon_image = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
    quest_title_text = (AppiumBy.ACCESSIBILITY_ID, "automation2")
    adventure_welcome_message_text = (AppiumBy.ACCESSIBILITY_ID, "Time to start your adventure!")
    start_adventure_button = (AppiumBy.ACCESSIBILITY_ID, "Start Adventure!")
    close_modal_button = (AppiumBy.ACCESSIBILITY_ID, "xmark.circle.fill")

    def verify_start_adventure_page_is_displayed(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.start_adventure_button)).is_displayed()
        except Exception:
            return False

    def click_start_adventure(self):
        self.wait.until(EC.element_to_be_clickable(self.start_adventure_button)).click()

    def click_close_modal(self):
        self.wait.until(EC.element_to_be_clickable(self.close_modal_button)).click()

    def get_quest_title(self):
        return self.wait.until(EC.presence_of_element_located(self.quest_title_text)).text
