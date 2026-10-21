from helpers.web import OnboardingPageHelper
from helpers.web.quest_test_data import BASE_URL, RESTRICTED_QUEST_ID, fallback_goto, onboarding_url, quest_path


def test_onboarding_mobile_fallback_redirects_to_login_when_signed_out(mobile_chrome_driver):
    """The Open in App fallback sends a signed-out visitor to /login."""
    mobile_chrome_driver.get(onboarding_url(RESTRICTED_QUEST_ID))
    href = OnboardingPageHelper(mobile_chrome_driver).get_open_in_app_href()

    assert href.startswith(f"{BASE_URL}/login?"), f"Expected a /login fallback, got: {href}"
    assert fallback_goto(href) == quest_path(RESTRICTED_QUEST_ID), f"Expected goto to point back at the quest: {href}"
