import pytest

from helpers.ios import CustomQuestPage
from helpers.ios.feed_data_helper import prompt_response, unique_text, utc_now, wait_for_feed_post
from helpers.ios.ios_test_data import TEST_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_private_prompt_stays_out_of_feed(rv_driver):
    """A Private open-prompt response is stored privately and never reaches the quest feed."""
    text = unique_text("private-prompt")
    started = utc_now()
    quest = CustomQuestPage(rv_driver)
    quest.sign_in_and_join()
    quest.complete_prompt_activity("Prompt", text, visibility="Private")

    assert prompt_response(public=False) == text, "A Private response should be stored as a private response"
    assert prompt_response(public=True) is None, "A Private response must not be stored publicly"
    assert wait_for_feed_post(since=started, predicate=lambda p: p.get("message") == text, timeout=8) is None, \
        "A private prompt response must not create a feed comment"
