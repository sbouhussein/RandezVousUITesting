from helpers.ios.device_helper import DeviceHelper, RV_BUNDLE_ID
from helpers.web.onboarding_helper import OnboardingPageHelper
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID, onboarding_url


def test_onboarding_ios_safari_deep_link_opens_app_when_installed(safari_driver):
    """QUEST_ONBOARDING_UX.md row 3, iOS path -- counterpart to
    test_onboarding_ios_safari_fallback_redirects_to_login_when_signed_out. Requires the RV
    app installed on this simulator, or the deep link is never handled and this instead hits
    the fallback branch that other test covers. openAppOrFallback (appLinks.js) never
    navigates away from the quest page itself when the deep link succeeds -- the only
    observable signal is the RV app taking the foreground, so we assert on
    query_app_state rather than a URL change."""
    driver = safari_driver
    device = DeviceHelper(driver)
    device.require_app_installed(installed=True)

    start_url = onboarding_url(RESTRICTED_QUEST_ID)
    driver.get(start_url)

    onboarding = OnboardingPageHelper(driver)
    # XCUITest Safari sessions start in the NATIVE_APP context -- switch into the
    # page's WEBVIEW context before any DOM lookup (see BaseHelper.switch_to_webview).
    onboarding.switch_to_webview()
    onboarding.click_open_in_app()

    state = device.wait_for_app_foreground()
    assert state == 4, (
        f"Expected the deep link to hand off to the installed RV app (query_app_state == 4), got: {state}"
    )

    # Leave the simulator idle rather than sat on the RV app foregrounded mid-test.
    driver.terminate_app(RV_BUNDLE_ID)
