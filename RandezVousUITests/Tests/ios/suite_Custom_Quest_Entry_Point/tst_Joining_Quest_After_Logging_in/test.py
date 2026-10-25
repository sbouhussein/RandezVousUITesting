import pytest

from helpers.ios import CustomQuestPage, LeaderboardHelper
from helpers.ios.ios_test_data import TEST_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_joining_quest_after_logging_in(rv_driver):
    CustomQuestPage(rv_driver).sign_in_and_join()
    expected, actual = LeaderboardHelper(rv_driver).score_check()
    assert actual == expected, f"Expected the {expected} starting points on the leaderboard after joining, got {actual}"
