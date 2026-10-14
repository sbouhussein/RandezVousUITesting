import pytest

from helpers.web.access_control_helper import AccessControlHelper
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.onboarding_helper import OnboardingPageHelper
from helpers.web.quest_test_data import ORG_ID, OPEN_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_onboarding_mobile_shows_restricted_banner_when_banned(mobile_chrome_driver, banned_user):
    """QUEST_ONBOARDING_UX.md row 6: AppActionCard now renders RestrictedBanner for a banned
    user, same as DefaultActionCard."""
    driver = mobile_chrome_driver
    banned_user(TEST_USER_EMAIL, ORG_ID, OPEN_QUEST_ID)

    nav = HomepageHelper(driver)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.wait_until_signed_in()

    driver.get(onboarding_url(OPEN_QUEST_ID))

    onboarding = OnboardingPageHelper(driver)
    onboarding.click_continue_on_web()

    access = AccessControlHelper(driver)
    assert access.is_restricted_banner_visible(custom_timeout=15), (
        "Expected the RestrictedBanner after a banned user's join attempt failed."
    )
