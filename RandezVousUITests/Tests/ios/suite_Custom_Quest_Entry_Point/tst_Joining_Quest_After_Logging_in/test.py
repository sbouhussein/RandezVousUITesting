import pytest

from helpers.ios.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.ios.leaderboard_helper import LeaderboardHelper
from helpers.ios.login_page_helper import LoginPageHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_joining_quest_after_logging_in(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    username = "OmarTesting"
    quest = "test-automation-quest"
    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    quest_helper = QuestHelper(rv_driver)
    leaderboard = LeaderboardHelper(rv_driver)

    quest_helper.sign_out_if_signed_in()
    login_helper.login_with_credentials(email_text = email, password_text = password)
    custom_quest.join_custom_quest(quest_code = quest)

    expected = leaderboard.expected_score()
    assert leaderboard.get_score(username, expected_points=expected) == expected, \
        f"'{username}' should have the {expected} starting points on the leaderboard after joining"
