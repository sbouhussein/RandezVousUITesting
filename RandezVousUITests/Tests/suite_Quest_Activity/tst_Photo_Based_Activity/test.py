import pytest
import os
from helpers.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.login_page_helper import LoginPageHelper
from helpers.profile_helper import ProfileHelper
from helpers.media_helper import push_image_to_simulator_gallery, make_image_recent


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_photo_based_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "TestAutomationActivityQuest"
    activity = "Photo Activity"
    score = "125"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_image_path = os.path.join(current_dir, "test_image.jpg")
    make_image_recent(local_image_path)
    push_image_to_simulator_gallery(local_image_path)

    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    profile_helper = ProfileHelper(rv_driver)

    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)
    custom_quest.complete_photo_activity(activity)

    custom_quest.click_exit_quest()
    profile_helper.log_out_if_logged_in(check_score=True, expected_score=score)