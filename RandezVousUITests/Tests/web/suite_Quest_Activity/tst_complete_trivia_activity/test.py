import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_trivia_activity(desktop_safari_driver):
    response = "Trivia"

    wait = WebDriverWait(desktop_safari_driver, 10)
    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    wait.until(EC.url_contains("/login"))

    nav.find_quest(ACTIVITY_QUEST_ID)
    wait.until(EC.url_contains("/quest"))

    quest.complete_trivia_activity(response)

    assert quest.verify_activity_completion(response), "Trivia activity was not marked as completed!"