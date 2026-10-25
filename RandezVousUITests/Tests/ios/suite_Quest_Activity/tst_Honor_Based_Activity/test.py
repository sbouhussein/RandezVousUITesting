import pytest

from helpers.ios import CustomQuestPage, LeaderboardHelper
from helpers.ios.ios_test_data import TEST_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_honor_based_activity(rv_driver):
    quest = CustomQuestPage(rv_driver)
    quest.sign_in_and_join()
    quest.complete_honor_based_activity("Honor")

    expected, actual = LeaderboardHelper(rv_driver).score_check(activities_completed=1)
    assert actual == expected, f"Expected {expected} points on the leaderboard after the activity, got {actual}"
