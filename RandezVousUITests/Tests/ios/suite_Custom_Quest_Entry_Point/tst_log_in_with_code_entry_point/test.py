import pytest

from helpers.ios.custom_quest_helper import CustomQuestPage
from helpers.ios.login_page_helper import LoginPageHelper, WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper


@pytest.mark.cleanup(type="username", value="AutomatedTester")
def test_log_in_with_code_entry_point(rv_driver):
    driver = rv_driver
    login_page = LoginPageHelper(driver)
    custom_quest_helper = CustomQuestPage(driver)
    welcome = WelcomeToQuestHelper(driver)
    choose_username = ChooseUsernameHelper(driver)
    start_adventure = StartAdventureHelper(driver)
    login_helper = LoginPageHelper(driver)
    quest = "testautomationQuest"

    if login_page.verify_login_page_is_displayed():
        login_page.click_login_with_code()

    custom_quest_helper.enter_quest_code(quest)
    custom_quest_helper.click_find_quest()
    welcome.click_lets_go()
    choose_username.enter_username("AutomatedTester")
    choose_username.click_join_quest()
    start_adventure.click_start_adventure()
    custom_quest_helper.click_exit_quest()

    login_helper.login_and_out_to_cleanup(email_text="oalson123@gmail.com", password_text="OmarTest123")
