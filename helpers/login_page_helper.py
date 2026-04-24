from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPageHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # --- Element Locators (Full Word Formatting) ---
    logo_image = (AppiumBy.ACCESSIBILITY_ID, "rvLogoGreen")
    welcome_slogan_text = (AppiumBy.ACCESSIBILITY_ID, "Your date with destiny awaits")

    create_new_account_button = (AppiumBy.ACCESSIBILITY_ID, "Create new account")
    already_have_account_button = (AppiumBy.ACCESSIBILITY_ID, "I already have an account")

    continue_with_apple_button = (AppiumBy.ACCESSIBILITY_ID, "Continue with Apple")
    continue_with_google_button = (AppiumBy.ACCESSIBILITY_ID, "Continue with Google")

    login_with_code_button = (AppiumBy.ACCESSIBILITY_ID, "Log in with code")
    skip_authentication_button = (AppiumBy.ACCESSIBILITY_ID, "Skip")

    # --- Actions ---
    def verify_login_page_is_displayed(self):
        """Checks if the RandezVous logo is visible on the screen."""
        try:
            element = self.wait.until(EC.visibility_of_element_located(self.logo_image))
            return element.is_displayed()
        except Exception:
            return False

    def click_create_new_account(self):
        self.wait.until(EC.element_to_be_clickable(self.create_new_account_button)).click()

    def click_i_already_have_an_account(self):
        self.wait.until(EC.element_to_be_clickable(self.already_have_account_button)).click()

    def click_continue_with_google(self):
        """Uses a native tap to handle the nested Google login button."""
        google_button = self.wait.until(EC.element_to_be_clickable(self.continue_with_google_button))
        self.driver.execute_script('mobile: tap', {
            'element': google_button.id,
            'x': 10,
            'y': 10
        })

    def click_login_with_code(self):
        self.wait.until(EC.element_to_be_clickable(self.login_with_code_button)).click()

    def click_skip_authentication(self):
        """Clicks the Skip button to bypass login."""
        self.wait.until(EC.element_to_be_clickable(self.skip_authentication_button)).click()

class WelcomeToQuestHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # --- Element Locators (Full Word Formatting) ---
    trophy_icon_image = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
    welcome_header_text = (AppiumBy.ACCESSIBILITY_ID, "Welcome to automation2!")
    guest_onboarding_description_text = (AppiumBy.ACCESSIBILITY_ID,
                                         "Let's get you set up with a temporary guest profile so you can join the fun. You can create a full account later to save your progress.")

    lets_go_button = (AppiumBy.ACCESSIBILITY_ID, "Let's Go")
    close_modal_button = (AppiumBy.ACCESSIBILITY_ID, "xmark.circle.fill")

    # --- Actions ---
    def verify_welcome_modal_is_displayed(self):
        """Checks if the Welcome onboarding screen is visible."""
        try:
            # We use the header text as the anchor for visibility
            element = self.wait.until(EC.visibility_of_element_located(self.welcome_header_text))
            return element.is_displayed()
        except Exception:
            return False

    def click_lets_go(self):
        """Proceeds past the guest setup introduction."""
        element = self.wait.until(EC.element_to_be_clickable(self.lets_go_button))
        element.click()

    def click_close_modal(self):
        """Closes the welcome screen using the X button."""
        self.wait.until(EC.element_to_be_clickable(self.close_modal_button)).click()

    def get_welcome_message(self):
        """Returns the text of the welcome header (useful for assertions)."""
        element = self.wait.until(EC.presence_of_element_located(self.welcome_header_text))
        return element.text

class ChooseUsernameHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # --- Element Locators (Full Word Formatting) ---
    trophy_icon_image = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
    choose_username_header_text = (AppiumBy.ACCESSIBILITY_ID, "Choose a Username")
    leaderboard_description_text = (AppiumBy.ACCESSIBILITY_ID, "This will be your name on the quest leaderboard.")

    username_input_field = (AppiumBy.CLASS_NAME, "XCUIElementTypeTextField")
    join_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Join Quest")
    close_modal_button = (AppiumBy.ACCESSIBILITY_ID, "xmark.circle.fill")

    # --- Actions ---
    def verify_choose_username_page_is_displayed(self):
        """Verifies the header text is visible to confirm we are on the right screen."""
        try:
            return self.wait.until(EC.visibility_of_element_located(self.choose_username_header_text)).is_displayed()
        except Exception:
            return False

    def enter_username(self, username_text):
        """Clicks the field and types the desired username."""
        field = self.wait.until(EC.element_to_be_clickable(self.username_input_field))
        field.click()
        field.send_keys(username_text + "\n")  # Adding \n usually dismisses the keyboard

        # Hide keyboard if it blocks the Join button (common in iOS)
        if self.driver.is_keyboard_shown():
            self.driver.hide_keyboard()

    def click_join_quest(self):
        """Clicks Join Quest. Note: XML shows this is disabled until text is entered."""
        element = self.wait.until(EC.element_to_be_clickable(self.join_quest_button))
        element.click()

    def click_close_modal(self):
        """Closes the username selection screen."""
        self.wait.until(EC.element_to_be_clickable(self.close_modal_button)).click()

    def is_join_button_enabled(self):
        """Checks if the Join Quest button has become active after typing."""
        button = self.driver.find_element(*self.join_quest_button)
        return button.is_enabled()

class StartAdventureHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # --- Element Locators (Full Word Formatting) ---
    trophy_icon_image = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
    quest_title_text = (AppiumBy.ACCESSIBILITY_ID, "automation2")
    adventure_welcome_message_text = (AppiumBy.ACCESSIBILITY_ID, "Time to start your adventure!")

    start_adventure_button = (AppiumBy.ACCESSIBILITY_ID, "Start Adventure!")
    close_modal_button = (AppiumBy.ACCESSIBILITY_ID, "xmark.circle.fill")

    # --- Actions ---
    def verify_start_adventure_page_is_displayed(self):
        """Checks if the 'Start Adventure!' button is visible to confirm the screen."""
        try:
            element = self.wait.until(EC.visibility_of_element_located(self.start_adventure_button))
            return element.is_displayed()
        except Exception:
            return False

    def click_start_adventure(self):
        """Clicks the final button to officially begin the quest adventure."""
        self.wait.until(EC.element_to_be_clickable(self.start_adventure_button)).click()

    def click_close_modal(self):
        """Closes the start adventure screen."""
        self.wait.until(EC.element_to_be_clickable(self.close_modal_button)).click()

    def get_quest_title(self):
        """Retrieves the name of the quest displayed on the start screen."""
        element = self.wait.until(EC.presence_of_element_located(self.quest_title_text))
        return element.text