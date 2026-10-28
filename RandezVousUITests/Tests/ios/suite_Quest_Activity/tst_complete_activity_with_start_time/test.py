from datetime import timedelta

import pytest

from helpers.common.access_data_helper import edited_activity, event_start
from helpers.ios import CustomQuestPage, LeaderboardHelper
from helpers.ios.ios_test_data import TEST_EMAIL
from helpers.web.quest_test_data import OPEN_QUEST_ID, ORG_ID

HONOR_ACTIVITY_ID = 1000  # the open quest's only activity
STARTS = [("30 minutes before it starts", timedelta(minutes=30)), ("23 hours after it started", timedelta(hours=-23))]


@pytest.mark.parametrize("when,offset", STARTS, ids=[name for name, _ in STARTS])
@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_complete_activity_with_start_time(rv_driver, when, offset):
    """An honor activity with a start time can be completed from just before the event begins to a day after."""
    with edited_activity(ORG_ID, OPEN_QUEST_ID, HONOR_ACTIVITY_ID, customStartString=event_start(offset)):
        quest = CustomQuestPage(rv_driver)
        quest.sign_in_and_join(quest_code=OPEN_QUEST_ID)
        quest.complete_honor_based_activity("Honor", click_back=False)  # the quest's only activity, so it also finishes the quest
        quest.dismiss_quest_completion_overlay()

        expected, actual = LeaderboardHelper(rv_driver).score_check(activities_completed=1, quest_completed=True)
        assert actual == expected, f"The event activity should be completable {when}: expected {expected} points, got {actual}"
