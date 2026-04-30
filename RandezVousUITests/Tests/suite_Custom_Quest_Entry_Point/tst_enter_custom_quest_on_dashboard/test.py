from helpers.custom_quest_helper import QuestHelper
from helpers.login_page_helper import WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper
from helpers.sign_in_overlay_helper import SignInOverlayHelper


def test_enter_custom_quest_on_dashboard(rv_driver_no_reset):
    driver = rv_driver_no_reset
    dashboard = SignInOverlayHelper(driver)
    welcome = WelcomeToQuestHelper(driver)
    username_screen = ChooseUsernameHelper(driver)
    adventure = StartAdventureHelper(driver)
    quest_helper = QuestHelper(driver)

    quest_helper.navigate_to_quests_tab()
    assert dashboard.verify_dashboard_is_displayed(), "Quests Dashboard not detected"
    dashboard.enter_custom_quest_code("testautomationQuest")

    if welcome.verify_welcome_modal_is_displayed():
        welcome.click_lets_go()

    username_screen.enter_username("AutomationTester")
    if username_screen.is_join_button_enabled():
        username_screen.click_join_quest()

    if adventure.verify_start_adventure_page_is_displayed():
        adventure.click_start_adventure()

    quest_helper.click_exit_quest()
