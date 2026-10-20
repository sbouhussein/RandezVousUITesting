import pytest

from helpers.web import AccessControlHelper, HomepageHelper, OnboardingPageHelper
from helpers.web.quest_test_data import ORG_ID, OPEN_QUEST_ID, TEST_USER_EMAIL, onboarding_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_onboarding_mobile_shows_restricted_banner_when_banned(mobile_chrome_driver, banned_user):
    """AppActionCard shows RestrictedBanner for a banned user."""
    banned_user(TEST_USER_EMAIL, ORG_ID, OPEN_QUEST_ID)
    HomepageHelper(mobile_chrome_driver).sign_in_and_open(onboarding_url(OPEN_QUEST_ID))
    OnboardingPageHelper(mobile_chrome_driver).click_continue_on_web()

    assert AccessControlHelper(mobile_chrome_driver).is_restricted_banner_visible(custom_timeout=15), \
        "Expected the RestrictedBanner after a banned user's join attempt failed"
