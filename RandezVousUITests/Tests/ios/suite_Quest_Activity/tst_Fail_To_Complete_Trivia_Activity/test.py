import pytest

from helpers.ios import CustomQuestPage
from helpers.ios.ios_test_data import TEST_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_fail_to_complete_trivia_activity(rv_driver):
    quest = CustomQuestPage(rv_driver)
    quest.sign_in_and_join()
    quest.attempt_trivia_activity("Trivia", "Triviq")

    assert quest.is_trivia_incorrect_message_visible(), "Expected 'Not quite, try again.' for a wrong answer"
