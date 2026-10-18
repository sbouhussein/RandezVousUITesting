import pytest

from helpers.web import AccessControlHelper, HomepageHelper, OnboardingPageHelper
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_onboarding_desktop_shows_google_signin_for_wrong_provider(desktop_safari_driver):
    """An email/password account on a domain-restricted quest gets "Sign in with Google", not "Switch accounts"."""
    driver = desktop_safari_driver

    nav = HomepageHelper(driver)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.wait_until_signed_in()

    driver.get(onboarding_url(RESTRICTED_QUEST_ID))

    onboarding = OnboardingPageHelper(driver)
    onboarding.click_start_quest()

    access = AccessControlHelper(driver)
    assert access.is_visible(access.sign_in_with_google_button, custom_timeout=15), (
        "Expected the wrong-provider panel's 'Sign in with Google' button."
    )
    assert not access.is_visible(access.switch_accounts_button, custom_timeout=2), (
        "Did not expect 'Switch accounts' for an account with no linked Google provider."
    )
