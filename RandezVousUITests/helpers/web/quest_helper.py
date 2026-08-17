from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class QuestHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        self.quest_code_input_locator = (By.ID, "quest-code")
        self.find_quest_button_locator = (By.XPATH, "//button[@type='submit' and contains(text(), 'Find Quest')]")
        self.trivia_activity_locator = (By.XPATH, "//h4[normalize-space()='Trivia Activity']")
        self.complete_trivia_button = (By.XPATH, "//button[@aria-label='Complete Trivia Activity']")
        self.text_box = (By.XPATH, "//textarea[@aria-label='Your response']")
        self.complete_activity_button = (By.XPATH, "//button[normalize-space()='Complete Activity']")

    def enter_quest_code(self, code):
        """Waits for the input field to be clickable, clears it, and types the code."""
        input_field = self.wait.until(EC.element_to_be_clickable(self.quest_code_input_locator))
        input_field.clear()
        input_field.send_keys(code)

    def click_find_quest(self):
        """Waits for the Find Quest submit button to be clickable, then clicks it."""
        self.is_find_quest_button_enabled()
        button = self.wait.until(EC.element_to_be_clickable(self.find_quest_button_locator))
        button.click()

    def is_find_quest_button_enabled(self):
        """Checks if the button is enabled (useful since it starts disabled)."""
        button = self.wait.until(EC.visibility_of_element_located(self.find_quest_button_locator))
        return button.is_enabled()

    def complete_trivia_activity(self, response):
        print("click and complete trivia activity")
        self.wait.until(EC.element_to_be_clickable(self.trivia_activity_locator)).click()
        self.wait.until(EC.element_to_be_clickable(self.complete_trivia_button)).click()
        textarea = self.wait.until(EC.element_to_be_clickable(self.text_box))
        textarea.click()
        textarea.clear()
        textarea.send_keys(response)
        self.wait.until(EC.element_to_be_clickable(self.complete_activity_button)).click()

