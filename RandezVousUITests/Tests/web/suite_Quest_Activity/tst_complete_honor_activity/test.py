
import pytest
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_honor_activity(desktop_safari_driver):

    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = "TestAutomationActivityQuest"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    print("Signing in")
    nav.login(email, password)
    nav.find_quest(quest_code)

    print("Clicking the complete activity button for honor system...")
    quest.complete_honor_activity()

    print("Verifying the honor activity is marked as complete...")
    assert quest.verify_activity_completion("Honor Code") == True, "Honor activity was not marked as completed!"
