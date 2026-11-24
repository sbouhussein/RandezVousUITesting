import pytest

from helpers.web import HomepageHelper, LeaderboardPageHelper, OnboardingPageHelper, QuestHelper
from helpers.web.quest_test_data import OPEN_QUEST_ID, TEST_USER_EMAIL, onboarding_url, quest_url

USERNAME = "OmarTesting"
STARTING, AFTER_QUEST = 25, 375  # 25 starting points, then +100 for the quest's one activity and +250 completion bonus


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_leaderboard_points(desktop_safari_driver):
    """Joining a quest gives its starting points; finishing the one-activity quest adds the activity and the completion bonus."""
    driver = desktop_safari_driver
    board = LeaderboardPageHelper(driver)
    HomepageHelper(driver).sign_in_and_open(onboarding_url(OPEN_QUEST_ID))
    OnboardingPageHelper(driver).click_start_quest()
    quest = QuestHelper(driver)
    assert quest.is_visible(quest.honor_activity_locator, custom_timeout=30), "Expected to land on the quest after joining"

    row = board.get_row(OPEN_QUEST_ID, USERNAME, points=STARTING)
    assert row and row["points"] == STARTING, f"Expected the starting {STARTING} points after joining, got {row}"

    driver.get(quest_url(OPEN_QUEST_ID))
    quest.complete_honor_activity()
    assert quest.verify_quest_completion(), "Finishing the only activity should finish the quest"
    row = board.get_row(OPEN_QUEST_ID, USERNAME, points=AFTER_QUEST)
    assert row and row["points"] == AFTER_QUEST, f"Expected {AFTER_QUEST} points with the completion bonus, got {row}"
