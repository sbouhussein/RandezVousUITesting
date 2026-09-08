import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="test_user@randezvous.com")
def tst_join_domain_quest_with_correct_domain(desktop_safari_driver):
    print("\n--- Starting test: tst_join_domain_quest_with_correct_domain ---")

    print("Navigating to http://localhost:5173")
    desktop_safari_driver.get("http://localhost:5173")

    email = "test_user@randezvous.com"
    password = "OmarTest123"
    domain_protected_quest_code = "DomainProtectedQuest"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    time.sleep(2)
    print(f"Logging in with authorized domain user: {email}")
    nav.login(email, password)

    print("Clicking 'Find Quest' navigation button...")
    nav.click_find_quest()

    print(f"Entering domain-protected quest code: {domain_protected_quest_code}")
    quest.enter_quest_code(domain_protected_quest_code)

    print("Submitting quest code lookup...")
    quest.click_find_quest()

    wait = WebDriverWait(desktop_safari_driver, 10)