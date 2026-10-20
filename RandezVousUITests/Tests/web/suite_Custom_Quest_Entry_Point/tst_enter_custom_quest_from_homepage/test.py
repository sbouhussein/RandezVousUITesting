import time

import pytest

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_enter_custom_quest_from_homepage(desktop_safari_driver):
    desktop_safari_driver.get(BASE_URL)
    nav, quest = HomepageHelper(desktop_safari_driver), QuestHelper(desktop_safari_driver)
    time.sleep(2)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.click_find_quest()
    quest.enter_quest_code(ACTIVITY_QUEST_ID)
    quest.click_find_quest()
    quest.complete_trivia_activity("Trivia")
    time.sleep(10)
