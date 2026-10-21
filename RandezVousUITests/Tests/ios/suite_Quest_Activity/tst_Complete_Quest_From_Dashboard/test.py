import pytest

from helpers.ios import CustomQuestPage, DeviceHelper, GuestJoinHelper, LeaderboardHelper
from helpers.ios.ios_test_data import GUEST_USERNAME


@pytest.mark.cleanup(type="username", value=GUEST_USERNAME)
def test_complete_quest_from_dashboard(rv_driver):
    guest = GuestJoinHelper(rv_driver)
    assert guest.open_dashboard(), "Quests Dashboard not detected"
    guest.enter_code()
    guest.finish_onboarding()

    DeviceHelper(rv_driver).set_simulator_location()
    quest = CustomQuestPage(rv_driver)
    quest.complete_all_activities()
    quest.dismiss_quest_completion_overlay()

    # Guest usernames repeat across leftover rows, so accept any row for this name at the expected score.
    expected, points = LeaderboardHelper(rv_driver).scores_for(GUEST_USERNAME, activities_completed=5, quest_completed=True)
    assert expected in points, f"Expected {expected} points for '{GUEST_USERNAME}' after completing the quest, saw {points}"
