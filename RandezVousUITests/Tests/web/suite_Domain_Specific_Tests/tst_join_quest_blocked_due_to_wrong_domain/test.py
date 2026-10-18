import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import BASE_URL, RESTRICTED_QUEST_ID, WRONG_DOMAIN_EMAIL, WRONG_DOMAIN_PASSWORD


@pytest.mark.cleanup(type="email", value=WRONG_DOMAIN_EMAIL)
def test_join_quest_blocked_wrong_domain(desktop_safari_driver):
    desktop_safari_driver.get(BASE_URL)

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    time.sleep(2)
    nav.login(WRONG_DOMAIN_EMAIL, WRONG_DOMAIN_PASSWORD)
    nav.click_find_quest()
    quest.enter_quest_code(RESTRICTED_QUEST_ID)
    quest.click_find_quest()

    wait = WebDriverWait(desktop_safari_driver, 10)
    error_banner = wait.until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(), 'restricted') or contains(text(), 'domain') or contains(text(), 'not authorized')]"
        ))
    )

    print(f"Error banner detected with text: '{error_banner.text}'")
    assert error_banner.is_displayed(), "Expected domain restriction message when entering with unauthorized account."