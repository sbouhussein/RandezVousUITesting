import pytest
from selenium.webdriver.support.ui import WebDriverWait

from helpers.web.access_control_helper import AccessControlHelper
from helpers.web.firebase_test_data_helper import clear_stale_grant, has_quest_grant
from helpers.web.google_identity_helper import GoogleIdentityHelper
from helpers.web.onboarding_helper import OnboardingPageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import GOOGLE_DOMAIN_EMAIL, ORG_ID, RESTRICTED_QUEST_ID, onboarding_url


@pytest.mark.cleanup(type="email", value=GOOGLE_DOMAIN_EMAIL)
def test_join_domain_quest_with_correct_domain(desktop_safari_driver):
    """Happy path for a domain-restricted quest: a signed-in user whose Google account is on the allowed
    domain joins `web-restricted` and lands on its quest page, with no restricted banner or locked screen.

    The user is a fabricated QA account with a `google.com` provider entry on @randezvous.com (see
    seed_qa_web_fixtures.py), signed in by custom token (helpers/web/google_identity_helper.py). That
    exercises the backend's google_hd domain check and the frontend's success rendering; it does NOT prove
    real Google consent-screen behavior, which Selenium can't automate."""
    driver = desktop_safari_driver

    # A leftover grant would make /join return early and skip the domain check this test is about.
    clear_stale_grant(GOOGLE_DOMAIN_EMAIL, RESTRICTED_QUEST_ID)

    GoogleIdentityHelper(driver).sign_in()

    driver.get(onboarding_url(RESTRICTED_QUEST_ID))
    OnboardingPageHelper(driver).click_start_quest()

    quest = QuestHelper(driver)
    access = AccessControlHelper(driver)
    WebDriverWait(driver, 30).until(
        lambda d: f"/quest/organization/{ORG_ID}/{RESTRICTED_QUEST_ID}" in d.current_url
        and "/onboarding" not in d.current_url,
        message="Expected to land on the quest page after starting the quest",
    )
    assert quest.is_visible(quest.honor_activity_locator, custom_timeout=30), \
        "Expected the quest's activity list for a correct-domain user"
    assert not access.is_restricted_banner_visible(custom_timeout=2), "Did not expect a restricted banner"
    assert not access.is_restricted_quest_screen_visible(custom_timeout=2), "Did not expect the locked-quest screen"
    assert has_quest_grant(GOOGLE_DOMAIN_EMAIL, RESTRICTED_QUEST_ID), \
        "Expected /api/quest/join to have granted access (questGrants doc) after passing the domain check"
