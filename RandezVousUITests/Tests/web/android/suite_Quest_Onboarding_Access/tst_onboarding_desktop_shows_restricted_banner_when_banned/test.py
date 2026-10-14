import pytest

from helpers.web.access_control_helper import AccessControlHelper
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.onboarding_helper import OnboardingPageHelper
from helpers.web.quest_test_data import ORG_ID, OPEN_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_onboarding_desktop_shows_restricted_banner_when_banned(desktop_safari_driver, banned_user):
    """QUEST_ONBOARDING_UX.md row 12: DefaultActionCard's "Start Quest" -> AccessErrorPanel
    renders RestrictedBanner for a banned user, the same shared component AppActionCard uses on
    mobile (tst_onboarding_mobile_shows_restricted_banner_when_banned).

    Uses OPEN_QUEST_ID, not RESTRICTED_QUEST_ID: /api/quest/join checks accessPolicy (domain)
    before the ban check (backend/routes/quests.js), and TEST_USER_EMAIL has no linked Google
    provider, so a domain-restricted quest would hit the wrong-provider panel first, not the
    ban -- see tst_onboarding_desktop_shows_google_signin_for_wrong_provider for that case."""
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
