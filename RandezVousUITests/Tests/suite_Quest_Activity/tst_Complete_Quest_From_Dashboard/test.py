import pytest

from helpers.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.login_page_helper import LoginPageHelper, WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper
from helpers.profile_helper import ProfileHelper
from helpers.sign_in_overlay_helper import DashboardOverlay


@pytest.mark.cleanup(type="username", value="AutomatedTester")
def test_complete_quest_from_dashboard(rv_driver):
    username = "AutomatedTester"
    quest = "TestAutomationActivityQuest"

    driver = rv_driver
    dashboard = DashboardOverlay(driver)
    welcome = WelcomeToQuestHelper(driver)
    choose_username = ChooseUsernameHelper(driver)
    adventure = StartAdventureHelper(driver)
    quest_helper = QuestHelper(driver)
    custom_quest = CustomQuestPage(driver)
    login_helper = LoginPageHelper(driver)

    login_helper.click_skip_authentication()
    quest_helper.navigate_to_quests_tab()
    assert dashboard.verify_dashboard_is_displayed(), "Quests Dashboard not detected"
    dashboard.enter_custom_quest_code(quest)
    welcome.click_lets_go()

    choose_username.enter_username(username)
    if choose_username.is_join_button_enabled():
        choose_username.click_join_quest()

    if adventure.verify_start_adventure_page_is_displayed():
        adventure.click_start_adventure()

    custom_quest.complete_all_activities()
    custom_quest.finish_quest()

    custom_quest.click_exit_quest()

    login_helper.login_and_out_to_cleanup(email_text="oalson123@gmail.com", password_text="OmarTest123")


