import pytest

from helpers.custom_quest_helper import QuestHelper
from helpers.login_page_helper import WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper, \
    EmailSignInHelper
from helpers.profile_helper import ProfileHelper
from helpers.sign_in_overlay_helper import SignInOverlayHelper

@pytest.mark.cleanup(type="username", value="AutomatedTester")

def test_enter_custom_quest_on_dashboard(rv_driver):
    driver = rv_driver
    dashboard = SignInOverlayHelper(driver)
    sign_in = EmailSignInHelper(driver)
    welcome = WelcomeToQuestHelper(driver)
    choose_username = ChooseUsernameHelper(driver)
    adventure = StartAdventureHelper(driver)
    quest_helper = QuestHelper(driver)
    profile_helper = ProfileHelper(driver)

    quest_helper.navigate_to_quests_tab()
    assert dashboard.verify_dashboard_is_displayed(), "Quests Dashboard not detected"
    dashboard.enter_custom_quest_code("testautomationQuest")

    if welcome.verify_welcome_modal_is_displayed():
        welcome.click_lets_go()

    choose_username.enter_username("AutomatedTester")
    if choose_username.is_join_button_enabled():
        choose_username.click_join_quest()

    if adventure.verify_start_adventure_page_is_displayed():
        adventure.click_start_adventure()

    quest_helper.click_exit_quest()
    dashboard.click_log_in()
    sign_in.login_with_credentials(email_text="oalson123@gmail.com", password_text="OmarTest123")
    profile_helper.sign_out_if_logged_in()

