from datetime import timedelta

import pytest

from helpers.common.access_data_helper import edited_activity, event_start
from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import BASE_URL, OPEN_QUEST_ID, ORG_ID, TEST_USER_EMAIL

HONOR_ACTIVITY_ID = 1000  # the open quest's only activity


@pytest.mark.usefixtures("fresh_web_backend")
@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_fail_to_complete_activity_before_start_time(desktop_safari_driver):
    """An activity with a start time can't be completed until its window opens, 1 hour before the start."""
    driver = desktop_safari_driver
    with edited_activity(ORG_ID, OPEN_QUEST_ID, HONOR_ACTIVITY_ID, customStartString=event_start(timedelta(hours=2))):
        driver.get(BASE_URL)
        HomepageHelper(driver).sign_in_and_find_quest(OPEN_QUEST_ID)
        quest = QuestHelper(driver)
        quest.click(quest.honor_activity_locator)

        assert quest.is_not_yet_available_visible(), "Expected 'Not Yet Available' on an event more than an hour away"
        assert not quest.is_visible(quest.complete_honor_button, custom_timeout=2), "The Complete button should be replaced"
