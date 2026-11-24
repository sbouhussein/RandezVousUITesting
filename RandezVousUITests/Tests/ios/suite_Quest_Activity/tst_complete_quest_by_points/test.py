import pytest

from helpers.common.access_data_helper import edited_quest
from helpers.ios import CustomQuestPage, LeaderboardHelper
from helpers.ios.ios_test_data import TEST_EMAIL
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, ORG_ID

POINTS_TO_WIN = 200  # starting points + two 100-point activities reach it; one activity does not


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_complete_quest_by_points(rv_driver):
    """A points-to-win quest completes once enough points are earned, without finishing every activity."""
    with edited_quest(ORG_ID, ACTIVITY_QUEST_ID, pointsToWin=POINTS_TO_WIN):  # restored even if the test fails
        quest, board = CustomQuestPage(rv_driver), LeaderboardHelper(rv_driver)
        quest.sign_in_and_join(quest_code=ACTIVITY_QUEST_ID)
        quest.complete_honor_based_activity("Honor")

        expected, actual = board.score_check(activities_completed=1)
        assert actual == expected, f"One activity should score {expected} with no completion bonus yet, got {actual}"
        board.close()
        quest.complete_prompt_activity("Prompt", "Prompt")  # the second activity reaches the target and finishes the quest
        quest.dismiss_quest_completion_overlay()

        expected, actual = board.score_check(activities_completed=2, quest_completed=True)
        assert actual == expected, f"Two activities should finish the quest with its bonus ({expected} points), got {actual}"
