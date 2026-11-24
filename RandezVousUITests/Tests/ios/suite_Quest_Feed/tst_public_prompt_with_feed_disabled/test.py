import pytest

from helpers.common.access_data_helper import edited_quest
from helpers.ios import CustomQuestPage
from helpers.ios.feed_data_helper import ORG_ID, QUEST_ID, prompt_response, unique_text, utc_now, wait_for_feed_post
from helpers.ios.ios_test_data import TEST_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_public_prompt_with_feed_disabled(rv_driver):
    """With the feed turned off, a Public prompt response is still recorded but no feed comment is made."""
    text = unique_text("public-prompt-no-feed")
    started = utc_now()
    with edited_quest(ORG_ID, QUEST_ID, hasFeed=False):  # restored even if the test fails
        quest = CustomQuestPage(rv_driver)
        quest.sign_in_and_join()
        quest.complete_prompt_activity("Prompt", text, visibility="Public")

        assert prompt_response(public=True) == text, "The response should still be recorded when the feed is off"
        assert wait_for_feed_post(since=started, predicate=lambda p: p.get("message") == text, timeout=8) is None, \
            "A quest with the feed disabled must not get a feed comment"
