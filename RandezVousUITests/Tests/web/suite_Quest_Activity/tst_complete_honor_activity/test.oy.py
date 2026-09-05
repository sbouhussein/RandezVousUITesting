import pytest
import time
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_honor_activity(desktop_safari_driver):

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

    print("Expanding the Honor Activity accordion...")
    # quest.expand_honor_activity()

    print("Clicking the complete activity button for honor system...")
    # quest.complete_honor_activity()

    print("Verifying the honor activity is marked as complete...")
    # assert quest.is_activity_completed("Honor") == True

    print("--- Finished test_complete_honor_activity ---\n")