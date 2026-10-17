from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.ios.base_helper import BaseHelper
from helpers.ios.login_page_helper import LoginPageHelper
from helpers.ios.profile_helper import ProfileHelper
from helpers.ios.device_helper import DeviceHelper
from helpers.ios.system_prompt_helper import SystemPromptHelper


class QuestHelper(BaseHelper, LoginPageHelper, ProfileHelper):
    quests_tab = (AppiumBy.IOS_PREDICATE, "label == ' Quests '")
    home_tab = (AppiumBy.ACCESSIBILITY_ID, "house")
    explore_tab = (AppiumBy.ACCESSIBILITY_ID, " Explore ")
    participants_tab = (AppiumBy.ACCESSIBILITY_ID, " Participants ")

    quests_header = (AppiumBy.ACCESSIBILITY_ID, "Quests")
    active_badge = (AppiumBy.ACCESSIBILITY_ID, "Active")
    custom_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Find")
    join_quest_page = (AppiumBy.ACCESSIBILITY_ID, "Find a Quest")
    info_button = (AppiumBy.IOS_PREDICATE, "label == 'Quest rules'")
    daily_challenge_section_label = (AppiumBy.ACCESSIBILITY_ID, "DAILY CHALLENGE")
    start_daily_quest_button = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name CONTAINS "Start!"`]')
    # First-launch "Monthly Quests" carousel that covers the Quests page.
    onboarding_skip_button = (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeButton' AND label == 'Skip'")
    sign_in_prompt = (
        AppiumBy.ACCESSIBILITY_ID,
        "Create an account or sign back in to customize your profile and get activities personalized just for you.",
    )

    def navigate_to_quests_tab(self):
        print("Navigating to Quests Tab")
        # Right after login the first tap on the tab is sometimes swallowed, so retry it.
        attempts = 3
        for attempt in range(1, attempts + 1):
            self.wait.until(EC.element_to_be_clickable(self.quests_tab)).click()
            try:
                WebDriverWait(self.driver, 8).until(EC.visibility_of_element_located(self.quests_header))
                self.skip_onboarding_if_present()
                return
            except TimeoutException:
                print(f"Quests page did not open (attempt {attempt}/{attempts}); retrying tap")
        raise AssertionError("Quests page header not visible after clicking tab")

    def skip_onboarding_if_present(self):
        if self.is_visible(self.onboarding_skip_button, custom_timeout=3):
            self.click(self.onboarding_skip_button)
            print("Skipped the Monthly Quests onboarding carousel.")

    def click_custom_quest_button(self):
        self.wait.until(EC.element_to_be_clickable(self.custom_quest_button)).click()
        assert self.wait.until(EC.visibility_of_element_located(self.join_quest_page)).is_displayed(), \
            "Custom Quest overlay did not appear"

    def click_info_icon(self):
        self.wait.until(EC.element_to_be_clickable(self.info_button)).click()

    def start_the_daily_challenge(self):
        self.wait.until(EC.element_to_be_clickable(self.start_daily_quest_button)).click()

    def is_active(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.active_badge)).is_displayed()
        except Exception:
            return False

    def sign_out_if_signed_in(self):
        if self.is_visible(self.tab_bar):
            print("App is signed in (anonymous or account). Fast-resetting to signed-out state.")
            DeviceHelper(self.driver).fast_reset_to_signed_out()


class CustomQuestPage(BaseHelper):
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    quest_code_input_field = (AppiumBy.CLASS_NAME, "XCUIElementTypeTextField")
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
    dismiss_after_completing_activity = (AppiumBy.ACCESSIBILITY_ID, "PopoverDismissRegion")
    quests_nav_bar = (AppiumBy.ACCESSIBILITY_ID, "Quests")
    back_button = (AppiumBy.IOS_PREDICATE, "label == 'Back'")
    add_to_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Add to Quest")
    completed_activity_button = (AppiumBy.ACCESSIBILITY_ID, "I've completed this activity")
    submit_photo_button = (AppiumBy.XPATH, "//XCUIElementTypeButton[contains(@label, 'Submit a Photo')]")
    photo_library_button = (AppiumBy.ACCESSIBILITY_ID, "photo.on.rectangle.angled")
    send_button = (AppiumBy.IOS_PREDICATE, "label == 'Send'")
    complete_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Complete in Quest")
    # QuestProgressView (the "Add <activity> to <quest>" sheet). Its button shares the card's label,
    # and the card's copy comes first in the tree, so anchor on the sheet's own label.
    progress_sheet_label = (AppiumBy.ACCESSIBILITY_ID, "Current Progress:")
    sheet_complete_quest_button = (
        AppiumBy.XPATH,
        "//XCUIElementTypeStaticText[@name='Current Progress:']"
        "/following::XCUIElementTypeButton[@name='Complete in Quest']",
    )
    finish_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Finish Quest")
    log_in_button = (AppiumBy.ACCESSIBILITY_ID, "Log in")
    prompt_nav_bar = (AppiumBy.ACCESSIBILITY_ID, "Prompt Activity")
    trivia_incorrect_message = (AppiumBy.ACCESSIBILITY_ID, "Not quite, try again.")
    # Shown in place of the "Complete in Quest" button when the user is out of range.
    out_of_range_message = (AppiumBy.IOS_PREDICATE, 'label CONTAINS "away from being able to complete this activity"')

    def join_custom_quest(self, quest_code):
        quest_helper = QuestHelper(self.driver)

        quest_helper.navigate_to_quests_tab()
        quest_helper.click_custom_quest_button()
        self.enter_quest_code(quest_code)
        self.click_find_quest()
        self.click_start_quest()
        # A first-time start lands on the quest detail screen, not the Quests list.
        self.wait.until(EC.visibility_of_element_located(self.primary_exit_quest_button))

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
                    return
                except Exception:
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
        """Swipes the horizontal activity carousel until `activity` is on screen, then taps its
        center. Appium reports off-screen carousel cards as present, so visibility is judged from
        the element's x position instead."""
        locator = (AppiumBy.IOS_PREDICATE, f'name CONTAINS "{activity}"')

        short_wait = WebDriverWait(self.driver, 2)
        screen_width = self.driver.get_window_size()['width']

        for i in range(max_swipes):
            try:
                element = short_wait.until(EC.presence_of_element_located(locator))
                rect = element.rect

                # In the right-most 15% of the screen (or past it) counts as off-screen.
                if rect['x'] >= (screen_width * 0.85):
                    print(f"Element in DOM but off-screen (x={rect['x']}). Forcing swipe...")
                    raise TimeoutException("Element is off screen")

                try:
                    center_x = rect['x'] + (rect['width'] / 2)
                    center_y = rect['y'] + (rect['height'] / 2)
                    self.driver.execute_script("mobile: tap", {"x": center_x, "y": center_y})
                    print(f"Clicked '{activity}' via coordinate tap (x={center_x}, y={center_y}).")
                    return

                except Exception as e:
                    print(f"Coordinate tap failed ({type(e).__name__}). Scrolling to center element...")
                    scroll_view = self.driver.find_element(AppiumBy.CLASS_NAME, "XCUIElementTypeScrollView")
                    self.driver.execute_script('mobile: scroll',
                                               {'direction': 'right', 'element': scroll_view.id, 'toVisible': True})
                    self.wait.until(EC.element_to_be_clickable(locator)).click()
                    return

            except TimeoutException:
                print(f"Activity not fully on screen. Swiping right... (Attempt {i + 1}/{max_swipes})")
                scroll_view = self.driver.find_element(AppiumBy.CLASS_NAME, "XCUIElementTypeScrollView")
                self.driver.execute_script('mobile: scroll', {'direction': 'right', 'element': scroll_view.id})

        raise Exception(f"Could not find activity '{activity}' after {max_swipes} swipes.")

    def dismiss_rating_popup_if_present(self):
        SystemPromptHelper(self.driver).dismiss_rating_prompt(timeout=10)

    def _click_past_rating_popup(self, locator):
        """The rating card can land after dismiss_rating_popup_if_present gives up and cover `locator`."""
        try:
            self.click(locator)
        except TimeoutException:
            if not SystemPromptHelper(self.driver).dismiss_rating_prompt(timeout=2):
                raise
            self.click(locator)

    def click_out_of_activity(self):
        """Taps the background to dismiss the bottom sheet."""
        print("clicking out of the activity...")
        self._click_past_rating_popup(self.dismiss_after_completing_activity)

    def click_back(self):
        print("clicking back...")
        self._click_past_rating_popup(self.back_button)

    # Trivia

    def click_check_requirements(self):
        self.wait.until(EC.element_to_be_clickable(self.check_quest_requirements)).click()

    def click_view_prompt(self):
        self.wait.until(EC.element_to_be_clickable(self.view_prompt)).click()

    def click_add_to_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.add_to_quest_button)).click()

    def enter_prompt(self, response_text):
        text_view = self.wait.until(EC.element_to_be_clickable(self.prompt_text_box))
        text_view.click()
        text_view.clear()
        text_view.send_keys(response_text)

    def click_submit(self):
        self.wait.until(EC.element_to_be_clickable(self.submit_response_button)).click()

    def click_check_answer(self):
        self.wait.until(EC.element_to_be_clickable(self.check_answer_button)).click()

    def complete_trivia_activity(self, activity, response_text):
        self.click_trivia_activity(activity)
        self.click_check_requirements()
        self.click_view_prompt()
        self.enter_prompt(response_text)
        self.click_check_answer()
        self.dismiss_rating_popup_if_present()
        self.click_out_of_activity()
        self.click_back()

    def attempt_trivia_activity(self, activity, response_text):
        """Like complete_trivia_activity, but stops after checking the answer so the caller can
        check either outcome."""
        self.click_trivia_activity(activity)
        self.click_check_requirements()
        self.click_view_prompt()
        self.enter_prompt(response_text)
        self.click_check_answer()

    def is_trivia_incorrect_message_visible(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.trivia_incorrect_message)).is_displayed()
        except TimeoutException:
            return False

    # Honor

    def click_completed_activity_button(self):
        self.wait.until(EC.element_to_be_clickable(self.completed_activity_button)).click()

    def complete_honor_based_activity(self, activity):
        self.click_activity(activity)
        self.click_complete_quest_button()
        self.click_completed_activity_button()
        self.dismiss_rating_popup_if_present()
        self.click_back()

    # Prompt

    def complete_prompt_activity(self, activity, response_text, click_back=False):
        self.click_activity(activity)
        self.click_check_requirements()
        self.click_view_prompt()
        self.enter_prompt(response_text)
        self.click_submit()
        self.dismiss_rating_popup_if_present()
        self.click_out_of_activity()
        if click_back:
            self.click_back()

    # Location

    def click_complete_quest_button(self):
        self.wait.until(EC.element_to_be_clickable(self.complete_quest_button)).click()

    def complete_location_activity(self, activity):
        self.click_activity(activity)
        # EligibleQuestOverlay auto-opens the sheet 1s after appearing when at the location; tapping
        # the banner toggles it and races that, so just wait for it.
        self.wait.until(EC.visibility_of_element_located(self.progress_sheet_label))
        self.click(self.sheet_complete_quest_button)
        self.dismiss_rating_popup_if_present()
        self.click_back()

    def is_out_of_range_message_visible(self, activity):
        """Out of range, the requirements screen shows a distance message ("You're 170 mi away
        from being able to complete this activity...") instead of 'Complete in Quest'."""
        self.click_activity(activity)
        self.click_check_requirements()
        try:
            return self.wait.until(EC.visibility_of_element_located(self.out_of_range_message)).is_displayed()
        except TimeoutException:
            return False

    # Photo

    def click_submit_photo_button(self):
        self.wait.until(EC.element_to_be_clickable(self.submit_photo_button)).click()

    def click_photo_button(self):
        btn = self.wait.until(EC.presence_of_element_located(self.photo_library_button))
        rect = btn.rect
        x = rect['x'] + (rect['width'] / 2)
        y = rect['y'] + (rect['height'] / 2)
        print(f"Tapping photo library button at x={x}, y={y}")
        self.driver.execute_script("mobile: tap", {"x": x, "y": y})

    def select_most_recent_image(self):
        # The picker fills its grid asynchronously after opening.
        first_photo = self.wait.until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "PXGGridLayout-Info"))
        )

        rect = first_photo.rect
        x = rect['x'] + (rect['width'] / 2)
        y = rect['y'] + (rect['height'] / 2)

        print(f"Tapping most recent photo at x={x}, y={y}")
        self.driver.execute_script('mobile: tap', {
            'x': x,
            'y': y,
            'element': first_photo
        })

    def click_send_button(self):
        self.wait.until(EC.visibility_of_element_located(self.send_button)).click()

    def complete_photo_activity(self, activity):
        self.click_activity(activity)
        self.click_check_requirements()
        self.click_submit_photo_button()
        self.click_photo_button()
        self.select_most_recent_image()
        self.click_send_button()
        self.dismiss_rating_popup_if_present()
        self.click_out_of_activity()
        self.click_back()

    def complete_all_activities(self):
        # Activity cards are labeled by bare type ("Trivia"), not "Trivia Activity".
        self.complete_trivia_activity("Trivia", "Trivia")
        self.complete_photo_activity("Photo")
        self.complete_location_activity("Location")
        self.complete_honor_based_activity("Honor")
        self.complete_prompt_activity("Prompt", "Prompt")

    def click_out_of_finish_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.quests_nav_bar)).click()

    def click_exit_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.primary_exit_quest_button)).click()
        self.wait.until(EC.element_to_be_clickable(self.secondary_exit_confirm_button)).click()
