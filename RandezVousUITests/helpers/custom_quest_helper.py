import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class QuestHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    # Tab Bar
    quests_tab = (AppiumBy.ACCESSIBILITY_ID, "scroll.fill")
    home_tab = (AppiumBy.ACCESSIBILITY_ID, "house")
    explore_tab = (AppiumBy.ACCESSIBILITY_ID, " Explore ")
    participants_tab = (AppiumBy.ACCESSIBILITY_ID, " Participants ")
    profile_tab = (AppiumBy.ACCESSIBILITY_ID, " Profile ")

    # Quests Page
    quests_header = (AppiumBy.ACCESSIBILITY_ID, "Quests")
    trophy_button = (AppiumBy.ACCESSIBILITY_ID, "trophy.fill")
    active_badge = (AppiumBy.ACCESSIBILITY_ID, "Active")
    custom_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Custom")
    join_quest_page = (AppiumBy.ACCESSIBILITY_ID, "Join a Quest")

    def navigate_to_quests_tab(self):
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


class CustomQuestPage:
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
    check_quest_requirements = (AppiumBy.ACCESSIBILITY_ID, "Check Quest Requirements")
    view_prompt = (AppiumBy.ACCESSIBILITY_ID, "View Prompt")
    prompt_text_box = (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeTextView")
    check_answer_button = (AppiumBy.ACCESSIBILITY_ID, "Check Answer")
    not_now_rating_button = (AppiumBy.ACCESSIBILITY_ID, "Not Now")
    dismiss_after_completing_activity = (AppiumBy.ACCESSIBILITY_ID, "PopoverDismissRegion")
    back_button = (AppiumBy.ACCESSIBILITY_ID, "chevron.left")
    add_to_quest_button = (AppiumBy.ACCESSIBILITY_ID, "Add to Quest")
    completed_activity_button = (AppiumBy.ACCESSIBILITY_ID, "I've completed this activity")
    submit_photo_button = (AppiumBy.ACCESSIBILITY_ID, "Submit Photo")

    """""Universal functions"""
    def join_custom_quest(self, quest_code):
        quest_helper = QuestHelper(self.driver)

        quest_helper.navigate_to_quests_tab()
        quest_helper.click_custom_quest_button()
        self.enter_quest_code(quest_code)
        self.click_find_quest()
        self.click_start_quest()

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

    def click_view_requirements(self):
        self.wait.until(EC.element_to_be_clickable(self.view_requirements_button)).click()

    def click_hide_requirements(self):
        self.wait.until(EC.element_to_be_clickable(self.hide_requirements_button)).click()

    def click_activity(self, activity):
        predicate = f'label CONTAINS "{activity}"'
        locator = (AppiumBy.IOS_PREDICATE, predicate)

        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()

        except Exception:
            print(f"Element '{activity}' not found immediately. Attempting to scroll...")

            self.driver.execute_script('mobile: scroll', {
                'direction': 'right',
                'element': self.driver.find_element(AppiumBy.CLASS_NAME, "XCUIElementTypeScrollView").id,
                'predicateString': f'name == "{activity}"'
            })

            self.driver.find_element(*locator).click()

    def dismiss_rating_popup_if_present(self):
        """Checks for the App Store rating popup and dismisses it if it blocks the view."""
        try:
            popup_wait = WebDriverWait(self.driver, 3)
            not_now_element = popup_wait.until(EC.element_to_be_clickable(self.not_now_rating_button))
            not_now_element.click()
            print("System Alert: Dismissed the 'Enjoying RandezVous?' rating popup.")
        except TimeoutException:
            pass

    def click_out_of_activity(self):
        """Taps the background to dismiss the bottom sheet."""
        self.wait.until(EC.element_to_be_clickable(self.dismiss_after_completing_activity)).click()

    def click_back(self):
        self.wait.until(EC.element_to_be_clickable(self.back_button)).click()

    """"Trivia Based Activity"""
    def click_check_requirements_activity(self):
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

    def click_check_answer(self):
        """Waits for the 'Check Answer' button to become enabled and clicks it."""
        check_button = self.wait.until(EC.element_to_be_clickable(self.check_answer_button))
        check_button.click()

    def complete_trivia_activity(self, activity, response_text):
        self.click_activity(activity)
        self.click_check_requirements_activity()
        self.click_view_prompt()
        self.enter_prompt(response_text)
        self.click_check_answer()
        self.dismiss_rating_popup_if_present()
        self.click_out_of_activity()
        self.click_back()

    """" Honor Based Activity"""
    def click_add_to_quest_button(self):
        self.wait.until(EC.element_to_be_clickable(self.add_to_quest_button)).click()

    def click_completed_activity_button(self):
        self.wait.until(EC.element_to_be_clickable(self.completed_activity_button)).click()

    def complete_honor_based_activity(self, activity):
        self.click_activity(activity)
        self.click_add_to_quest()
        self.click_completed_activity_button()
        self.dismiss_rating_popup_if_present()
        self.click_back()

    """" Prompt Based Activity"""
    def complete_prompt_activity(self, activity, response_text):
        self.click_activity(activity)
        self.click_check_requirements_activity()
        self.click_view_prompt()
        self.enter_prompt(response_text)
        self.click_check_answer()
        self.dismiss_rating_popup_if_present()
        self.click_out_of_activity()
        self.click_back()

    """" Location Based Activity"""
    def complete_location_activity(self, activity):
        self.click_activity(activity)
        self.click_check_requirements_activity()
        self.click_out_of_activity()
        self.click_back()

    """" Location Based Activity"""
    def click_submit_photo_button(self):
        self.wait.until(EC.element_to_be_clickable(self.submit_photo_button)).click()

    def complete_photo_activity(self, activity):
        self.click_activity(activity)
        self.click_check_requirements_activity()
        self.click_submit_photo_button()

    def click_exit_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.primary_exit_quest_button)).click()
        self.wait.until(EC.element_to_be_clickable(self.secondary_exit_confirm_button)).click()





