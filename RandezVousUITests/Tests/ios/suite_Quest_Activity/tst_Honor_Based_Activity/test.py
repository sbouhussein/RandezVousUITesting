import pytest

from helpers.ios import CustomQuestPage, LeaderboardHelper



@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_honor_based_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    username = "OmarTesting"
    quest = "test-automation-quest"
    activity = "Honor"

    custom_quest = CustomQuestPage(rv_driver)
    leaderboard = LeaderboardHelper(rv_driver)

    custom_quest.sign_in_and_join(email, password, quest)
    custom_quest.complete_honor_based_activity(activity)

    expected = leaderboard.expected_score(activities_completed=1)
    assert leaderboard.get_score(username, expected_points=expected) == expected, \
        f"'{username}' should have {expected} points on the leaderboard after the activity"
