from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from helpers.web.quest_helper import QuestHelper

class HomepageHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        self.find_quest_button = (By.XPATH, "//*[contains(text(), 'Find Quest')]")
        self.login_button = (By.CSS_SELECTOR, "a.bg-primary-green[href*='/login']")
        self.email_input_button = (By.XPATH, "//input[@id='auth-email']")
        self.password_input_button = (By.XPATH, "//input[@id='auth-password']")
        self.sign_in_button = (By.XPATH, "//button[@type='submit' and normalize-space()='Sign In']")
        self.guest_button = (By.XPATH, "//button[contains(normalize-space(), 'Continue as Guest')]")
        self.sign_in_save= (By.XPATH, "//a[normalize-space()='Sign In to Save Progress']")

    def find_quest(self, quest_code):
        quest_helper = QuestHelper(self.driver)

        self.click_find_quest()
        quest_helper.enter_quest_code(quest_code)
        quest_helper.click_find_quest()

    def click_find_quest(self):
        """Waits for the button to be clickable, then clicks it."""
        print("\n--- Starting find_quest ---")
        self.wait.until(EC.element_to_be_clickable(self.find_quest_button)).click()

    def click_login_button(self):
        print("Clicking login button")
        self.driver.get("http://localhost:5173/login")

    ### Joining quest from URL ###
    def click_guest_button(self):
        print("Clicking continue as guest button")
        self.wait.until(EC.element_to_be_clickable(self.guest_button)).click()

    def click_sign_in_to_save_button(self):
        print("Clicking sign in to save button")
        self.wait.until(EC.element_to_be_clickable(self.sign_in_save)).click()

    def login_from_url(self, email, password):
        self.enter_email(email)
        self.enter_password(password)
        self.click_sign_in()

    def enter_email(self, email):
        """Waits for the email to be clickable, then clicks it."""
        field = self.wait.until(EC.element_to_be_clickable(self.email_input_button))
        field.click()
        field.clear()
        field.send_keys(email)

    def enter_password(self, password):
        """Waits for the password to be clickable, then clicks it."""
        field = self.wait.until(EC.element_to_be_clickable(self.password_input_button))
        field.click()
        field.clear()
        field.send_keys(password)

    def click_sign_in(self):
        self.wait.until(EC.element_to_be_clickable(self.sign_in_button)).click()

    def login(self, email, password):
        self.click_login_button()
        self.enter_email(email)
        self.enter_password(password)
        self.click_sign_in()



