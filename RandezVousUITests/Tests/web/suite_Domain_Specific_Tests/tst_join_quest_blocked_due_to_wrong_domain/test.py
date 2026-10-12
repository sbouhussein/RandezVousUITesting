import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import BASE_URL, RESTRICTED_QUEST_ID


@pytest.mark.cleanup(type="email", value="unauthorized_domain_user@yahoo.com")
def test_join_quest_blocked_wrong_domain(desktop_safari_driver):
    print("\n--- Starting test: test_join_quest_blocked_wrong_domain ---")

    print(f"Navigating to {BASE_URL}")
    desktop_safari_driver.get(BASE_URL)

    email = "unauthorized_domain_user@yahoo.com"
    password = "OmarTest123"
    domain_protected_quest_code = RESTRICTED_QUEST_ID

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    time.sleep(2)
    print(f"Logging in with unauthorized domain user: {email}")
    nav.login(email, password)

    print("Clicking 'Find Quest' navigation button...")
    nav.click_find_quest()

    print(f"Entering domain-protected quest code: {domain_protected_quest_code}")
    quest.enter_quest_code(domain_protected_quest_code)

    print("Submitting quest code lookup...")
    quest.click_find_quest()

    print("Waiting for domain restriction error banner/modal to appear...")
    wait = WebDriverWait(desktop_safari_driver, 10)
    error_banner = wait.until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(), 'restricted') or contains(text(), 'domain') or contains(text(), 'not authorized')]"
        ))
    )

    print(f"Error banner detected with text: '{error_banner.text}'")
    assert error_banner.is_displayed(), "Expected domain restriction message when entering with unauthorized account."