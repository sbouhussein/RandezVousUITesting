import pytest

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_photo_activity(desktop_safari_driver):
    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.find_quest(ACTIVITY_QUEST_ID)

    quest.complete_photo_activity()

    assert quest.verify_activity_completion("Photo"), "Photo activity was not marked as completed!"
