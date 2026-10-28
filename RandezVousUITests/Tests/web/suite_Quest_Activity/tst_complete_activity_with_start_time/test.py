from datetime import timedelta

import pytest

from helpers.common.access_data_helper import edited_activity, event_start
from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import BASE_URL, OPEN_QUEST_ID, ORG_ID, TEST_USER_EMAIL

HONOR_ACTIVITY_ID = 1000  # the open quest's only activity
# rvsite opens an event activity 1 hour before it starts; only location activities also close, 24 hours after the start.
STARTS = [("30 minutes before it starts", timedelta(minutes=30)), ("23 hours after it started", timedelta(hours=-23))]


@pytest.mark.parametrize("when,offset", STARTS, ids=[name for name, _ in STARTS])
@pytest.mark.usefixtures("fresh_web_backend")
@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_activity_with_start_time(desktop_safari_driver, when, offset):
    """An honor activity with a start time can be completed from just before the event begins to a day after."""
    driver = desktop_safari_driver
    with edited_activity(ORG_ID, OPEN_QUEST_ID, HONOR_ACTIVITY_ID, customStartString=event_start(offset)):
        driver.get(BASE_URL)
        HomepageHelper(driver).sign_in_and_find_quest(OPEN_QUEST_ID)
        quest = QuestHelper(driver)
        quest.complete_honor_activity()

        assert quest.verify_quest_completion(), f"The event activity should be completable {when}"
