import pytest

from helpers.common.access_data_helper import preload_progress, quest_completed_date
from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import EXPIRED_QUEST_ID, ORG_ID, TEST_USER_EMAIL, quest_url

# Both activities of the expired fixture, finished "before" it ended.
FINISHED = {"honor challenge:1000": f"{EXPIRED_QUEST_ID}-1000", "prompt challenge:1002": f"{EXPIRED_QUEST_ID}-1002"}


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_expired_quest(desktop_safari_driver):
    """A user who finished every activity before the quest ended can still complete the quest afterwards."""
    preload_progress(TEST_USER_EMAIL, ORG_ID, EXPIRED_QUEST_ID, FINISHED)
    HomepageHelper(desktop_safari_driver).sign_in_and_open(quest_url(EXPIRED_QUEST_ID))
    quest = QuestHelper(desktop_safari_driver)

    assert quest.verify_quest_completion(), "An ended quest with every activity finished should still complete"
    assert quest_completed_date(TEST_USER_EMAIL, EXPIRED_QUEST_ID), "The completion should be saved on the user's quest history"
