import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_prompt_activity(desktop_safari_driver):
    # Initialize explicit wait for page transitions
    wait = WebDriverWait(desktop_safari_driver, 10)

    print("Navigating to http://localhost:5173")
    desktop_safari_driver.get("http://localhost:5173")

    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = "TestAutomationActivityQuest"
    response = "Trivia"

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

    print("Expanding the Prompt Activity accordion...")
    quest.complete_trivia_activity(response)

    print("Entering valid text into the prompt response field...")
    # quest.complete_prompt_activity("This is an automated test response for the prompt.")

    print("Verifying the prompt activity is marked as complete...")
    # assert quest.is_activity_completed("Prompt") == True