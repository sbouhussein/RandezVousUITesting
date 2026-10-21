import pytest

from helpers.ios import CustomQuestPage, DeviceHelper
from helpers.ios.ios_test_data import TEST_EMAIL

# Out-of-range coordinates, the same ones the web suite uses.
OUT_OF_RANGE = dict(lat=42.282778, lon=-154.829444)


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_fail_to_complete_location_activity(rv_driver):
    quest = CustomQuestPage(rv_driver)
    quest.sign_in_and_join()
    DeviceHelper(rv_driver).set_simulator_location(**OUT_OF_RANGE)

    assert quest.is_out_of_range_message_visible("Location"), \
        "Expected the 'away from being able to complete' message when out of range"
