import pytest

from helpers.ios.firebase_cleanup_helper import cleanup_user_data
from helpers.ios.login_page_helper import WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper

QUEST_URL = "https://www.randezvous.com/quest/organization/test-3hmYPwC0cFa6zch5syk7/testautomationQuest/onboarding"

@pytest.fixture(autouse=True)
def clean_user_data():
    username = "AutomatedTester"
    cleanup_user_data(target_username=username)

def test_joining_quest_through_url(rv_driver):
    driver = rv_driver
    welcome = WelcomeToQuestHelper(driver)
    username_screen = ChooseUsernameHelper(driver)
    adventure = StartAdventureHelper(driver)

    driver.get(QUEST_URL)

    print("Opening URL on safari")
    driver.execute_script("mobile: deepLink", {
        "url": QUEST_URL,
        "bundleId": "sbouhussein.github.io-rvsite.RandezVous"
    })

    print("RandezVous should be opem")
    if welcome.verify_welcome_modal_is_displayed():
        welcome.click_lets_go()

    username_screen.enter_username("AutomatedTester")
    if username_screen.is_join_button_enabled():
        username_screen.click_join_quest()

    if adventure.verify_start_adventure_page_is_displayed():
        adventure.click_start_adventure()


