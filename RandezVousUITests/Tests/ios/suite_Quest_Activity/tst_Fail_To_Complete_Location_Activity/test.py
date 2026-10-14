import pytest

from helpers.ios.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.ios.login_page_helper import LoginPageHelper
from helpers.ios.device_helper import DeviceHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_fail_to_complete_location_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "test-automation-quest"
    activity = "Location"
    # Same out-of-range coordinates the web suite uses for this scenario.
    out_of_range_lat = 42.282778
    out_of_range_lon = -154.829444

    device_helper = DeviceHelper(rv_driver)
    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    quest_helper = QuestHelper(rv_driver)

    quest_helper.sign_out_if_signed_in()
    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)

    print("Setting simulator location out of range...")
    device_helper.set_simulator_location(lat=out_of_range_lat, lon=out_of_range_lon)

    assert custom_quest.is_out_of_range_message_visible(activity), \
        "Expected the 'away from being able to complete' message when out of range"
