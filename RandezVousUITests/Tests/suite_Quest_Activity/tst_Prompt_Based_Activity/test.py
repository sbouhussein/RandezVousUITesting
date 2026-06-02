import pytest

from helpers.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.login_page_helper import LoginPageHelper
from helpers.profile_helper import ProfileHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_prompt_based_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "TestAutomationActivityQuest"
    activity = "Prompt Activity"
    response = "Prompt"
    score = "125"

    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    profile_helper = ProfileHelper(rv_driver)

    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)
    custom_quest.click_view_requirements()
    custom_quest.complete_prompt_activity(activity, response)

    custom_quest.click_exit_quest()
    profile_helper.log_out_if_logged_in(True, score)

