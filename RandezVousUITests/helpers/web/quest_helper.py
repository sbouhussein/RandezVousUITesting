import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from helpers.web.base_helper import BaseHelper


class QuestHelper(BaseHelper):
    quest_code_input_locator = (By.ID, "quest-code")
    find_quest_button_locator = (By.XPATH, "//button[@type='submit' and contains(text(), 'Find Quest')]")

    # Trivia
    trivia_activity_locator = (By.XPATH, "//h4[normalize-space()='Trivia Activity']")
    complete_trivia_button = (By.XPATH, "//button[@aria-label='Complete Trivia Activity']")
    trivia_error_message = (By.XPATH, "//p[normalize-space()='Response is incorrect.']")
    # Shown when a signed-out visitor tries to complete an activity
    sign_in_required_modal = (By.XPATH, "//*[normalize-space()='Sign in to complete this activity and track your points.']")
    # Shown on /find-quest when a signed-out visitor enters a restricted quest's code
    find_quest_sign_in_prompt = (By.XPATH, "//*[normalize-space()='Sign in to find and access your quest.']")

    # Prompt
    prompt_activity_locator = (By.XPATH, "//h4[normalize-space()='Prompt Activity']")
    complete_prompt_button = (By.XPATH, "//button[@aria-label='Complete Prompt Activity']")

    # Honor
    honor_activity_locator = (By.XPATH, "//h4[normalize-space()='Honor Code Activity']")
    complete_honor_button = (By.XPATH, "//button[@aria-label='Complete Honor Code Activity']")
    honor_code_checkbox = (By.XPATH, "//label[contains(., 'honor code')]//input[@type='checkbox']")

    # Photo
    photo_activity_locator = (By.XPATH, "//h4[normalize-space()='Photo Activity']")
    complete_photo_button = (By.XPATH, "//button[@aria-label='Complete Photo Activity']")
    file_input = (By.XPATH, "//input[@type='file']")

    # Location
    location_activity_locator = (By.XPATH, "//h4[normalize-space()='Location Activity']")
    complete_location_button = (By.XPATH, "//button[@aria-label='Complete Location Activity']")
    check_location_button = (By.XPATH, "//button[contains(., 'Check My Location')]")
    location_error_message = (By.XPATH,
                              "//div[contains(@class, 'bg-red-50') and contains(., 'Location verification failed')]")

    text_box = (By.XPATH, "//textarea[@aria-label='Your response']")
    complete_activity_button = (By.XPATH, "//button[normalize-space()='Complete Activity']")
    prompt_activity_details_button = (By.XPATH, "//button[@aria-label='View details for Prompt Activity']")
    activity_completed_indicator = (By.XPATH, "//div[contains(@class, 'bg-green-50') and normalize-space()='Activity Completed']")
    quest_completed_message = (By.XPATH, "//p[normalize-space()='Congratulations on completing your quest!']")

    def enter_quest_code(self, code):
        print("Entering quest code")
        input_field = self.wait.until(EC.element_to_be_clickable(self.quest_code_input_locator))
        input_field.clear()
        input_field.send_keys(code)

    def click_find_quest(self):
        print("Clicking Find Quest button...")
        self.wait.until(EC.element_to_be_clickable(self.find_quest_button_locator)).click()

    def open_trivia_complete_form(self):
        """Expands the Trivia accordion and presses its Complete button (for a signed-out
        visitor this raises the sign-in modal instead of the response form)."""
        self.click(self.trivia_activity_locator)
        self.click(self.complete_trivia_button)

    def is_sign_in_required_modal_visible(self):
        return self.is_visible(self.sign_in_required_modal, custom_timeout=10)

    def is_find_quest_sign_in_prompt_visible(self, custom_timeout=10):
        return self.is_visible(self.find_quest_sign_in_prompt, custom_timeout=custom_timeout)

    def complete_trivia_activity(self, response):
        print("click and complete trivia activity")
        self.open_trivia_complete_form()
        textarea = self.click(self.text_box)
        textarea.clear()
        print("Entering response")
        textarea.send_keys(response)
        self.click(self.complete_activity_button)

    def complete_prompt_activity(self, response):
        print("click and complete prompt activity")
        self.click(self.prompt_activity_locator)
        self.click(self.complete_prompt_button)
        textarea = self.click(self.text_box)
        textarea.clear()
        print("Entering response")
        textarea.send_keys(response)
        self.click(self.complete_activity_button)

    def complete_honor_activity(self):
        print("click and complete honor activity")
        self.click(self.honor_activity_locator)
        self.click(self.complete_honor_button)
        self.click(self.honor_code_checkbox)
        self.click(self.complete_activity_button)

    def complete_photo_activity(self):
        print("click and complete photo activity")
        self.click(self.photo_activity_locator)
        self.click(self.complete_photo_button)
        self.upload_photo()
        self.click(self.complete_activity_button)

    def upload_photo(self, file_name="test_image.jpg"):
        helper_dir = os.path.dirname(os.path.abspath(__file__))
        photo_path = os.path.join(helper_dir, file_name)

        if not os.path.exists(photo_path):
            raise FileNotFoundError(f"Test image not found in helper directory at: {photo_path}")

        print(f"Uploading file from: {photo_path}")
        self.driver.find_element(*self.file_input).send_keys(photo_path)

    def check_location(self):
        """Opens the Location activity and runs its location check, without completing it."""
        self.click(self.location_activity_locator)
        self.click(self.complete_location_button)
        self.click(self.check_location_button)

    def complete_location_activity(self):
        print("click and complete location activity")
        self.check_location()
        self.click(self.complete_activity_button)

    def is_location_error_visible(self):
        return self.is_visible(self.location_error_message, custom_timeout=3)

    def mock_geo_location(self, lat, long):
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
                return 999;
            }};
            """
        self.driver.execute_script(mock_location_js)

        self.driver.set_script_timeout(5)
        check_location_js = """
            var done = arguments[arguments.length - 1];
            window.navigator.geolocation.getCurrentPosition(
                function(position) {
                    done({ lat: position.coords.latitude, lng: position.coords.longitude });
                },
                function(error) {
                    done({ error: error.message });
                }
            );
            """
        reported_location = self.driver.execute_async_script(check_location_js)
        print(f"Browser reports its location as: {reported_location}")

    def complete_quest(self, trivia_response, prompt_response):
        self.complete_trivia_activity(trivia_response)
        self.complete_prompt_activity(prompt_response)
        self.complete_honor_activity()
        self.complete_photo_activity()
        self.complete_location_activity()

    def verify_quest_completion(self):
        """Waits for the completion banner (auto-finish fires ~2.5s after
        requirements are met, so give it more room than the default wait)."""
        print("Verifying the quest is complete")
        return self.is_visible(self.quest_completed_message, custom_timeout=15)

    def verify_activity_completion(self, activity_name):
        print(f"Clicking details for activity: {activity_name}")
        dynamic_locator = (By.XPATH, f"//button[@aria-label='View details for {activity_name} Activity']")
        self.click(dynamic_locator)
        print("Verifying Activity Completion")
        result = self.is_visible(self.activity_completed_indicator, custom_timeout=3)
        # "View details" is its own sub-route; go back for whatever's checked next. Best-effort:
        # after the quest's last activity the completion screen may cover the page.
        self.driver.back()
        self.is_visible(dynamic_locator, custom_timeout=5)
        return result

    def is_trivia_error_visible(self):
        return self.is_visible(self.trivia_error_message, custom_timeout=3)

