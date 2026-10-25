import pytest

from helpers.web import AccessControlHelper, HomepageHelper, OnboardingPageHelper
from helpers.web.quest_test_data import ORG_ID, OPEN_QUEST_ID, TEST_USER_EMAIL, onboarding_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_onboarding_desktop_shows_restricted_banner_when_banned(desktop_safari_driver, banned_user):
    """Start Quest shows RestrictedBanner for a banned user; uses the open quest because a restricted one hits the domain check first."""
    banned_user(TEST_USER_EMAIL, ORG_ID, OPEN_QUEST_ID)
    HomepageHelper(desktop_safari_driver).sign_in_and_open(onboarding_url(OPEN_QUEST_ID))
    OnboardingPageHelper(desktop_safari_driver).click_start_quest()

    assert AccessControlHelper(desktop_safari_driver).is_restricted_banner_visible(custom_timeout=15), \
        "Expected the RestrictedBanner after a banned user's join attempt failed"
