from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD


class HomepageHelper:
    find_quest_button = (By.XPATH, "//*[contains(text(), 'Find Quest')]")
    login_button = (By.CSS_SELECTOR, "a.bg-primary-green[href*='/login']")
    route_spinner = (By.CSS_SELECTOR, ".animate-spin")
    email_input_button = (By.XPATH, "//input[@id='auth-email']")
    password_input_button = (By.XPATH, "//input[@id='auth-password']")
    sign_in_button = (By.XPATH, "//button[@type='submit' and normalize-space()='Sign In']")
    auth_network_error = (By.XPATH, "//*[contains(normalize-space(), 'auth/network-request-failed')]")
    guest_button = (By.XPATH, "//button[contains(normalize-space(), 'Continue as Guest')]")
    sign_in_save = (By.XPATH, "//a[normalize-space()='Sign In to Save Progress']")

    def __init__(self, driver):
        self.driver = driver
        # /login's first paint after a fresh Vite start can take well over 10s.
        self.wait = WebDriverWait(self.driver, 30)

    def find_quest(self, quest_code):
        quest_helper = QuestHelper(self.driver)

        self.click_find_quest()
        quest_helper.enter_quest_code(quest_code)
        quest_helper.click_find_quest()

    def click_find_quest(self):
        print("Clicking Find Quest")
        self.wait.until(EC.element_to_be_clickable(self.find_quest_button)).click()

    def click_login_button(self):
        print("Opening the login page")
        self.driver.get(f"{BASE_URL}/login")
        self._wait_for_login_form()

    def _wait_for_login_form(self):
        """Waits out the route spinner, then for the auth form. #auth-email isn't in the DOM until
        React Router hydrates LoginPage and useAuth() resolves."""
        print("Waiting for login form to finish loading...")
        try:
            self.wait.until(EC.invisibility_of_element_located(self.route_spinner))
        except TimeoutException:
            print("Route spinner still visible; looking for the form anyway.")
        self.wait.until(EC.element_to_be_clickable(self.email_input_button))

    def click_guest_button(self):
        print("Clicking continue as guest button")
        self.wait.until(EC.element_to_be_clickable(self.guest_button)).click()

    def click_sign_in_to_save_button(self):
        print("Clicking sign in to save button")
        self.wait.until(EC.element_to_be_clickable(self.sign_in_save)).click()

    def login_from_url(self, email, password):
        # Typing before LoginPage mounts intermittently loses the input or the Sign In click.
        self._wait_for_login_form()
        self._submit_credentials(email, password)

    def _submit_credentials(self, email, password, attempts=3, settle_timeout=15):
        """Submits the sign-in form, retrying Firebase's intermittent sign-in stall: the page stays
        on /login with no error (or eventually `auth/network-request-failed`), and the SDK stays
        broken until a reload. Returns once the page leaves /login, or after the last attempt;
        callers decide what a stuck sign-in means."""
        for attempt in range(1, attempts + 1):
            self.enter_email(email)
            self.enter_password(password)
            self.click_sign_in()
            try:
                WebDriverWait(self.driver, settle_timeout).until(
                    lambda d: "/login" not in d.current_url or d.find_elements(*self.auth_network_error))
            except TimeoutException:
                pass
            if "/login" not in self.driver.current_url:
                return
            if attempt == attempts:
                print(f"Sign-in still stuck on /login after {attempts} attempts: {self._login_page_state()}")
                return
            print(f"Sign-in stalled on /login (attempt {attempt}/{attempts}: {self._login_page_state()}); reloading and retrying...")
            self.driver.refresh()
            self._wait_for_login_form()

    def _login_page_state(self):
        """Summary of the login page for diagnosing a stuck sign-in. Never includes the password."""
        try:
            alerts = [e.text for e in self.driver.find_elements(
                By.XPATH, "//*[@role='alert' or contains(@class,'red-') or contains(@class,'error')]") if e.text.strip()]
            fields = {e.get_attribute("id"): bool(e.get_attribute("value"))
                      for e in self.driver.find_elements(By.XPATH, "//input[@id='auth-email' or @id='auth-password']")}
            heading = [h.text for h in self.driver.find_elements(By.XPATH, "//h1|//h2") if h.text.strip()][:2]
            return f"url={self.driver.current_url} headings={heading} filled={fields} alerts={alerts[:3]}"
        except Exception as e:
            return f"(couldn't read login page state: {e})"

    def enter_email(self, email):
        field = self.wait.until(EC.element_to_be_clickable(self.email_input_button))
        field.click()
        field.clear()
        field.send_keys(email)

    def enter_password(self, password):
        field = self.wait.until(EC.element_to_be_clickable(self.password_input_button))
        field.click()
        field.clear()
        field.send_keys(password)

    def click_sign_in(self):
        self.wait.until(EC.element_to_be_clickable(self.sign_in_button)).click()

    def login(self, email, password):
        self.click_login_button()
        self._submit_credentials(email, password)

    def sign_in_and_find_quest(self, quest_code, email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD):
        self.login(email, password)
        self.find_quest(quest_code)

    def sign_in_and_open(self, url, email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD):
        """Signs in, waits until the app treats the session as signed in, then opens `url`."""
        self.login(email, password)
        self.wait_until_signed_in()
        self.driver.get(url)

    def wait_until_signed_in(self):
        """Waits for LoginPage's post-sign-in redirect."""
        self.wait.until(lambda d: "/login" not in d.current_url)

