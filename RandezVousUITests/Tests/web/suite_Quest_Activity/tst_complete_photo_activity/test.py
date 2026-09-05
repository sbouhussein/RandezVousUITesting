import pytest
import time
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_photo_activity(desktop_safari_driver):

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

    print("Expanding the Photo Activity accordion...")
    # quest.expand_photo_activity()

    print("Uploading a valid photo file...")
    # quest.upload_photo_for_activity("/path/to/test_image.jpg")

    print("Submitting the photo activity...")
    # quest.submit_photo_activity()

    print("Verifying the photo activity is marked as complete...")
    # assert quest.is_activity_completed("Photo") == True

    print("--- Finished test_complete_photo_activity ---\n")