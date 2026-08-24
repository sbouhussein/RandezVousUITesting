import pytest

from helpers.ios.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.ios.login_page_helper import LoginPageHelper
from helpers.ios.device_helper import DeviceHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_quest_from_login(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "TestAutomationActivityQuest"

    custom_quest = CustomQuestPage(rv_driver)
    quest_helper = QuestHelper(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    device_helper = DeviceHelper(rv_driver)

    quest_helper.sign_out_if_signed_in()
    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)
    device_helper.set_simulator_location()
    custom_quest.complete_all_activities()

