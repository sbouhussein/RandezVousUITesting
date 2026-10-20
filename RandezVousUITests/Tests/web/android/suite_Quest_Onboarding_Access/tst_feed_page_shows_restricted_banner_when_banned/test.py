import pytest

from helpers.web import AccessControlHelper, HomepageHelper
from helpers.web.quest_test_data import ORG_ID, OPEN_QUEST_ID, TEST_USER_EMAIL, feed_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_feed_page_shows_restricted_banner_when_banned(desktop_safari_driver, banned_user):
    """A banned user sees RestrictedBanner instead of the generic "Feed Not Available" error."""
    banned_user(TEST_USER_EMAIL, ORG_ID, OPEN_QUEST_ID)
    HomepageHelper(desktop_safari_driver).sign_in_and_open(feed_url(OPEN_QUEST_ID))

    access = AccessControlHelper(desktop_safari_driver)
    assert access.is_restricted_banner_visible(custom_timeout=30), "Expected the RestrictedBanner, not the generic feed error"
    assert access.is_visible(access.back_to_quest_link), "Expected a way back to the quest page"
