from urllib.parse import urlparse, parse_qs, unquote

from helpers.ios.device_helper import DeviceHelper
from helpers.web.onboarding_helper import OnboardingPageHelper
from helpers.web.quest_test_data import BASE_URL, ORG_ID, RESTRICTED_QUEST_ID, onboarding_url, quest_url


def test_onboarding_ios_safari_fallback_redirects_to_login_when_signed_out(safari_driver):
    """QUEST_ONBOARDING_UX.md row 3, iOS path: mobile_chrome_driver's Android user-agent trick
    (see its docstring in conftest.py) can only verify the fallback href, since Android's
    "Open in App" link resolves straight to the fallback URL. iOS instead fires the deep link
    and only navigates to the fallback from openAppOrFallback's 1500ms no-blur timeout
    (src/utils/appLinks.js) -- that branch needs a real iOS Safari to exercise, hence
    safari_driver instead of mobile_chrome_driver. Requires the RV app NOT installed on this
    simulator, or the deep link succeeds and the fallback never fires -- see
    test_onboarding_ios_safari_deep_link_opens_app_when_installed for that counterpart."""
    driver = safari_driver
    DeviceHelper(driver).require_app_installed(installed=False)

    start_url = onboarding_url(RESTRICTED_QUEST_ID)
    driver.get(start_url)

    onboarding = OnboardingPageHelper(driver)
    # XCUITest Safari sessions start in the NATIVE_APP context -- switch into the
    # page's WEBVIEW context before any DOM lookup (see BaseHelper.switch_to_webview).
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
