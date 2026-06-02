import time

import pytest

from helpers.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.login_page_helper import LoginPageHelper
from helpers.profile_helper import ProfileHelper

def set_simulator_location(rv_driver):
    rv_driver.set_location(40.741895, -73.989308, 10)
    time.sleep(2)

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_location_based_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "TestAutomationActivityQuest"
    activity = "Location Activity"
    score = "125"

    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    profile_helper = ProfileHelper(rv_driver)

    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)
    custom_quest.click_view_requirements()
    custom_quest.complete_location_activity(activity)

    custom_quest.click_exit_quest()
    profile_helper.log_out_if_logged_in(True, score)
