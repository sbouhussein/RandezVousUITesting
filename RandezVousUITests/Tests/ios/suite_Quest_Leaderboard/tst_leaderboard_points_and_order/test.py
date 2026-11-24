from helpers.ios import CustomQuestPage, LeaderboardHelper
from helpers.ios.ios_test_data import TEST_EMAIL, TEST_PASSWORD, TEST_USERNAME
from helpers.web.quest_test_data import OPEN_QUEST_ID  # a single-activity (honor) quest


def finish_quest(quest):
    quest.complete_honor_based_activity("Honor", click_back=False)
    quest.dismiss_quest_completion_overlay()


def test_leaderboard_points_and_order(rv_driver, second_user):
    """Joining gives the starting points, finishing adds the completion bonus, and equal scores are listed by who finished first."""
    other_email, other_password, other_username = second_user
    quest, board = CustomQuestPage(rv_driver), LeaderboardHelper(rv_driver)
    quest.sign_in_and_join(other_email, other_password, OPEN_QUEST_ID)

    expected, actual = board.score_check(other_username, activities_completed=0)
    assert actual == expected, f"Expected the starting {expected} points after joining, got {actual}"
    board.close()
    finish_quest(quest)
    expected, actual = board.score_check(other_username, activities_completed=1, quest_completed=True)
    assert actual == expected, f"Expected {expected} points with the completion bonus, got {actual}"

    quest.sign_in_and_join(TEST_EMAIL, TEST_PASSWORD, OPEN_QUEST_ID)
    finish_quest(quest)
    expected, actual = board.score_check(TEST_USERNAME, activities_completed=1, quest_completed=True)
    assert actual == expected, f"Expected the second finisher to also have {expected} points, got {actual}"

    names = [row["username"] for row in board.get_visible_rows()]  # equal scores share a rank number, so compare row order
    assert names.index(other_username) < names.index(TEST_USERNAME), f"The earlier finisher should be listed first, got {names}"
