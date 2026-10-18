import pytest

from helpers.ios import CustomQuestPage, FeedHelper, PhotoUploadHelper
from helpers.ios.feed_data_helper import (
    PHOTO_ACTIVITY_KEY, TEST_EMAIL, TEST_PASSWORD, TEST_USERNAME,
    photo_visibility, unique_text, utc_now, wait_for_feed_post,
)


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_public_photo_posts_to_feed(rv_driver):
    """The visibility toggle swaps the caption field, and a Public photo with a caption becomes a feed post."""
    caption = unique_text("public-photo")
    started = utc_now()

    CustomQuestPage(rv_driver).sign_in_and_join(TEST_EMAIL, TEST_PASSWORD)

    upload = PhotoUploadHelper(rv_driver)
    upload.select_photo()

    assert "everyone on" in upload.get_visibility_text(), f"Public should be the default: {upload.get_visibility_text()}"
    assert upload.is_caption_field_visible(), "A public upload to a quest with a feed should offer a caption"

    upload.select_visibility(PhotoUploadHelper.ADMIN_ONLY)
    assert "admin of" in upload.get_visibility_text(), f"Admin Only should limit visibility: {upload.get_visibility_text()}"
    assert not upload.is_caption_field_visible(), "A private upload makes no feed post, so there should be no caption field"

    upload.select_visibility(PhotoUploadHelper.PUBLIC)
    assert "everyone on" in upload.get_visibility_text(), "Switching back to Public should restore its visibility text"
    assert upload.is_caption_field_visible(), "Switching back to Public should bring the caption field back"

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
