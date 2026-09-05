import time
import pytest

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_enter_custom_quest_from_url_not_signed_in(desktop_safari_driver):
    desktop_safari_driver.get("http://localhost:5173")
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    QUEST_URL = "http://localhost:5173/quest/organization/test-3hmYPwC0cFa6zch5syk7/TestAutomationActivityQuest/onboarding"
    response = "Trivia"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    desktop_safari_driver.get(QUEST_URL)
    time.sleep(2)
    nav.click_guest_button()
    #verify sign in pop appears
    quest.complete_trivia_activity(response)
    time.sleep(200)


