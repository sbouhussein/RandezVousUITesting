import pytest

from helpers.web.access_control_helper import AccessControlHelper
from helpers.web.firebase_test_data_helper import clear_stale_grant, has_quest_grant
from helpers.web.google_identity_helper import GoogleIdentityHelper
from helpers.web.onboarding_helper import OnboardingPageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import (
    GOOGLE_WRONG_DOMAIN_EMAIL, GOOGLE_WRONG_DOMAIN_UID, RESTRICTED_QUEST_ID, onboarding_url,
)


@pytest.mark.cleanup(type="email", value=GOOGLE_WRONG_DOMAIN_EMAIL)
def test_join_domain_quest_blocked_for_wrong_google_domain(desktop_safari_driver):
    """Unhappy path for a domain-restricted quest: a signed-in Google user on the WRONG domain tries to
    join `web-restricted` (randezvous.com only) and is refused -- they see the domain error with a
    "Switch accounts" remedy, never reach the quest, and no access grant is created.

    The user is a fabricated QA account with a `google.com` provider entry on @gmail.com (see
    seed_qa_web_fixtures.py), signed in by custom token. That makes the backend's join check reject on the
    wrong-DOMAIN branch -- distinct from an email/password account, which is rejected on the wrong-PROVIDER
    branch ("Sign in with Google"; covered by tst_onboarding_desktop_shows_google_signin_for_wrong_provider)."""
    driver = desktop_safari_driver

    # A leftover grant would bypass the domain check this test is about.
    clear_stale_grant(GOOGLE_WRONG_DOMAIN_EMAIL, RESTRICTED_QUEST_ID)

    GoogleIdentityHelper(driver).sign_in(GOOGLE_WRONG_DOMAIN_UID)

    driver.get(onboarding_url(RESTRICTED_QUEST_ID))
    OnboardingPageHelper(driver).click_start_quest()

    access = AccessControlHelper(driver)
    quest = QuestHelper(driver)

    assert access.is_wrong_domain_message_visible(custom_timeout=30), \
        "Expected the wrong-domain error for a Google user outside the allowed domain"
    message = access.get_wrong_domain_message()
    assert "@randezvous.com" in message and "@gmail.com" in message, \
        f"Expected the message to name the required and the actual domain, got: {message!r}"
    assert access.is_visible(access.switch_accounts_button, custom_timeout=5), \
        "Expected a 'Switch accounts' remedy for a wrong-domain Google user"
    assert not access.is_visible(access.sign_in_with_google_button, custom_timeout=2), \
        "'Sign in with Google' is the wrong-provider remedy; this user already is a Google user"
    assert not access.is_restricted_banner_visible(custom_timeout=2), \
        "This is a domain refusal, not a ban -- no restricted banner expected"

    assert "/onboarding" in driver.current_url, "A refused user must not be taken to the quest page"
    assert not quest.is_visible(quest.honor_activity_locator, custom_timeout=2), \
        "The quest's activities must not be visible to a refused user"
    assert not has_quest_grant(GOOGLE_WRONG_DOMAIN_EMAIL, RESTRICTED_QUEST_ID), \
        "/api/quest/join must not create a questGrants doc when the domain check fails"
