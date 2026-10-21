import pytest

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, ACTIVITY_QUEST_LOCATION, BASE_URL, TEST_USER_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_quest(desktop_safari_driver):
    desktop_safari_driver.get(BASE_URL)
    HomepageHelper(desktop_safari_driver).sign_in_and_find_quest(ACTIVITY_QUEST_ID)
    quest = QuestHelper(desktop_safari_driver)
    quest.mock_geo_location(*ACTIVITY_QUEST_LOCATION)
    quest.complete_quest(trivia_response="Trivia", prompt_response="Prompt")

    assert quest.verify_quest_completion(), "Quest was not completed!"
