import pytest

from helpers.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.login_page_helper import LoginPageHelper, WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper
from helpers.profile_helper import ProfileHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_quest_from_login(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "TestAutomationActivityQuest"
    username = "OmarTesting"
    score = "775"

    custom_quest = CustomQuestPage(rv_driver)
    quest_helper = QuestHelper(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    profile_helper = ProfileHelper(rv_driver)

    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)
    custom_quest.complete_all_activities()
    #quest_helper.check_leaderboard(username, score)
    custom_quest.finish_quest()

    custom_quest.click_exit_quest()
    profile_helper.log_out_if_logged_in()

