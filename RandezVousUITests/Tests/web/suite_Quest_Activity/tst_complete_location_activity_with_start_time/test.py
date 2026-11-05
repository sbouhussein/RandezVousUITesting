from datetime import timedelta

import pytest

from helpers.common.access_data_helper import edited_activity, event_start
from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, ACTIVITY_QUEST_LOCATION, BASE_URL, ORG_ID, TEST_USER_EMAIL

LOCATION_ACTIVITY_ID = 1004


@pytest.mark.usefixtures("fresh_web_backend")
@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_location_activity_with_start_time(desktop_safari_driver):
    """A location activity with a start time can still be completed 23 hours after it starts (it closes at 24)."""
    driver = desktop_safari_driver
    with edited_activity(ORG_ID, ACTIVITY_QUEST_ID, LOCATION_ACTIVITY_ID, customStartString=event_start(timedelta(hours=-23))):
        driver.get(BASE_URL)
        HomepageHelper(driver).sign_in_and_find_quest(ACTIVITY_QUEST_ID)
        quest = QuestHelper(driver)
        quest.mock_geo_location(*ACTIVITY_QUEST_LOCATION)
        quest.complete_location_activity()

        assert quest.verify_activity_completion("Location"), "The location event activity should be completable inside its window"
