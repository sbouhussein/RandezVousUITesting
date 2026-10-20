import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_enter_custom_quest_from_url_signed_in(desktop_safari_driver):
    desktop_safari_driver.get(BASE_URL)
    desktop_safari_driver.get(onboarding_url(ACTIVITY_QUEST_ID))
    nav = HomepageHelper(desktop_safari_driver)
    nav.click_sign_in_to_save_button()
    nav.login_from_url(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    WebDriverWait(desktop_safari_driver, 30).until(EC.url_contains(f"/{ACTIVITY_QUEST_ID}"))
    quest = QuestHelper(desktop_safari_driver)
    quest.complete_trivia_activity("Trivia")

    assert quest.verify_activity_completion("Trivia"), "Trivia activity was not marked as completed!"
