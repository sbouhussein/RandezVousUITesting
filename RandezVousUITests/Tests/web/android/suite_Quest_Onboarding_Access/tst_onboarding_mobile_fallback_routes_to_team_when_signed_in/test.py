import pytest

from helpers.web import HomepageHelper, OnboardingPageHelper
from helpers.web.quest_test_data import TEAM_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url, team_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_onboarding_mobile_fallback_routes_to_team_when_signed_in(mobile_chrome_driver):
    """The Open in App fallback sends a signed-in visitor to the team picker (/team)."""
    driver = mobile_chrome_driver

    nav = HomepageHelper(driver)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.wait_until_signed_in()

    driver.get(onboarding_url(TEAM_QUEST_ID))

    onboarding = OnboardingPageHelper(driver)
    href = onboarding.get_open_in_app_href()

    assert href == team_url(TEAM_QUEST_ID), f"Expected the team-picker fallback, got: {href}"
