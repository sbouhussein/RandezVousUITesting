import pytest
from helpers.custom_quest_helper import QuestHelper
from helpers.firebase_cleanup_helper import cleanup_user_data
from helpers.login_page_helper import WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper

QUEST_URL = "https://www.randezvous.com/quest/organization/test-3hmYPwC0cFa6zch5syk7/testautomationQuest/onboarding"

@pytest.fixture(autouse=True)
def clean_user_data():
    username = "AutomatedTester"
    cleanup_user_data(target_username=username)

def test_joining_quest_through_url(safari_driver):
    driver = safari_driver
    welcome = WelcomeToQuestHelper(driver)
    username_screen = ChooseUsernameHelper(driver)
    adventure = StartAdventureHelper(driver)
    quest_helper = QuestHelper(driver)

    driver.get(QUEST_URL)

    contexts = driver.contexts
    for context in contexts:
        if 'WEBVIEW' in context:
            driver.switch_to.context(context)
            break

    try:
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
    except Exception as e:
        print(f"JS Clear failed: {e}")

    driver.switch_to.context('NATIVE_APP')

    if welcome.verify_welcome_modal_is_displayed():
        welcome.click_lets_go()

    username_screen.enter_username("AutomatedTester")
    if username_screen.is_join_button_enabled():
        username_screen.click_join_quest()

    if adventure.verify_start_adventure_page_is_displayed():
        adventure.click_start_adventure()

    quest_helper.click_exit_quest()
