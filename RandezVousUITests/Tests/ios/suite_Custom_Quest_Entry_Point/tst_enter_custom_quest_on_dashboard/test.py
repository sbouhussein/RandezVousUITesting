import pytest

from helpers.ios import GuestJoinHelper
from helpers.ios.ios_test_data import GUEST_USERNAME


@pytest.mark.cleanup(type="username", value=GUEST_USERNAME)
def test_enter_custom_quest_on_dashboard(rv_driver):
    guest = GuestJoinHelper(rv_driver)
    assert guest.open_dashboard(), "Quests Dashboard not detected"
    guest.enter_code()
    guest.finish_onboarding()
