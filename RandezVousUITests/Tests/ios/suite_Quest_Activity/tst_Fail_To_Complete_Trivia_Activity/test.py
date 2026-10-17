import pytest

from helpers.ios.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.ios.login_page_helper import LoginPageHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_fail_to_complete_trivia_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "test-automation-quest"
    activity = "Trivia"
    wrong_response = "Triviq"

    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    quest_helper = QuestHelper(rv_driver)

    quest_helper.sign_out_if_signed_in()
    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)

    custom_quest.attempt_trivia_activity(activity, wrong_response)

    assert custom_quest.is_trivia_incorrect_message_visible(), \
        "Expected 'Not quite, try again.' to appear for a wrong answer"
