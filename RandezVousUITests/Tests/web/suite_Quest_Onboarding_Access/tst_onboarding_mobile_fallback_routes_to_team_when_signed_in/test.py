import pytest

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.onboarding_helper import OnboardingPageHelper
from helpers.web.quest_test_data import TEAM_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url, team_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_onboarding_mobile_fallback_routes_to_team_when_signed_in(mobile_chrome_driver):
    """QUEST_ONBOARDING_UX.md row 5: Open in App fallback now routes a signed-in visitor
    to the team picker (`/team`) instead of the bare quest page."""
    driver = mobile_chrome_driver

    nav = HomepageHelper(driver)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.wait_until_signed_in()

    driver.get(onboarding_url(TEAM_QUEST_ID))

    onboarding = OnboardingPageHelper(driver)
    href = onboarding.get_open_in_app_href()

    assert href == team_url(TEAM_QUEST_ID), f"Expected the team-picker fallback, got: {href}"
