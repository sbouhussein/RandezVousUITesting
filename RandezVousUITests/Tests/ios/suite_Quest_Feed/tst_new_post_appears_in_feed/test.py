import pytest

from helpers.ios import CustomQuestPage, FeedHelper
from helpers.ios.feed_data_helper import unique_text, utc_now, wait_for_feed_post
from helpers.ios.ios_test_data import TEST_EMAIL, TEST_USERNAME


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_new_post_appears_in_feed(rv_driver):
    """A message from the New post button appears under the user's name and is stored as a free-form comment."""
    text = unique_text("new-post")
    started = utc_now()
    CustomQuestPage(rv_driver).sign_in_and_join()
    feed = FeedHelper(rv_driver)
    feed.open_feed()
    feed.compose_post(text)

    post = wait_for_feed_post(since=started, post_type="comment", predicate=lambda p: p.get("message") == text)
    assert post is not None, f"Expected a comment with message '{text}' in the quest feed"
    assert post.get("activityId") is None, f"A free-form post shouldn't be tied to an activity: {post.get('activityId')}"
    shown = feed.find_post(text)
    assert shown is not None, f"Expected '{text}' on the Quest Feed screen"
    assert shown["author"] == TEST_USERNAME, f"Post should be by {TEST_USERNAME}, got {shown['author']}"
    assert shown["in_response_to"] is None, "A free-form post isn't a response to an activity"
