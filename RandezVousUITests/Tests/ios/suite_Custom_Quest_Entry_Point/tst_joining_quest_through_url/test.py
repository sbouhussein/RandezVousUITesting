import pytest

from helpers.ios.device_helper import RV_BUNDLE_ID
from helpers.ios.login_page_helper import WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper

QUEST_URL = "https://www.randezvous.com/quest/organization/test-org/test-automation-quest/onboarding"


@pytest.mark.cleanup(type="username", value="AutomatedTester")
def test_joining_quest_through_url(rv_driver):
    driver = rv_driver
    welcome = WelcomeToQuestHelper(driver)
    username_screen = ChooseUsernameHelper(driver)
    adventure = StartAdventureHelper(driver)

    driver.get(QUEST_URL)

    driver.execute_script("mobile: deepLink", {"url": QUEST_URL, "bundleId": RV_BUNDLE_ID})

    if welcome.verify_welcome_modal_is_displayed():
        welcome.click_lets_go()

    username_screen.enter_username("AutomatedTester")
    if username_screen.is_join_button_enabled():
        username_screen.click_join_quest()

    if adventure.verify_start_adventure_page_is_displayed():
        adventure.click_start_adventure()
