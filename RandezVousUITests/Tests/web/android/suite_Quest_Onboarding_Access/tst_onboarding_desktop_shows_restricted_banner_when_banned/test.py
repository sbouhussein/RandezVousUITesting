import pytest

from helpers.web import AccessControlHelper, HomepageHelper, OnboardingPageHelper
from helpers.web.quest_test_data import ORG_ID, OPEN_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_onboarding_desktop_shows_restricted_banner_when_banned(desktop_safari_driver, banned_user):
    """Start Quest shows RestrictedBanner for a banned user; uses the open quest because a restricted one hits the domain check first."""
    driver = desktop_safari_driver
    banned_user(TEST_USER_EMAIL, ORG_ID, OPEN_QUEST_ID)

    nav = HomepageHelper(driver)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.wait_until_signed_in()

    driver.get(onboarding_url(OPEN_QUEST_ID))

    onboarding = OnboardingPageHelper(driver)
    onboarding.click_start_quest()

    access = AccessControlHelper(driver)
    assert access.is_restricted_banner_visible(custom_timeout=15), (
        "Expected DefaultActionCard to show the RestrictedBanner after a banned user's join attempt failed."
    )
