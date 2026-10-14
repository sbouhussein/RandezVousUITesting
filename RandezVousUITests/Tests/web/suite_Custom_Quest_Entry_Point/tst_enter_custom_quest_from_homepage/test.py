import time
import pytest

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_enter_custom_quest_from_homepage(desktop_safari_driver):
    desktop_safari_driver.get(BASE_URL)
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest_code = ACTIVITY_QUEST_ID
    response = "Trivia"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    time.sleep(2)
    nav.login(email, password)
    nav.click_find_quest()
    quest.enter_quest_code(quest_code)
    quest.click_find_quest()
    quest.complete_trivia_activity(response)
    time.sleep(10)

