import pytest

from helpers.ios.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.ios.leaderboard_helper import LeaderboardHelper
from helpers.ios.login_page_helper import LoginPageHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_trivia_based_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    username = "OmarTesting"
    quest = "test-automation-quest"
    activity = "Trivia"
    response = "Trivia"

    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    quest_helper = QuestHelper(rv_driver)
    leaderboard = LeaderboardHelper(rv_driver)

    quest_helper.sign_out_if_signed_in()
    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)
    custom_quest.complete_trivia_activity(activity, response)

    expected = leaderboard.expected_score(activities_completed=1)
    assert leaderboard.get_score(username, expected_points=expected) == expected, \
        f"'{username}' should have {expected} points on the leaderboard after one activity"
