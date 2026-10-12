from urllib.parse import urlparse, parse_qs, unquote

from helpers.web.onboarding_helper import OnboardingPageHelper
from helpers.web.quest_test_data import BASE_URL, ORG_ID, RESTRICTED_QUEST_ID, onboarding_url, quest_url


def test_onboarding_mobile_fallback_redirects_to_login_when_signed_out(mobile_chrome_driver):
    """QUEST_ONBOARDING_UX.md row 3: Open in App fallback now routes a signed-out visitor
    to /login instead of the raw quest page."""
    driver = mobile_chrome_driver
    driver.get(onboarding_url(RESTRICTED_QUEST_ID))

    onboarding = OnboardingPageHelper(driver)
    href = onboarding.get_open_in_app_href()

    parsed = urlparse(href)
    assert href.startswith(f"{BASE_URL}/login?"), f"Expected a /login fallback, got: {href}"
    goto = unquote(parse_qs(parsed.query)["goto"][0])
    assert goto == quest_url(RESTRICTED_QUEST_ID, org_id=ORG_ID).removeprefix(BASE_URL), (
        f"Expected goto to point back at the restricted quest, got: {goto}"
    )
