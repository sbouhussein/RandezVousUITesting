from helpers.ios import DeviceHelper
from helpers.web import OnboardingPageHelper
from helpers.web.quest_test_data import BASE_URL, RESTRICTED_QUEST_ID, fallback_goto, onboarding_url, quest_path


def test_onboarding_ios_safari_fallback_redirects_to_login_when_signed_out(safari_driver):
    """iOS only navigates to the fallback after a 1500ms no-blur timeout, so it needs real Safari and the RV app not installed."""
    driver = safari_driver
    DeviceHelper(driver).require_app_installed(installed=False)
    start_url = onboarding_url(RESTRICTED_QUEST_ID)
    driver.get(start_url)
    onboarding = OnboardingPageHelper(driver)
    onboarding.switch_to_webview()
    onboarding.click_open_in_app()
    final_url = onboarding.wait_for_app_fallback_redirect(start_url, custom_timeout=10)

    assert final_url.startswith(f"{BASE_URL}/login?"), f"Expected the fallback to land on /login, got: {final_url}"
    assert fallback_goto(final_url) == quest_path(RESTRICTED_QUEST_ID), f"Expected goto to point back at the quest: {final_url}"
