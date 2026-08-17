from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.ios.base_helper import BaseHelper
from helpers.ios.login_page_helper import LoginPageHelper
from helpers.ios.profile_helper import ProfileHelper


class QuestHelper(BaseHelper, LoginPageHelper, ProfileHelper):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    # Tab Bar
    quests_tab = (AppiumBy.ACCESSIBILITY_ID, "scroll.fill")
    home_tab = (AppiumBy.ACCESSIBILITY_ID, "house")
    explore_tab = (AppiumBy.ACCESSIBILITY_ID, " Explore ")
    participants_tab = (AppiumBy.ACCESSIBILITY_ID, " Participants ")
    #profile_tab = (AppiumBy.ACCESSIBILITY_ID, " Profile ")

    # Quests Page
    quests_header = (AppiumBy.ACCESSIBILITY_ID, "Quests")
    leaderboard_button = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
    active_badge = (AppiumBy.ACCESSIBILITY_ID, "Active")
    custom_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Custom")
    join_quest_page = (AppiumBy.ACCESSIBILITY_ID, "Join a Quest")
    tab_bar = (AppiumBy.XPATH,'//XCUIElementTypeTabBar[@name="Tab Bar"]/XCUIElementTypeOther/XCUIElementTypeOther[2]')
    sign_in_prompt = (AppiumBy.ACCESSIBILITY_ID,
        (
            "Create an account or sign back in to customize your profile and get"
            " activities personalized just for you."
        ),
                      )

    def navigate_to_quests_tab(self):
        print("Navigating to Quests Tab")
        self.wait.until(EC.element_to_be_clickable(self.quests_tab)).click()
        assert self.wait.until(EC.visibility_of_element_located(self.quests_header)).is_displayed(), \
            "Quests page header not visible after clicking tab"

    def click_custom_quest_button(self):
        self.wait.until(EC.element_to_be_clickable(self.custom_quest_button)).click()
        assert self.wait.until(EC.visibility_of_element_located(self.join_quest_page)).is_displayed(), \
            "Custom Quest overlay did not appear"

    def get_quest_title(self):
        return self.wait.until(EC.presence_of_element_located(self.quest_title)).text

    def is_active(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.active_badge)).is_displayed()
        except Exception:
            return False

    def click_leaderboard_button(self):
        self.wait.until(EC.element_to_be_clickable(self.leaderboard_button)).click()
        print(f"Clicking LeaderBoard Button")

    def check_leaderboard(self, expected_username, expected_score):
        self.click_leaderboard_button()
        row_xpath = f'//XCUIElementTypeCell[descendant::XCUIElementTypeStaticText[@name="{expected_username}"]]'
        print(f"Searching for row belonging to user: '{expected_username}'...")

        parent_cell = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((AppiumBy.XPATH, row_xpath))
        )

        text_elements = parent_cell.find_elements(AppiumBy.CLASS_NAME, "XCUIElementTypeStaticText")
        actual_username = text_elements[0].get_attribute("name")
        actual_score = text_elements[1].get_attribute("name")

        print(f"Row Found -> Extracted User: '{actual_username}' | Extracted Score: '{actual_score}'")

        assert actual_username == expected_username, f"Username mismatch! Expected '{expected_username}' but found '{actual_username}'"
        assert actual_score == expected_score, f"Score mismatch for {expected_username}! Expected '{expected_score}' but found '{actual_score}'"

        print(f"Success! Verified score for {actual_username} matches expected value of {actual_score}.")
        self.navigate_to_quests_tab()

    def sign_out_if_signed_in(self):
        if self.is_visible(self.tab_bar):
            print("App is on Dashboard")
            self.click(self.profile_tab)

            if  self.is_visible(self.sign_in_prompt):
                print("User is on Dasahbaord. Signing in and signing out")
                self.login_and_out_to_cleanup(email_text="oalson123@gmail.com", password_text="OmarTest123")

            elif self.is_visible(self.show_menu_button):
                print("User is signed in. Signing out")
                self.log_out_if_logged_in()

        elif self.is_visible(self.login_with_code_button):
            pass

class CustomQuestPage(BaseHelper):
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    back_button = (AppiumBy.ACCESSIBILITY_ID, "BackButton")
    quest_code_input_field = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeTextField[`value == "Custom Code"`]')
    find_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Find Quest")
    clear_search_button = (AppiumBy.ACCESSIBILITY_ID, "Clear Search")
    found_quest_title_label = (AppiumBy.ACCESSIBILITY_ID, "Found a Custom Quest")
    start_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Start Quest")
    create_own_quest_link = (AppiumBy.ACCESSIBILITY_ID, "Want to create a quest of your own?")
    view_requirements_button = (AppiumBy.ACCESSIBILITY_ID, "View Requirements")
    primary_exit_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Exit Quest")
    secondary_exit_confirm_button = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeSheet/**/XCUIElementTypeButton[`name == "Exit Quest"`]')
    hide_requirements_button = (AppiumBy.ACCESSIBILITY_ID, "Hide Requirements")
    quest_title = (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeStaticText[`label == 'automation2'`][1]")
    quest_date_range = (AppiumBy.ACCESSIBILITY_ID, "March 9, 2026 - March 3, 2027")
    quest_feed_button = (AppiumBy.ACCESSIBILITY_ID, "Quest Feed, : Hello")
    check_quest_requirements = (AppiumBy.ACCESSIBILITY_ID, "View Quest Requirements")
    view_prompt = (AppiumBy.ACCESSIBILITY_ID, "View Prompt")
    prompt_text_box = (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeTextView")
    submit_response_button = (AppiumBy.ACCESSIBILITY_ID, "Submit Response")
    check_answer_button = (AppiumBy.ACCESSIBILITY_ID, "Check Answer")
    not_now_rating_button = (AppiumBy.ACCESSIBILITY_ID, "Not Now")
    dismiss_after_completing_activity = (AppiumBy.ACCESSIBILITY_ID, "PopoverDismissRegion")
    quests_nav_bar = (AppiumBy.ACCESSIBILITY_ID, "Quests")
    back_button = (AppiumBy.ACCESSIBILITY_ID, "chevron.left")
    add_to_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Add to Quest")
    completed_activity_button = (AppiumBy.ACCESSIBILITY_ID, "I've completed this activity")
    submit_photo_button = (AppiumBy.XPATH, "//XCUIElementTypeButton[contains(@label, 'Submit a Photo')]")
    complete_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Complete in Quest")
    finish_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Finish Quest")
    log_in_button = (AppiumBy.ACCESSIBILITY_ID, "Log in")
    prompt_nav_bar = (AppiumBy.ACCESSIBILITY_ID, "Prompt Activity")

    """""Universal functions"""
    def join_custom_quest(self, quest_code):
        quest_helper = QuestHelper(self.driver)

        quest_helper.navigate_to_quests_tab()
        quest_helper.click_custom_quest_button()
        self.enter_quest_code(quest_code)
        self.click_find_quest()
        self.click_start_quest()
        self.wait.until(EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Quests")))

    def enter_quest_code(self, code):
        field = self.wait.until(EC.element_to_be_clickable(self.quest_code_input_field))
        field.clear()
        field.send_keys(code)

    def click_find_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.find_quest_button)).click()

    def verify_quest_is_found(self):
        return self.wait.until(EC.visibility_of_element_located(self.found_quest_title_label)).is_displayed()

    def click_start_quest(self):
        start_btn = self.wait.until(EC.presence_of_element_located(self.start_quest_button))
        self.driver.execute_script('mobile: tap', {'element': start_btn.id, 'x': 10, 'y': 10})

    def click_clear_search(self):
        self.wait.until(EC.element_to_be_clickable(self.clear_search_button)).click()

    def click_trivia_activity(self, activity, max_swipes=5):
        locator = (AppiumBy.IOS_PREDICATE, f'name CONTAINS "{activity}"')

        for i in range(max_swipes):
            try:
                element = self.wait.until(EC.element_to_be_clickable(locator))

                try:
                    element.click()
                    print(f"Clicked '{activity}' successfully.")
                    return  # We are done!
                except:
                    print("Click failed, scrolling to center element...")
                    scroll_view = self.driver.find_element(AppiumBy.CLASS_NAME, "XCUIElementTypeScrollView")
                    self.driver.execute_script('mobile: scroll',
                                               {'direction': 'right', 'element': scroll_view.id, 'toVisible': True})
                    element.click()
                    return

            except TimeoutException:
                print(f"Activity not found. Scrolling... ({i + 1}/{max_swipes})")
                scroll_view = self.driver.find_element(AppiumBy.CLASS_NAME, "XCUIElementTypeScrollView")
                self.driver.execute_script('mobile: scroll', {'direction': 'right', 'element': scroll_view.id})

        raise Exception(f"Could not find activity '{activity}' after {max_swipes} scrolls.")

    def click_activity(self, activity, max_swipes=5):
        # 1. Standard locator (we use math for visibility, not Appium)
        locator = (AppiumBy.IOS_PREDICATE, f'name CONTAINS "{activity}"')

        # 2. Temporarily turn OFF global implicit waits
        self.driver.implicitly_wait(0)
        short_wait = WebDriverWait(self.driver, 2)

        # Get the physical width of the phone screen for our math check
        screen_width = self.driver.get_window_size()['width']

        try:
            for i in range(max_swipes):
                try:
                    # 3. Look for the element in the DOM
                    element = short_wait.until(EC.presence_of_element_located(locator))

                    # --- THE MATH CHECK ---
                    rect = element.rect

                    # If the element is technically in the code but sitting in the right-most 15%
                    # (or entirely off-screen), throw an exception to force a swipe.
                    if rect['x'] >= (screen_width * 0.85):
                        print(f"Element in DOM but off-screen (x={rect['x']}). Forcing swipe...")
                        raise TimeoutException("Element mathematically off screen")
                    # ----------------------

                    try:
                        # 4. It passed the math check! Calculate the exact center pixel.
                        center_x = rect['x'] + (rect['width'] / 2)
                        center_y = rect['y'] + (rect['height'] / 2)

                        # Force iOS to tap those exact mathematical coordinates
                        self.driver.execute_script("mobile: tap", {"x": center_x, "y": center_y})

                        print(f"Clicked '{activity}' successfully via coordinate tap (x={center_x}, y={center_y}).")
                        return  # Success! Exit the function.

                    except Exception as e:
                        # Fallback just in case something intercepts the strict coordinate tap
                        print(f"Coordinate tap failed ({type(e).__name__}). Scrolling to center element...")
                        scroll_view = self.driver.find_element(AppiumBy.CLASS_NAME, "XCUIElementTypeScrollView")
                        self.driver.execute_script('mobile: scroll',
                                                   {'direction': 'right', 'element': scroll_view.id, 'toVisible': True})
                        self.wait.until(EC.element_to_be_clickable(locator)).click()
                        return

                except TimeoutException:
                    # 5. Element wasn't in DOM, OR it failed the math check. Execute ONE swipe.
                    print(f"Activity not fully on screen. Swiping right... (Attempt {i + 1}/{max_swipes})")
                    scroll_view = self.driver.find_element(AppiumBy.CLASS_NAME, "XCUIElementTypeScrollView")
                    self.driver.execute_script('mobile: scroll', {'direction': 'right', 'element': scroll_view.id})

            # 6. Loop exhausted
            raise Exception(f"Could not find activity '{activity}' after {max_swipes} swipes.")

        finally:
            # 7. ALWAYS turn implicit wait back on when the function finishes (or fails)
            # Change '10' to whatever your standard framework wait time is.
            self.driver.implicitly_wait(10)

    def dismiss_rating_popup_if_present(self):
        """Checks for the App Store rating popup and dismisses it if it blocks the view."""
        try:
            popup_wait = WebDriverWait(self.driver, 10)
            not_now_element = popup_wait.until(EC.element_to_be_clickable(self.not_now_rating_button))
            not_now_element.click()
            print("System Alert: Dismissed the 'Enjoying RandezVous?' rating popup.")
        except TimeoutException:
            pass

    def click_out_of_activity(self):
        """Taps the background to dismiss the bottom sheet."""
        print("clicking out of the activity...")
        self.wait.until(EC.element_to_be_clickable(self.dismiss_after_completing_activity)).click()

    def click_back(self):
        print("clicking back...")
        self.wait.until(EC.element_to_be_clickable(self.back_button)).click()

    """"Trivia Based Activity"""
    def click_check_requirements(self):
        """Clicks the 'Check Quest Requirements' button."""
        self.wait.until(EC.element_to_be_clickable(self.check_quest_requirements)).click()

    def click_view_prompt(self):
        """Clicks the 'View Prompt' button."""
        self.wait.until(EC.element_to_be_clickable(self.view_prompt)).click()

    def click_add_to_quest(self):
        """Clicks the 'Add To Quest' button."""
        self.wait.until(EC.element_to_be_clickable(self.add_to_quest_button)).click()

    def enter_prompt(self, response_text):
        """Waits for the text box to be visible, clicks it, and enters the response text."""
        text_view = self.wait.until(EC.element_to_be_clickable(self.prompt_text_box))
        text_view.click()
        text_view.clear()
        text_view.send_keys(response_text)

    def click_submit(self):
        """Waits for the 'submit response' button to become enabled and clicks it."""
        submit_button = self.wait.until(EC.element_to_be_clickable(self.submit_response_button))
        submit_button.click()

    def click_check_answer(self):
        """Waits for the 'Check Answer' button to become enabled and clicks it."""
        check_button = self.wait.until(EC.element_to_be_clickable(self.check_answer_button))
        check_button.click()

    def complete_trivia_activity(self, activity, response_text):
        self.click_trivia_activity(activity)
        self.click_check_requirements()
        self.click_view_prompt()
        self.enter_prompt(response_text)
        self.click_check_answer()
        self.dismiss_rating_popup_if_present()
        self.click_out_of_activity()
        self.click_back()

    """" Honor Based Activity"""
    def click_add_to_quest_button(self):
        assert self.wait.until(EC.visibility_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Honor Code Activity")))
        self.wait.until(EC.element_to_be_clickable(self.add_to_quest_button)).click()

    def click_completed_activity_button(self):
        self.wait.until(EC.element_to_be_clickable(self.completed_activity_button)).click()

    def complete_honor_based_activity(self, activity, login = False):
        self.click_activity(activity)
        self.click_complete_quest_button()
        self.click_completed_activity_button()
        self.dismiss_rating_popup_if_present()
        self.click_back()

    """" Prompt Based Activity"""
    def complete_prompt_activity(self, activity, response_text, click_back = False):
        self.click_activity(activity)
        self.click_check_requirements()
        self.click_view_prompt()
        self.enter_prompt(response_text)
        self.click_submit()
        self.dismiss_rating_popup_if_present()
        self.click_out_of_activity()
        if click_back:
            self.click_back()

    """" Location Based Activity"""
    def click_complete_quest_button(self):
        self.wait.until(EC.element_to_be_clickable(self.complete_quest_button)).click()

    def complete_location_activity(self, activity):
        self.click_activity(activity)
        self.click_complete_quest_button()
        self.click_complete_quest_button()
        self.dismiss_rating_popup_if_present()
        self.click_back()

    """" Photo Based Activity"""
    def click_submit_photo_button(self):
        self.wait.until(EC.element_to_be_clickable(self.submit_photo_button)).click()

    def click_photo_button(self):
        print("Waiting for the photo library icon...", flush=True)

        library_locator = (AppiumBy.ACCESSIBILITY_ID, "photo.on.rectangle.angled")

        btn = self.wait.until(EC.presence_of_element_located(library_locator))

        rect = btn.rect
        abs_x = rect['x'] + (rect['width'] / 2)
        abs_y = rect['y'] + (rect['height'] / 2)

        print(f"Tapping absolute coordinates: x={abs_x}, y={abs_y}", flush=True)

        self.driver.execute_script("mobile: tap", {
            "x": abs_x,
            "y": abs_y
        })

        print("Absolute coordinate tap executed.", flush=True)

    def select_most_recent_image(self):
        print("Finding image by identifier...")
        all_photos = self.driver.find_elements(AppiumBy.ACCESSIBILITY_ID, "PXGGridLayout-Info")

        if not all_photos:
            raise Exception("Could not find any photos.")

        first_photo = all_photos[0]

        rect = first_photo.rect
        x = rect['x'] + (rect['width'] / 2)
        y = rect['y'] + (rect['height'] / 2)

        print(f"Executing REAL TAP on coordinates: x={x}, y={y}")

        self.driver.execute_script('mobile: tap', {
            'x': x,
            'y': y,
            'element': first_photo
        })
        print("Waiting for app to process selection...")

    def click_send_button(self):
        print("Waiting for Send button visibility...")
        wait = WebDriverWait(self.driver, 20)
        try:
            self.send_button = (AppiumBy.IOS_PREDICATE, "label == 'Send'")
            btn = self.wait.until(EC.visibility_of_element_located(self.send_button))
            btn.click()
            print("Clicked Send Button")

        except Exception as e:
            raise e

    def complete_photo_activity(self, activity):
        print("Step 1: Clicking activity...")
        self.click_activity(activity)
        print("Step 2: Checking requirements...")
        self.click_check_requirements()
        print("Step 3: Submitting photo button...")
        self.click_submit_photo_button()
        print("Step 4: Clicking photo trigger...")
        self.click_photo_button()
        print("Step 5: Selecting most recent image...")
        self.select_most_recent_image()
        self.click_send_button()
        self.dismiss_rating_popup_if_present()
        self.click_out_of_activity()
        self.click_back()

    def complete_all_activities(self):
        self.complete_trivia_activity("Trivia Activity", "Trivia")
        self.complete_photo_activity("Photo Activity")
        self.complete_location_activity("Location Activity")
        self.complete_honor_based_activity("Honor Code Activity")
        self.complete_prompt_activity("Prompt Activity", "Prompt")

    def click_out_of_finish_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.quests_nav_bar)).click()

    def click_exit_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.primary_exit_quest_button)).click()
        self.wait.until(EC.element_to_be_clickable(self.secondary_exit_confirm_button)).click()





