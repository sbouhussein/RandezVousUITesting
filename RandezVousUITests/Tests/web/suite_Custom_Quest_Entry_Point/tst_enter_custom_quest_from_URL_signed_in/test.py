import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL, onboarding_url


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_enter_custom_quest_from_url_signed_in(desktop_safari_driver):
    desktop_safari_driver.get(BASE_URL)
    email = "oalson123@gmail.com"
    password = "OmarTest123"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    desktop_safari_driver.get(onboarding_url(ACTIVITY_QUEST_ID))
    nav.click_sign_in_to_save_button()
    nav.login_from_url(email, password)
    WebDriverWait(desktop_safari_driver, 30).until(EC.url_contains(f"/{ACTIVITY_QUEST_ID}"))

    quest.complete_trivia_activity("Trivia")
    assert quest.verify_activity_completion("Trivia") is True, "Trivia activity was not marked as completed!"
