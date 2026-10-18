import pytest

from helpers.ios import CustomQuestPage, FeedHelper, LeaderboardHelper, PhotoUploadHelper
from helpers.ios.feed_data_helper import (
    OTHER_EMAIL, OTHER_PASSWORD, TEST_EMAIL, TEST_PASSWORD, TEST_USERNAME,
    delete_stored_photos, delete_user_feed_posts, get_feed_posts, get_stored_photo, is_org_admin, photo_storage_path, photo_visibility,
    storage_read_status, utc_now, wait_for_feed_post,
)


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_private_photo_stays_out_of_feed(rv_driver, other_user_cleanup, distinct_photo):
    """An Admin Only photo scores but never reaches the feed, and a non-admin member can't read it from Cloud Storage."""
    removed = delete_user_feed_posts()  # start with none of this account's posts in the feed
    print(f"Cleared {removed} existing feed post(s) by {TEST_USERNAME}")
    print(f"Removed {delete_stored_photos()} leftover stored photo(s) for {TEST_USERNAME}")
    started = utc_now()

    CustomQuestPage(rv_driver).sign_in_and_join(TEST_EMAIL, TEST_PASSWORD)

    feed = FeedHelper(rv_driver)
    feed.open_feed()
    newest_before = feed.get_latest_post()
    feed.close_feed()

    PhotoUploadHelper(rv_driver).upload_photo(PhotoUploadHelper.ADMIN_ONLY)

    assert wait_for_feed_post(since=started, post_type="imagePost", timeout=8) is None, \
        "An Admin Only photo must not create a feed post"
    assert get_feed_posts(since=started) == [], "No feed doc of any kind should come from a private upload"
    assert photo_visibility() == "private", "An Admin Only upload should be filed under the user's private images"

    stored = get_stored_photo(private=True)
    assert stored is not None, "The private photo was not found in Cloud Storage"
    assert _is_near(stored.getpixel((stored.width // 4, stored.height * 3 // 4)), (255, 0, 255)) \
        and _is_near(stored.getpixel((stored.width * 3 // 4, stored.height // 4)), (0, 200, 0)), \
        "The stored photo is not the distinctive magenta/green image that was picked"
    assert get_stored_photo(private=False) is None, "A private upload must not also be stored as a public photo"

    feed.open_feed()
    assert feed.get_latest_post() == newest_before, "The Quest Feed screen's newest post changed after a private upload"
    feed.close_feed()

    leaderboard = LeaderboardHelper(rv_driver)
    expected = leaderboard.expected_score(activities_completed=1)
    assert leaderboard.get_score(TEST_USERNAME, expected_points=expected) == expected, \
        "A private photo should still complete the activity and score its points"

    # A different user joins the quest and looks at the feed: the private photo must not have reached it.
    CustomQuestPage(rv_driver).sign_in_and_join(OTHER_EMAIL, OTHER_PASSWORD)

    feed.open_feed()
    assert feed.get_latest_post() == newest_before, \
        "Another user's feed shows a newer post than before the private upload; the photo may have leaked"

    # Storage rules: the owner can read the file, a joined non-admin member cannot.
    assert not is_org_admin(OTHER_EMAIL), f"{OTHER_EMAIL} is an org admin, so it is the wrong account for this check"
    private_path = photo_storage_path(TEST_EMAIL, private=True)
    assert storage_read_status(TEST_EMAIL, private_path) == 200, \
        "Control failed: the owner could not read their own private photo, so the check below proves nothing"
    assert storage_read_status(OTHER_EMAIL, private_path) == 403, \
        "A non-admin quest member was allowed to read someone else's private photo from Storage"


def _is_near(pixel, expected, tolerance=40):
    """JPEG conversion shifts colors slightly; compare each channel within a tolerance."""
    return all(abs(a - b) <= tolerance for a, b in zip(pixel, expected))
