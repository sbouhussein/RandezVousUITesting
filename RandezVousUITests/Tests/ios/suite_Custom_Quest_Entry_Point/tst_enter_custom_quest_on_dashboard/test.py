import pytest

from helpers.ios.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.ios.login_page_helper import WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper
from helpers.ios.sign_in_overlay_helper import DashboardOverlay
from helpers.ios.login_page_helper import LoginPageHelper

@pytest.mark.cleanup(type="username", value="AutomatedTester")
def test_enter_custom_quest_on_dashboard(rv_driver):
    quest = "testautomationQuest"

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
    dashboard.enter_custom_quest_code("testautomationQuest")

    if welcome.verify_welcome_modal_is_displayed():
        welcome.click_lets_go()

    choose_username.enter_username("AutomatedTester")
    if choose_username.is_join_button_enabled():
        choose_username.click_join_quest()

    if adventure.verify_start_adventure_page_is_displayed():
        adventure.click_start_adventure()

    custom_quest.click_exit_quest()
    login_helper.login_and_out_to_cleanup(email_text="oalson123@gmail.com", password_text="OmarTest123")
