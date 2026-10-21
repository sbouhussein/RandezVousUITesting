from helpers.android.device_helper import DeviceHelper
from helpers.web import OnboardingPageHelper
from helpers.web.quest_test_data import BASE_URL, RESTRICTED_QUEST_ID, fallback_goto, onboarding_url, quest_path


def test_onboarding_android_chrome_fallback_redirects_to_login_when_signed_out(android_chrome_driver):
    """Android intent links carry their fallback URL, so a signed-out visitor lands on /login; needs the RV TWA not installed."""
    driver = android_chrome_driver
    DeviceHelper(driver).require_app_installed(installed=False)
    start_url = onboarding_url(RESTRICTED_QUEST_ID)
    driver.get(start_url)
    onboarding = OnboardingPageHelper(driver)
    onboarding.switch_to_webview()
    onboarding.click_open_in_app()
    final_url = onboarding.wait_for_app_fallback_redirect(start_url, custom_timeout=10)

    assert final_url.startswith(f"{BASE_URL}/login?"), f"Expected the fallback to land on /login, got: {final_url}"
    assert fallback_goto(final_url) == quest_path(RESTRICTED_QUEST_ID), f"Expected goto to point back at the quest: {final_url}"
