import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.web.base_helper import BaseHelper

class QuestHelper(BaseHelper):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        self.quest_code_input_locator = (By.ID, "quest-code")
        self.find_quest_button_locator = (By.XPATH, "//button[@type='submit' and contains(text(), 'Find Quest')]")
        #Trivia
        self.trivia_activity_locator = (By.XPATH, "//h4[normalize-space()='Trivia Activity']")
        self.complete_trivia_button = (By.XPATH, "//button[@aria-label='Complete Trivia Activity']")
        self.trivia_activity_locator = (By.XPATH, "//h4[normalize-space()='Trivia Activity']")
        self.complete_trivia_button = (By.XPATH, "//button[@aria-label='Complete Trivia Activity']")
        self.trivia_error_message = (By.XPATH, "//p[normalize-space()='Response is incorrect.']")
        #Prompt
        self.prompt_activity_locator = (By.XPATH, "//h4[normalize-space()='Prompt Activity']")
        self.complete_prompt_button = (By.XPATH, "//button[@aria-label='Complete Prompt Activity']")
        #Honor
        self.honor_activity_locator = (By.XPATH, "//h4[normalize-space()='Honor Code Activity']")
        self.complete_honor_button = (By.XPATH, "//button[@aria-label='Complete Honor Code Activity']")
        self.honor_code_checkbox = (By.XPATH, "//label[contains(., 'honor code')]//input[@type='checkbox']")
        #Photo
        self.photo_activity_locator = (By.XPATH, "//h4[normalize-space()='Photo Activity']")
        self.complete_photo_button = (By.XPATH, "//button[@aria-label='Complete Photo Activity']")
        #Location
        self.location_activity_locator = (By.XPATH, "//h4[normalize-space()='Location Activity']")
        self.complete_location_button = (By.XPATH, "//button[@aria-label='Complete Location Activity']")
        self.check_location_button = (By.XPATH, "//button[contains(., 'Check My Location')]")
        self.location_error_message = (By.XPATH,
                                  "//div[contains(@class, 'bg-red-50') and contains(., 'Location verification failed')]")

        self.text_box = (By.XPATH, "//textarea[@aria-label='Your response']")
        self.complete_activity_button = (By.XPATH, "//button[normalize-space()='Complete Activity']")
        self.prompt_activity_details_button = (By.XPATH, "//button[@aria-label='View details for Prompt Activity']")
        self.activity_completed_indicator = (By.XPATH,"//div[contains(@class, 'bg-green-50') and normalize-space()='Activity Completed']")

    def enter_quest_code(self, code):
        """Waits for the input field to be clickable, clears it, and types the code."""
        print("Entering quest code")
        input_field = self.wait.until(EC.element_to_be_clickable(self.quest_code_input_locator))
        input_field.clear()
        input_field.send_keys(code)

    def click_find_quest(self):
        """Waits for the Find Quest submit button to be clickable, then clicks it."""
        print("Clicking Find Quest button...")
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
        print("Entering response")
        textarea.send_keys(response)
        self.wait.until(EC.element_to_be_clickable(self.complete_activity_button)).click()

    def complete_prompt_activity(self, response):
        print("click and complete prompt activity")
        self.click(self.prompt_activity_locator)
        self.click(self.complete_prompt_button)
        textarea = self.click(self.text_box)
        textarea.click()
        textarea.clear()
        print("Entering response")
        textarea.send_keys(response)
        self.wait.until(EC.element_to_be_clickable(self.complete_activity_button)).click()

    def complete_honor_activity(self):
        print("click and complete honor activity")
        self.click(self.honor_activity_locator)
        self.click(self.complete_honor_button)
        self.click(self.honor_code_checkbox)
        self.wait.until(EC.element_to_be_clickable(self.complete_activity_button)).click()

    def complete_photo_activity(self):
        print("click and complete photo activity")
        self.click(self.photo_activity_locator)
        self.click(self.complete_photo_button)
        self.upload_photo()
        self.wait.until(EC.element_to_be_clickable(self.complete_activity_button)).click()

    def upload_photo(self, file_name="test_image.jpg"):

        helper_dir = os.path.dirname(os.path.abspath(__file__))
        photo_path = os.path.join(helper_dir, file_name)

        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"Test image not found in helper directory at: {photo_path}")

        print(f"Uploading file from: {photo_path}")
        file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(photo_path)

    def complete_location_activity(self, fail_check = False):
        print("click and complete location activity")
        self.click(self.location_activity_locator)
        print("here")
        self.click(self.complete_location_button)
        print("here2")
        self.click(self.check_location_button)
        print("here3")

        if fail_check:
            print("Fail check")
            assert self.is_visible(self.location_error_message, custom_timeout=3)

        else:
            self.wait.until(EC.element_to_be_clickable(self.complete_activity_button)).click()

    def mock_geo_location(self, dv, lat, long):
        mock_location_js = f"""
            const mockPosition = {{
                coords: {{
                    latitude: {lat},
                    longitude: {long},
                    altitude: null,
                    accuracy: 10,
                    altitudeAccuracy: null,
                    heading: null,
                    speed: null
                }},
                timestamp: Date.now()
            }};

            window.navigator.geolocation.getCurrentPosition = function(success, error, options) {{
                success(mockPosition);
            }};

            window.navigator.geolocation.watchPosition = function(success, error, options) {{
                success(mockPosition);
                return 999; // Mock watch ID
            }};
            """

        dv.execute_script(mock_location_js)

        print("Checking what Safari thinks its location is...")
        dv.set_script_timeout(5)

        check_location_js = """
            // Selenium automatically provides a callback function as the last argument
            var seleniumCallback = arguments[arguments.length - 1]; 

            window.navigator.geolocation.getCurrentPosition(
                function(position) {
                    // Return the coordinates to Python
                    seleniumCallback({ 
                        lat: position.coords.latitude, 
                        lng: position.coords.longitude 
                    });
                }, 
                function(error) {
                    seleniumCallback({ error: error.message });
                }
            );
            """

        reported_location = dv.execute_async_script(check_location_js)
        print(f"Safari reported its location to the app as: {reported_location}")

    def complete_quest(self, trivia_response, prompt_response):
        self.complete_trivia_activity(trivia_response)
        self.complete_prompt_activity(prompt_response)
        self.complete_honor_activity()
        self.complete_photo_activity()
        self.complete_location_activity()

    def verify_quest_completion(self):
        print("Verifying the quest is complete")

    def verify_activity_completion(self, activity_name):
        print(f"Clicking details for activity: {activity_name}")
        dynamic_locator = (By.XPATH, f"//button[@aria-label='View details for {activity_name} Activity']")
        self.click(dynamic_locator)
        print("Verifying Activity Completion")
        return self.is_visible(self.activity_completed_indicator, custom_timeout=3)

    def is_trivia_error_visible(self):
        return self.is_visible(self.trivia_error_message, custom_timeout=3)

