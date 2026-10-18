import pytest

from helpers.ios import CustomQuestPage, DeviceHelper



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

    custom_quest.sign_in_and_join(email, password, quest)

    print("Setting simulator location out of range...")
    device_helper.set_simulator_location(lat=out_of_range_lat, lon=out_of_range_lon)

    assert custom_quest.is_out_of_range_message_visible(activity), \
        "Expected the 'away from being able to complete' message when out of range"
