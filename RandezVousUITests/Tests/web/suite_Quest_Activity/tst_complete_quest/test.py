import pytest
import time
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_quest(desktop_safari_driver):

    print(f"Navigating to {BASE_URL}")
    desktop_safari_driver.get(BASE_URL)
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = ACTIVITY_QUEST_ID
    trivia_response = "Trivia"
    prompt_response = "Prompt"

    latitude = 41.282778
    longitude = -157.829444

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    print("Signing in")
    nav.login(email, password)
    nav.find_quest(quest_code)

    print("Injecting bulletproof geolocation mock...")
    quest.mock_geo_location(desktop_safari_driver, latitude, longitude)

    print("Completing all required activities in the quest...")
    quest.complete_quest(trivia_response, prompt_response)

    print("Verifying the quest is complete")
    assert quest.verify_quest_completion() == True, "Quest was not completed!"
