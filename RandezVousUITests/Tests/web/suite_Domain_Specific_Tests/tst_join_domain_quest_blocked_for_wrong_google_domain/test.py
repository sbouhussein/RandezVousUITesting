import pytest

from helpers.common.access_data_helper import clear_stale_grant, has_quest_grant
from helpers.web import AccessControlHelper, GoogleIdentityHelper, OnboardingPageHelper, QuestHelper
from helpers.web.quest_test_data import (
    GOOGLE_WRONG_DOMAIN_EMAIL, GOOGLE_WRONG_DOMAIN_UID, RESTRICTED_QUEST_ID, onboarding_url,
)


@pytest.mark.cleanup(type="email", value=GOOGLE_WRONG_DOMAIN_EMAIL)
def test_join_domain_quest_blocked_for_wrong_google_domain(desktop_safari_driver):
    """A Google user on the wrong domain is refused with a "Switch accounts" option and gets no access grant."""
    driver = desktop_safari_driver
    clear_stale_grant(GOOGLE_WRONG_DOMAIN_EMAIL, RESTRICTED_QUEST_ID)  # a leftover grant would skip the domain check
    GoogleIdentityHelper(driver).sign_in(GOOGLE_WRONG_DOMAIN_UID)
    driver.get(onboarding_url(RESTRICTED_QUEST_ID))
    OnboardingPageHelper(driver).click_start_quest()
    access, quest = AccessControlHelper(driver), QuestHelper(driver)

    assert access.is_wrong_domain_message_visible(custom_timeout=30), "Expected the wrong-domain error"
    message = access.get_wrong_domain_message()
    assert "@randezvous.com" in message and "@gmail.com" in message, f"Message should name both domains: {message!r}"
    assert access.is_visible(access.switch_accounts_button, custom_timeout=5), "Expected a 'Switch accounts' remedy"
    assert not access.is_visible(access.sign_in_with_google_button, custom_timeout=2), \
        "'Sign in with Google' is the wrong-provider remedy; this user already is a Google user"
    assert not access.is_restricted_banner_visible(custom_timeout=2), "This is a domain refusal, not a ban"
    assert "/onboarding" in driver.current_url, "A refused user must not be taken to the quest page"
    assert not quest.is_visible(quest.honor_activity_locator, custom_timeout=2), "The quest's activities must stay hidden"
    assert not has_quest_grant(GOOGLE_WRONG_DOMAIN_EMAIL, RESTRICTED_QUEST_ID), \
        "/api/quest/join must not create a questGrants doc when the domain check fails"
