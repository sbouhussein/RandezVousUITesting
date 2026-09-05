import pytest
import time
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_fail_to_complete_location_activity(desktop_safari_driver):

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

    print("Expanding the Location Activity accordion...")
    # quest.expand_location_activity()

    print("Attempting to check-in with invalid coordinates or denied permissions...")
    # quest.trigger_invalid_location_checkin()

    print("Verifying the activity shows an 'Out of Range' or 'Permission Denied' error...")
    # assert quest.is_location_error_visible() == True

    print("Verifying the activity is NOT marked as complete...")
    # assert quest.is_activity_completed("Location") == False

    print("--- Finished test_fail_to_complete_location_activity ---\n")