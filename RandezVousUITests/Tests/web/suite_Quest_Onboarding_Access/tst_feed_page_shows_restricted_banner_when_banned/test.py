import pytest

from helpers.web.access_control_helper import AccessControlHelper
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_test_data import ORG_ID, OPEN_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, feed_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_feed_page_shows_restricted_banner_when_banned(desktop_safari_driver, banned_user):
    """QUEST_ONBOARDING_UX.md FeedPage audit: banned user now sees RestrictedBanner instead of
    the generic "Feed Not Available" error."""
    driver = desktop_safari_driver
    banned_user(TEST_USER_EMAIL, ORG_ID, OPEN_QUEST_ID)

    nav = HomepageHelper(driver)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.wait_until_signed_in()

    driver.get(feed_url(OPEN_QUEST_ID))

    access = AccessControlHelper(driver)
    assert access.is_restricted_banner_visible(custom_timeout=30), (
        "Expected FeedPage to show the RestrictedBanner for a banned user, not the generic feed-error state."
    )
    assert access.is_visible(access.back_to_quest_link), "Expected a way back to the quest page."
