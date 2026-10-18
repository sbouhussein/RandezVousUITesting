import pytest

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_honor_activity(desktop_safari_driver):
    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.find_quest(ACTIVITY_QUEST_ID)

    quest.complete_honor_activity()

    assert quest.verify_activity_completion("Honor Code"), "Honor activity was not marked as completed!"
