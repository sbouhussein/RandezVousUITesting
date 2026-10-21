import pytest

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, TEST_USER_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_prompt_activity(desktop_safari_driver):
    HomepageHelper(desktop_safari_driver).sign_in_and_find_quest(ACTIVITY_QUEST_ID)
    quest = QuestHelper(desktop_safari_driver)
    quest.complete_prompt_activity("Prompt")

    assert quest.verify_activity_completion("Prompt"), "Prompt activity was not marked as completed!"
