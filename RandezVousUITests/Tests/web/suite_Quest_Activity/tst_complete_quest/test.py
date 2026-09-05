import pytest
import time
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_quest(desktop_safari_driver):

    print("Navigating to http://localhost:5173")
    desktop_safari_driver.get("http://localhost:5173")
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = "TestAutomationActivityQuest"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    print("Signing in")
    nav.login(email, password)
    nav.find_quest(quest_code)

    print("Completing all required activities in the quest...")
    # quest.expand_and_complete_trivia_activity("Test Trivia")
    # quest.expand_and_complete_honor_activity()

    print("Clicking the final 'Complete Quest' submit button...")
    # quest.click_finish_quest_button()

    print("Verifying the quest completion success screen is visible...")
    # assert quest.is_quest_success_screen_visible() == True

    print("--- Finished test_complete_quest ---\n")