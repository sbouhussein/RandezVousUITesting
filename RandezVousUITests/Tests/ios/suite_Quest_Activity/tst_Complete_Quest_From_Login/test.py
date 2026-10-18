import pytest

from helpers.ios import CustomQuestPage, LeaderboardHelper, DeviceHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_quest_from_login(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    username = "OmarTesting"
    quest = "test-automation-quest"

    custom_quest = CustomQuestPage(rv_driver)
    device_helper = DeviceHelper(rv_driver)
    leaderboard = LeaderboardHelper(rv_driver)

    custom_quest.sign_in_and_join(email, password, quest)
    device_helper.set_simulator_location()
    custom_quest.complete_all_activities()
    custom_quest.dismiss_quest_completion_overlay()

    expected = leaderboard.expected_score(activities_completed=5, quest_completed=True)
    assert leaderboard.get_score(username, expected_points=expected) == expected, \
        f"'{username}' should have {expected} points on the leaderboard after the activity"
