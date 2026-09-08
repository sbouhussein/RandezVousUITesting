import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_expired_quest(desktop_safari_driver):

    print("Navigating to http://localhost:5173")
    desktop_safari_driver.get("http://localhost:5173")
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = "ExpiredTestQuest"
    response = "yes"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    print("Signing in")
    nav.login(email, password)
    nav.find_quest(quest_code)

    print("Clicking the complete activity button for honor system...")
    quest.complete_honor_activity()

    print("Expanding the Prompt Activity accordion...")
    quest.complete_prompt_activity(response)

    #TODO verify the activities have been completed before hand

