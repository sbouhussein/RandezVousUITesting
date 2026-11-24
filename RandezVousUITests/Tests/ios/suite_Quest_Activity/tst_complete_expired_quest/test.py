import pytest

from helpers.common.access_data_helper import preload_progress, quest_completed_date
from helpers.ios import CustomQuestPage, LoginPageHelper, QuestHelper
from helpers.ios.ios_test_data import TEST_EMAIL, TEST_PASSWORD
from helpers.web.quest_test_data import EXPIRED_QUEST_ID, ORG_ID

# Both activities of the expired fixture, finished "before" it ended.
FINISHED = {"honor challenge:1000": f"{EXPIRED_QUEST_ID}-1000", "prompt challenge:1002": f"{EXPIRED_QUEST_ID}-1002"}


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_complete_expired_quest(rv_driver):
    """A user who finished every activity before the quest ended can still complete the quest afterwards."""
    preload_progress(TEST_EMAIL, ORG_ID, EXPIRED_QUEST_ID, FINISHED)
    app, quest = QuestHelper(rv_driver), CustomQuestPage(rv_driver)
    app.sign_out_if_signed_in()
    LoginPageHelper(rv_driver).login_with_credentials(TEST_EMAIL, TEST_PASSWORD)
    app.navigate_to_quests_tab()
    app.click_custom_quest_button()
    quest.enter_quest_code(EXPIRED_QUEST_ID)
    quest.click_find_quest()
    quest.click_start_quest()

    assert quest.is_quest_completed_message_visible(), "An ended quest with every activity finished should still complete"
    assert quest_completed_date(TEST_EMAIL, EXPIRED_QUEST_ID), "The completion should be saved on the user's quest history"
