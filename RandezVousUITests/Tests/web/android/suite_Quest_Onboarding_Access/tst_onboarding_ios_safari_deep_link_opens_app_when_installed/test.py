from helpers.ios.device_helper import DeviceHelper, RV_BUNDLE_ID
from helpers.web import OnboardingPageHelper
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID, onboarding_url


def test_onboarding_ios_safari_deep_link_opens_app_when_installed(safari_driver):
    """The deep link brings the installed RV app to the foreground; needs the app installed."""
    driver = safari_driver
    device = DeviceHelper(driver)
    device.require_app_installed(installed=True)

    start_url = onboarding_url(RESTRICTED_QUEST_ID)
    driver.get(start_url)

    onboarding = OnboardingPageHelper(driver)
    # Switch into WEBVIEW before any DOM lookup.
    onboarding.switch_to_webview()
    onboarding.click_open_in_app()

    # A cold launch behind SpringBoard's prompt can outlast the helper's 10s default.
    state = device.wait_for_app_foreground(timeout=40)
    assert state == 4, (
        f"Expected the deep link to hand off to the installed RV app (query_app_state == 4), got: {state}"
    )

    # Leave the simulator idle rather than sat on the RV app foregrounded mid-test.
    driver.terminate_app(RV_BUNDLE_ID)
