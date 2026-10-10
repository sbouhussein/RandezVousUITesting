from urllib.parse import urlparse, parse_qs, unquote

from helpers.android.device_helper import DeviceHelper
from helpers.web.onboarding_helper import OnboardingPageHelper
from helpers.web.quest_test_data import BASE_URL, ORG_ID, RESTRICTED_QUEST_ID, onboarding_url, quest_url


def test_onboarding_android_chrome_fallback_redirects_to_login_when_signed_out(android_chrome_driver):
    """QUEST_ONBOARDING_UX.md row 3, Android path: mobile_chrome_driver's UA trick can
    only verify the fallback href -- a desktop browser has no app to resolve the intent
    link against, so this needs a real Android browser to exercise the actual navigation.
    Android's intent:// URI carries its fallback (S.browser_fallback_url) in the URI
    itself, so Chrome navigates there the instant the intent fails to resolve -- no
    1500ms blur-timeout wait like iOS's custom-scheme deep link (see
    test_onboarding_ios_safari_fallback_redirects_to_login_when_signed_out). Requires the
    RV TWA NOT installed, or the intent resolves straight to the app and the fallback
    never fires. (There is no installed-app counterpart on Android: the intent's target
    host is only ever verified against the real randezvous.com domain, which this
    localhost-backed suite can never serve from, so that branch isn't testable here --
    see rvsite/public/.well-known/assetlinks.json.)"""
    driver = android_chrome_driver
    DeviceHelper(driver).require_app_installed(installed=False)

    start_url = onboarding_url(RESTRICTED_QUEST_ID)
    driver.get(start_url)

    onboarding = OnboardingPageHelper(driver)
    # Android Chrome sessions also use NATIVE_APP/WEBVIEW contexts -- switch into
    # WEBVIEW before any DOM lookup (see BaseHelper.switch_to_webview).
    onboarding.switch_to_webview()
    onboarding.click_open_in_app()

    final_url = onboarding.wait_for_app_fallback_redirect(start_url, custom_timeout=10)

    parsed = urlparse(final_url)
    assert final_url.startswith(f"{BASE_URL}/login?"), (
        f"Expected the intent fallback to land on /login, got: {final_url}"
    )
    goto = unquote(parse_qs(parsed.query)["goto"][0])
    assert goto == quest_url(RESTRICTED_QUEST_ID, org_id=ORG_ID).removeprefix(BASE_URL), (
        f"Expected goto to point back at the restricted quest, got: {goto}"
    )
