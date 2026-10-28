import pytest

from helpers.common.access_data_helper import edited_quest
from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL, ORG_ID, TEST_USER_EMAIL

POINTS_TO_WIN = 200  # starting points + two 100-point activities reach it; one activity does not


@pytest.mark.usefixtures("fresh_web_backend")
@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_quest_by_points(desktop_safari_driver):
    """A points-to-win quest completes once enough points are earned, without finishing every activity."""
    driver = desktop_safari_driver
    with edited_quest(ORG_ID, ACTIVITY_QUEST_ID, pointsToWin=POINTS_TO_WIN):  # restored even if the test fails
        driver.get(BASE_URL)
        HomepageHelper(driver).sign_in_and_find_quest(ACTIVITY_QUEST_ID)
        quest = QuestHelper(driver)
        quest.complete_honor_activity()
        assert not quest.verify_quest_completion(), "One activity is not enough points to win"

        quest.complete_prompt_activity("Prompt")
        assert quest.verify_quest_completion(), "Two activities should reach the points needed to win"
