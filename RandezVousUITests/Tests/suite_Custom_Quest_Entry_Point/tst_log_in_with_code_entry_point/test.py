import pytest

from helpers.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.login_page_helper import LoginPageHelper, WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper
from helpers.profile_helper import ProfileHelper

@pytest.mark.cleanup(type="username", value="AutomatedTester")

def test_log_in_with_code_entry_point(rv_driver):
    driver = rv_driver
    login_page = LoginPageHelper(driver)
    quest_page = CustomQuestPage(driver)
    quest_helper = QuestHelper(driver)
    welcome = WelcomeToQuestHelper(driver)
    choose_username = ChooseUsernameHelper(driver)
    start_adventure = StartAdventureHelper(driver)
    profile_helper = ProfileHelper(driver)

    if login_page.verify_login_page_is_displayed():
        login_page.click_login_with_code()

    quest_page.enter_quest_code("testautomationQuest")
    quest_page.click_find_quest()
    welcome.click_lets_go()
    choose_username.enter_username("AutomatedTester")
    choose_username.click_join_quest()
    start_adventure.click_start_adventure()
    quest_helper.click_exit_quest()

    profile_helper.navigate_to_profile()
    profile_helper.sign_out_if_logged_in()
