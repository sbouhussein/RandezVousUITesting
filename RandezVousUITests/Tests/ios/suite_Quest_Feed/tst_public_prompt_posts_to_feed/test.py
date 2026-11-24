import pytest

from helpers.ios import CustomQuestPage
from helpers.ios.feed_data_helper import PROMPT_ACTIVITY_KEY, prompt_response, unique_text, utc_now, wait_for_feed_post
from helpers.ios.ios_test_data import TEST_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_public_prompt_posts_to_feed(rv_driver):
    """A Public open-prompt response becomes a comment in the quest feed and is stored as a public response."""
    text = unique_text("public-prompt")
    started = utc_now()
    quest = CustomQuestPage(rv_driver)
    quest.sign_in_and_join()
    quest.complete_prompt_activity("Prompt", text, visibility="Public")

    post = wait_for_feed_post(since=started, predicate=lambda p: p.get("message") == text)
    assert post is not None, "Expected a public prompt response to appear as a quest feed comment"
    assert post.get("activityId") == PROMPT_ACTIVITY_KEY, f"The comment is for the wrong activity: {post.get('activityId')}"
    assert prompt_response(public=True) == text, "A Public response should be stored as a public response"
    assert prompt_response(public=False) is None, "A Public response must not also be stored privately"
