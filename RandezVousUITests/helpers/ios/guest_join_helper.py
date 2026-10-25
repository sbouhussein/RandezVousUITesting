from helpers.ios.custom_quest_helper import QuestHelper
from helpers.ios.ios_test_data import GUEST_USERNAME, QUEST_ID
from helpers.ios.login_page_helper import (
    ChooseUsernameHelper, LoginPageHelper, StartAdventureHelper, WelcomeToQuestHelper,
)
from helpers.ios.sign_in_overlay_helper import DashboardOverlay


class GuestJoinHelper:
    """Joining a custom quest as a guest (no account): dashboard code entry, then the onboarding screens."""

    def __init__(self, driver):
        self.driver = driver
        self.quest = QuestHelper(driver)
        self.login = LoginPageHelper(driver)
        self.dashboard = DashboardOverlay(driver)
        self.welcome = WelcomeToQuestHelper(driver)
        self.choose_username = ChooseUsernameHelper(driver)
        self.adventure = StartAdventureHelper(driver)

    def open_dashboard(self):
        """Signs out, continues as a guest and opens the Quests dashboard; returns whether it is displayed."""
        self.quest.sign_out_if_signed_in()
        self.login.click_skip_authentication()
        self.quest.navigate_to_quests_tab()
        return self.dashboard.verify_dashboard_is_displayed()

    def enter_code(self, quest_code=QUEST_ID):
        self.dashboard.enter_custom_quest_code(quest_code)

    def continue_past_welcome(self, required=False):
        if required or self.welcome.verify_welcome_modal_is_displayed():
            self.welcome.click_lets_go()

    def start_adventure(self, required=False):
        if required or self.adventure.verify_start_adventure_page_is_displayed():
            self.adventure.click_start_adventure()

    def finish_onboarding(self, username=GUEST_USERNAME, required=False):
        """Welcome -> choose username -> join -> start adventure; screens that may be skipped are only handled
        when shown, unless `required`."""
        self.continue_past_welcome(required)
        self.choose_username.enter_username(username)
        if required or self.choose_username.is_join_button_enabled():
            self.choose_username.click_join_quest()
        self.start_adventure(required)

    def join_as_guest(self, quest_code=QUEST_ID, username=GUEST_USERNAME):
        self.open_dashboard()
        self.enter_code(quest_code)
        self.finish_onboarding(username)
