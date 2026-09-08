import pytest
import time
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_photo_activity(desktop_safari_driver):

    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = "TestAutomationActivityQuest"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    print("Signing in")
    nav.login(email, password)
    nav.find_quest(quest_code)

    print("Expanding the Photo Activity accordion...")
    quest.complete_photo_activity()

    print("Verifying the photo activity is marked as complete...")
    assert quest.verify_activity_completion("Photo") == True
