from urllib.parse import urlparse, parse_qs, unquote

from helpers.ios import DeviceHelper
from helpers.web import OnboardingPageHelper
from helpers.web.quest_test_data import BASE_URL, ORG_ID, RESTRICTED_QUEST_ID, onboarding_url, quest_url


def test_onboarding_ios_safari_fallback_redirects_to_login_when_signed_out(safari_driver):
    """iOS only navigates to the fallback after a 1500ms no-blur timeout, so it needs real Safari and the RV app not installed."""
    driver = safari_driver
    DeviceHelper(driver).require_app_installed(installed=False)

    start_url = onboarding_url(RESTRICTED_QUEST_ID)
    driver.get(start_url)

    onboarding = OnboardingPageHelper(driver)
    # Switch into WEBVIEW before any DOM lookup.
    onboarding.switch_to_webview()
    onboarding.click_open_in_app()

    final_url = onboarding.wait_for_app_fallback_redirect(start_url, custom_timeout=10)

    parsed = urlparse(final_url)
    assert final_url.startswith(f"{BASE_URL}/login?"), (
        f"Expected the 1500ms blur-timeout to land on /login, got: {final_url}"
    )
    goto = unquote(parse_qs(parsed.query)["goto"][0])
    assert goto == quest_url(RESTRICTED_QUEST_ID, org_id=ORG_ID).removeprefix(BASE_URL), (
        f"Expected goto to point back at the restricted quest, got: {goto}"
    )
