import pytest

from helpers.ios import CustomQuestPage, LeaderboardHelper, DeviceHelper
from helpers.ios.ios_test_data import TEST_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_complete_quest_from_login(rv_driver):
    quest = CustomQuestPage(rv_driver)
    quest.sign_in_and_join()
    DeviceHelper(rv_driver).set_simulator_location()
    quest.complete_all_activities()
    quest.dismiss_quest_completion_overlay()

    expected, actual = LeaderboardHelper(rv_driver).score_check(activities_completed=5, quest_completed=True)
    assert actual == expected, f"Expected {expected} points on the leaderboard after completing the quest, got {actual}"
