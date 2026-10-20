import pytest

from helpers.ios import CustomQuestPage, FeedHelper, PhotoUploadHelper
from helpers.ios.feed_data_helper import PHOTO_ACTIVITY_KEY, photo_visibility, unique_text, utc_now, wait_for_feed_post
from helpers.ios.ios_test_data import TEST_EMAIL, TEST_USERNAME

PUBLIC, ADMIN_ONLY = PhotoUploadHelper.PUBLIC, PhotoUploadHelper.ADMIN_ONLY


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_public_photo_posts_to_feed(rv_driver):
    """The visibility toggle swaps the caption field, and a Public photo with a caption becomes a feed post."""
    caption = unique_text("public-photo")
    started = utc_now()
    CustomQuestPage(rv_driver).sign_in_and_join()
    upload = PhotoUploadHelper(rv_driver)
    upload.select_photo()

    assert upload.visibility_state() == (PUBLIC, True), "Public with a caption field should be the default"
    upload.select_visibility(ADMIN_ONLY)
    assert upload.visibility_state() == (ADMIN_ONLY, False), "Admin Only should hide the caption (no feed post)"
    upload.select_visibility(PUBLIC)
    assert upload.visibility_state() == (PUBLIC, True), "Switching back should restore Public and the caption field"
    upload.add_caption(caption)
    upload.submit()
    upload.finish_upload()

    post = wait_for_feed_post(since=started, post_type="imagePost")
    assert post is not None, "Expected a public photo upload to create an imagePost in the quest feed"
    assert post.get("activityId") == PHOTO_ACTIVITY_KEY, f"Post is for the wrong activity: {post.get('activityId')}"
    assert post.get("caption") == caption, f"Feed post should carry the caption, got: {post.get('caption')!r}"
    assert photo_visibility() == "public", "A Public upload should be filed under the user's public images"

    feed = FeedHelper(rv_driver)
    feed.open_feed()
    shown = feed.find_post(caption)
    assert shown is not None, f"Expected a post with caption '{caption}' on the Quest Feed screen"
    assert shown["author"] == TEST_USERNAME, f"Post should be by {TEST_USERNAME}, got {shown['author']}"
    assert shown["posted_for"] == "Photo", f"Post should read 'Posted for: Photo', got {shown['posted_for']}"
