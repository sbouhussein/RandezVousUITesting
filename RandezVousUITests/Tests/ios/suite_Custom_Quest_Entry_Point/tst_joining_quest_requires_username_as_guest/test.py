import pytest

from helpers.ios import GuestJoinHelper
from helpers.ios.ios_test_data import GUEST_USERNAME


@pytest.mark.cleanup(type="username", value=GUEST_USERNAME)
def test_joining_quest_requires_username_as_guest(rv_driver):
    """A guest with no saved username can't join a custom quest without choosing one first."""
    guest = GuestJoinHelper(rv_driver)
    username = guest.choose_username
    guest.open_dashboard()
    guest.enter_code()
    guest.continue_past_welcome()

    assert username.verify_choose_username_page_is_displayed(), "A guest should be asked to choose a username"
    assert username.is_join_button_enabled() is False, "Join Quest should be disabled until a username is entered"
    username.enter_username(GUEST_USERNAME)
    assert username.is_join_button_enabled() is True, "Join Quest should be enabled once a username is entered"
    username.click_join_quest()
    guest.start_adventure()
