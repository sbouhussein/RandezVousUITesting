from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class QuestHelper:
    def __init__(self, driver):
        self.driver = driver

        self.quest_code_input_locator = (By.ID, "quest-code")
        self.find_quest_button_locator = (By.XPATH, "//button[@type='submit' and contains(text(), 'Find Quest')]")

    def enter_quest_code(self, code):
        """Waits for the input field to be clickable, clears it, and types the code."""
        wait = WebDriverWait(self.driver, 10)
        input_field = wait.until(EC.element_to_be_clickable(self.quest_code_input_locator))
        input_field.clear()
        input_field.send_keys(code)

    def click_find_quest(self):
        """Waits for the Find Quest submit button to be clickable, then clicks it."""
        self.is_find_quest_button_enabled()
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(EC.element_to_be_clickable(self.find_quest_button_locator))
        button.click()

    def is_find_quest_button_enabled(self):
        """Checks if the button is enabled (useful since it starts disabled)."""
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(EC.visibility_of_element_located(self.find_quest_button_locator))
        return button.is_enabled()