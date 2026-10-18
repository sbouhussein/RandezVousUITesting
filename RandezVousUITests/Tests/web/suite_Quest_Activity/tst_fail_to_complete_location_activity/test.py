import pytest

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD

OUT_OF_RANGE_LOCATION = (42.282778, -154.829444)


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_fail_to_complete_location_activity(desktop_safari_driver):
    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.find_quest(ACTIVITY_QUEST_ID)

    quest.mock_geo_location(*OUT_OF_RANGE_LOCATION)
    quest.check_location()

    assert quest.is_location_error_visible(), "Expected a location verification error when out of range"
