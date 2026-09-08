import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_prompt_activity(desktop_safari_driver):

    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = "TestAutomationActivityQuest"
    response = "Trivia"

    wait = WebDriverWait(desktop_safari_driver, 10)
    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    print("Signing in")
    nav.login(email, password)

    print("Waiting for login transition...")
    wait.until(EC.url_contains("/login"))

    print("Finding quest...")
    nav.find_quest(quest_code)

    print("Waiting for quest page to load...")
    wait.until(EC.url_contains("/quest"))

    print("Expanding the Trivia Activity accordion...")
    quest.complete_trivia_activity(response)

    print("Verifying the prompt activity is complete")
    assert quest.verify_activity_completion(response) == True, "Prompt activity was not marked as completed!"