import pytest

from helpers.ios import CustomQuestPage, FeedHelper, LeaderboardHelper, PhotoUploadHelper
from helpers.ios.feed_data_helper import (
    get_stored_photo, is_org_admin, photo_visibility, private_photo_read_statuses,
    reset_photo_state, stored_photo_matches, utc_now, wait_for_feed_post,
)
from helpers.ios.ios_test_data import OTHER_EMAIL, OTHER_PASSWORD, TEST_EMAIL

MAGENTA_AND_GREEN = ((255, 0, 255), (0, 200, 0))  # the halves of fixtures/private_photo.png


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_private_photo_stays_out_of_feed(rv_driver, other_user_cleanup, distinct_photo):
    """An Admin Only photo scores but never reaches the feed, and a non-admin member can't read it from Cloud Storage."""
    reset_photo_state()
    started = utc_now()
    CustomQuestPage(rv_driver).sign_in_and_join()
    feed = FeedHelper(rv_driver)
    newest_before = feed.peek_latest_post()
    PhotoUploadHelper(rv_driver).upload_photo(PhotoUploadHelper.ADMIN_ONLY)

    assert wait_for_feed_post(since=started, timeout=8) is None, "A private upload must not create any feed doc"
    assert photo_visibility() == "private", "An Admin Only upload should be filed under the user's private images"
    assert stored_photo_matches(MAGENTA_AND_GREEN), "The stored private photo should be the distinctive image that was picked"
    assert get_stored_photo(private=False) is None, "A private upload must not also be stored as a public photo"
    assert feed.peek_latest_post() == newest_before, "The Quest Feed screen's newest post changed after a private upload"
    expected, actual = LeaderboardHelper(rv_driver).score_check(activities_completed=1)
    assert actual == expected, f"A private photo should still score its points: expected {expected}, got {actual}"

    # A second, non-admin member sees an unchanged feed and is refused the file by Storage's rules.
    CustomQuestPage(rv_driver).sign_in_and_join(OTHER_EMAIL, OTHER_PASSWORD)
    assert feed.peek_latest_post() == newest_before, "Another user's feed shows a newer post; the photo may have leaked"
    assert not is_org_admin(OTHER_EMAIL), f"{OTHER_EMAIL} is an org admin, so it is the wrong account for this check"
    owner_status, other_status = private_photo_read_statuses(TEST_EMAIL, OTHER_EMAIL)
    assert owner_status == 200, "Control failed: the owner could not read their own private photo"
    assert other_status == 403, "A non-admin quest member was allowed to read someone else's private photo"
