import pytest

from helpers.common.access_data_helper import has_quest_grant
from helpers.web import AccessControlHelper, GoogleIdentityHelper, OnboardingPageHelper, QuestHelper
from helpers.web.quest_test_data import GOOGLE_DOMAIN_EMAIL, ORG_ID, RESTRICTED_QUEST_ID, onboarding_url


@pytest.mark.cleanup(type="email", value=GOOGLE_DOMAIN_EMAIL)
def test_banned_user_with_right_domain_cannot_join_domain_quest(desktop_safari_driver, banned_user):
    """A banned user on the allowed domain passes the domain check but is refused by the ban (fabricated QA account)."""
    driver = desktop_safari_driver
    banned_user(GOOGLE_DOMAIN_EMAIL, ORG_ID, RESTRICTED_QUEST_ID)
    GoogleIdentityHelper(driver).sign_in()
    driver.get(onboarding_url(RESTRICTED_QUEST_ID))
    OnboardingPageHelper(driver).click_start_quest()

    access = AccessControlHelper(driver)
    assert access.is_restricted_banner_visible(custom_timeout=15), "Expected the RestrictedBanner for a banned user"
    assert not access.is_wrong_domain_message_visible(custom_timeout=2), "The domain is right; the ban should be the reason"
    assert not QuestHelper(driver).is_visible(QuestHelper.honor_activity_locator, custom_timeout=2), \
        "A banned user must not see the quest's activities"
    assert not has_quest_grant(GOOGLE_DOMAIN_EMAIL, RESTRICTED_QUEST_ID), "A banned join must not create a grant"
