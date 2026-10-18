import pytest

from helpers.ios import (
    CustomQuestPage, QuestHelper, LeaderboardHelper, LoginPageHelper,
    WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper, DeviceHelper,
    DashboardOverlay,
)


@pytest.mark.cleanup(type="username", value="AutomatedTester")
def test_complete_quest_from_dashboard(rv_driver):
    username = "AutomatedTester"
    quest = "test-automation-quest"

    driver = rv_driver
    dashboard = DashboardOverlay(driver)
    welcome = WelcomeToQuestHelper(driver)
    choose_username = ChooseUsernameHelper(driver)
    adventure = StartAdventureHelper(driver)
    quest_helper = QuestHelper(driver)
    custom_quest = CustomQuestPage(driver)
    login_helper = LoginPageHelper(driver)
    device_helper = DeviceHelper(rv_driver)
    leaderboard = LeaderboardHelper(rv_driver)

    quest_helper.sign_out_if_signed_in()
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

    device_helper.set_simulator_location()
    custom_quest.complete_all_activities()
    custom_quest.dismiss_quest_completion_overlay()

    # Guest usernames can repeat across leftover rows, so accept any row for this name at the expected score.
    expected = leaderboard.expected_score(activities_completed=5, quest_completed=True)
    leaderboard.open()
    leaderboard.get_row(username, points=expected)
    points = [r["points"] for r in leaderboard.get_rows_for(username)]
    assert expected in points, \
        f"'{username}' should have {expected} points on the leaderboard after completing the quest, saw {points}"
