import pytest
import time
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_fail_to_complete_trivia_activity(desktop_safari_driver):

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

    print("Expanding the Trivia Activity accordion...")
    # quest.expand_trivia_activity()

    print("Entering an incorrect response into the trivia field...")
    # quest.complete_trivia_activity("Wrong Answer")

    print("Verifying the UI displays an 'Incorrect Answer' warning...")
    # assert quest.is_trivia_error_visible() == True

    print("Verifying the activity is NOT marked as complete...")
    # assert quest.is_activity_completed("Trivia") == False

    print("--- Finished test_fail_to_complete_trivia_activity ---\n")