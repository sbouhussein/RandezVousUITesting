import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import BASE_URL, RESTRICTED_QUEST_ID


def tst_join_domain_quest_not_signed_in(desktop_safari_driver):
    print("\n--- Starting test: tst_join_domain_quest_not_signed_in ---")

    print(f"Navigating to {BASE_URL}")
    desktop_safari_driver.get(BASE_URL)

    domain_protected_quest_code = RESTRICTED_QUEST_ID

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    time.sleep(2)
    print("Skipping login step to remain an unauthenticated guest...")

    print("Clicking 'Find Quest' navigation button...")
    nav.click_find_quest()

    print(f"Entering domain-protected quest code: {domain_protected_quest_code}")
    quest.enter_quest_code(domain_protected_quest_code)

    print("Submitting quest code lookup...")
    quest.click_find_quest()

    print("Waiting for login redirect or authentication error banner...")
    wait = WebDriverWait(desktop_safari_driver, 10)