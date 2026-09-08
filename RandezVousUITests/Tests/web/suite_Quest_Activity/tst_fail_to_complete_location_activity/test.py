import pytest
import time
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_location_activity(desktop_safari_driver):

    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = "TestAutomationActivityQuest"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    print("Signing in")
    nav.login(email, password)
    nav.find_quest(quest_code)

    print("Injecting bulletproof geolocation mock...")
    latitude = 42.282778
    longitude = -154.829444

    quest.mock_geo_location(desktop_safari_driver, latitude, longitude)

    print("Triggering location check-in...")
    quest.complete_location_activity(fail_check = True)
