import pytest

from helpers.web import AccessControlHelper, HomepageHelper, OnboardingPageHelper
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID, TEST_USER_EMAIL, onboarding_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_onboarding_desktop_shows_google_signin_for_wrong_provider(desktop_safari_driver):
    """An email/password account on a domain-restricted quest gets "Sign in with Google", not "Switch accounts"."""
    HomepageHelper(desktop_safari_driver).sign_in_and_open(onboarding_url(RESTRICTED_QUEST_ID))
    OnboardingPageHelper(desktop_safari_driver).click_start_quest()

    access = AccessControlHelper(desktop_safari_driver)
    assert access.is_visible(access.sign_in_with_google_button, custom_timeout=15), "Expected 'Sign in with Google'"
    assert not access.is_visible(access.switch_accounts_button, custom_timeout=2), \
        "Did not expect 'Switch accounts' for an account with no linked Google provider"
