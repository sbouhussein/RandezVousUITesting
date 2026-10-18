import pytest

from helpers.ios import CustomQuestPage



@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_fail_to_complete_trivia_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "test-automation-quest"
    activity = "Trivia"
    wrong_response = "Triviq"

    custom_quest = CustomQuestPage(rv_driver)

    custom_quest.sign_in_and_join(email, password, quest)

    custom_quest.attempt_trivia_activity(activity, wrong_response)

    assert custom_quest.is_trivia_incorrect_message_visible(), \
        "Expected 'Not quite, try again.' to appear for a wrong answer"
