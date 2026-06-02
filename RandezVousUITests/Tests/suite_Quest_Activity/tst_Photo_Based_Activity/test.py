import pytest

from helpers.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.login_page_helper import LoginPageHelper
from helpers.profile_helper import ProfileHelper
from helpers.media_helper import get_base64_image, get_simulator_path

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_photo_based_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "TestAutomationActivityQuest"
    activity = "Photo Activity"
    score = "125"

    encoded_img = get_base64_image("test_image.jpg", folder_name="photo_activity")
    dest_path = get_simulator_path("test_image.jpg")
    # 3. USE IT HERE: This is where encoded_img goes
    # This transfers the image from your computer into the Simulator's folder
    rv_driver.push_file(dest_path, encoded_img)
    print("Photo has been successfully pushed to the simulator.")

    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    profile_helper = ProfileHelper(rv_driver)

    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)
    custom_quest.click_view_requirements()
    custom_quest.complete_photo_activity(activity, response)

    custom_quest.click_exit_quest()
    profile_helper.log_out_if_logged_in(True, score)
