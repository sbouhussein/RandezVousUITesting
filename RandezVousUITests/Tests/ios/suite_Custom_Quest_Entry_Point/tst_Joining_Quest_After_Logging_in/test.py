import pytest

from helpers.ios import CustomQuestPage, LeaderboardHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_joining_quest_after_logging_in(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    username = "OmarTesting"
    quest = "test-automation-quest"
    custom_quest = CustomQuestPage(rv_driver)
    leaderboard = LeaderboardHelper(rv_driver)

    custom_quest.sign_in_and_join(email, password, quest)

    expected = leaderboard.expected_score()
    assert leaderboard.get_score(username, expected_points=expected) == expected, \
        f"'{username}' should have the {expected} starting points on the leaderboard after joining"
