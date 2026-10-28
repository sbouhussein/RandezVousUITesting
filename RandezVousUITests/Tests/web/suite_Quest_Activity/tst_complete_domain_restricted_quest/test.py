import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.common.access_data_helper import clear_stale_grant, edited_quest, has_quest_grant
from helpers.web import AccessControlHelper, GoogleIdentityHelper, OnboardingPageHelper, QuestHelper
from helpers.web.quest_test_data import (
    ACTIVITY_QUEST_ID, ACTIVITY_QUEST_LOCATION, GOOGLE_DOMAIN_EMAIL, ORG_ID, onboarding_url,
)

DOMAIN_POLICY = {"type": "google_hd", "allowedDomains": ["randezvous.com"]}


@pytest.mark.usefixtures("fresh_web_backend")
@pytest.mark.cleanup(type="email", value=GOOGLE_DOMAIN_EMAIL)
def test_complete_domain_restricted_quest(desktop_safari_driver):
    """A user on the allowed domain joins a domain-restricted quest with every activity type and completes it."""
    driver = desktop_safari_driver
    clear_stale_grant(GOOGLE_DOMAIN_EMAIL, ACTIVITY_QUEST_ID)
    with edited_quest(ORG_ID, ACTIVITY_QUEST_ID, accessPolicy=DOMAIN_POLICY):  # restored even if the test fails
        GoogleIdentityHelper(driver).sign_in()
        driver.get(onboarding_url(ACTIVITY_QUEST_ID))
        access = AccessControlHelper(driver)
        assert access.is_visible(access.domain_requirement_text, custom_timeout=15), "The temporary restriction should be in effect"
        OnboardingPageHelper(driver).click_start_quest()
        quest = QuestHelper(driver)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(quest.honor_activity_locator))
        quest.mock_geo_location(*ACTIVITY_QUEST_LOCATION)
        quest.complete_quest(trivia_response="Trivia", prompt_response="Prompt")

        assert quest.verify_quest_completion(), "The domain-restricted quest was not completed"
        assert has_quest_grant(GOOGLE_DOMAIN_EMAIL, ACTIVITY_QUEST_ID), "The user should hold a grant after joining"
