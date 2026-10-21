import pytest

from helpers.ios import CustomQuestPage, GuestJoinHelper, LoginPageHelper, QuestHelper
from helpers.ios.ios_test_data import GUEST_USERNAME, QUEST_ID


@pytest.mark.cleanup(type="username", value=GUEST_USERNAME)
def test_log_in_with_code_entry_point(rv_driver):
    QuestHelper(rv_driver).sign_out_if_signed_in()
    LoginPageHelper(rv_driver).click_login_with_code()
    quest = CustomQuestPage(rv_driver)
    quest.enter_quest_code(QUEST_ID)
    quest.click_find_quest()
    GuestJoinHelper(rv_driver).finish_onboarding(required=True)
