import pytest

from helpers.common.access_data_helper import edited_quest
from helpers.ios import CustomQuestPage, PhotoUploadHelper
from helpers.ios.feed_data_helper import ORG_ID, QUEST_ID, photo_visibility, utc_now, wait_for_feed_post
from helpers.ios.ios_test_data import TEST_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_public_photo_with_feed_disabled(rv_driver):
    """With the feed turned off, a Public photo is still saved but no feed post is made."""
    started = utc_now()
    with edited_quest(ORG_ID, QUEST_ID, hasFeed=False):  # restored even if the test fails
        CustomQuestPage(rv_driver).sign_in_and_join()
        PhotoUploadHelper(rv_driver).upload_photo(PhotoUploadHelper.PUBLIC)

        assert photo_visibility() == "public", "The photo should still be filed as public when the feed is off"
        assert wait_for_feed_post(since=started, post_type="imagePost", timeout=8) is None, \
            "A quest with the feed disabled must not get a photo feed post"
