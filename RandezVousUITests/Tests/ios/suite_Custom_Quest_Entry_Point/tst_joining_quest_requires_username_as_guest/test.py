import pytest

from helpers.ios import (
    QuestHelper, LoginPageHelper, WelcomeToQuestHelper, ChooseUsernameHelper,
    StartAdventureHelper, DashboardOverlay,
)



@pytest.mark.cleanup(type="username", value="AutomatedTester")
def test_joining_quest_requires_username_as_guest(rv_driver):
    """A guest with no saved username can't join a custom quest without choosing one first."""
    quest = "test-automation-quest"

    driver = rv_driver
    login_helper = LoginPageHelper(driver)
    quest_helper = QuestHelper(driver)
    dashboard = DashboardOverlay(driver)
    welcome = WelcomeToQuestHelper(driver)
    choose_username = ChooseUsernameHelper(driver)
    adventure = StartAdventureHelper(driver)

    quest_helper.sign_out_if_signed_in()
    login_helper.click_skip_authentication()
    quest_helper.navigate_to_quests_tab()
    dashboard.enter_custom_quest_code(quest)

    if welcome.verify_welcome_modal_is_displayed():
        welcome.click_lets_go()

    assert choose_username.verify_choose_username_page_is_displayed(), \
        "A guest with no username should be asked to choose one before joining"
    assert choose_username.is_join_button_enabled() is False, \
        "Join Quest should be disabled until a username is entered"

    choose_username.enter_username("AutomatedTester")
    assert choose_username.is_join_button_enabled() is True, \
        "Join Quest should become enabled once a username is entered"
    choose_username.click_join_quest()

    if adventure.verify_start_adventure_page_is_displayed():
        adventure.click_start_adventure()
