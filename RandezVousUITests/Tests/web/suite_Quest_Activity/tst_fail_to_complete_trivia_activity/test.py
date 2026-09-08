import pytest
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_fail_to_complete_trivia_activity(desktop_safari_driver):

    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = "TestAutomationActivityQuest"
    response = "Triviq"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    print("Signing in")
    nav.login(email, password)
    nav.find_quest(quest_code)

    print("Completing trivia activity")
    quest.complete_trivia_activity(response)

    print("Verifying the UI displays an 'Incorrect Answer' warning...")
    assert quest.is_trivia_error_visible() == True, "The trivia error message did not appear!"
