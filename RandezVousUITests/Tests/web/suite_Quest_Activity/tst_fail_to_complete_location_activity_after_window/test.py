from datetime import timedelta

import pytest

from helpers.common.access_data_helper import edited_activity, event_start
from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, ACTIVITY_QUEST_LOCATION, BASE_URL, ORG_ID, TEST_USER_EMAIL

LOCATION_ACTIVITY_ID = 1004


@pytest.mark.usefixtures("fresh_web_backend")
@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_fail_to_complete_location_activity_after_window(desktop_safari_driver):
    """A location activity's check-in window closes 24 hours after its start; the dialog then says the window has passed."""
    driver = desktop_safari_driver
    with edited_activity(ORG_ID, ACTIVITY_QUEST_ID, LOCATION_ACTIVITY_ID, customStartString=event_start(timedelta(hours=-25))):
        driver.get(BASE_URL)
        HomepageHelper(driver).sign_in_and_find_quest(ACTIVITY_QUEST_ID)
        quest = QuestHelper(driver)
        quest.mock_geo_location(*ACTIVITY_QUEST_LOCATION)
        quest.click(quest.location_activity_locator)
        quest.click(quest.complete_location_button)

        assert quest.is_window_passed_visible(), "Expected 'Window has passed' for a location event more than 24 hours old"
        assert not quest.is_visible(quest.check_location_button, custom_timeout=2), "The location check should not be offered"
