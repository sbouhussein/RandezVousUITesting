import pytest

from helpers.ios import AccessHelper, GuestJoinHelper
from helpers.ios.ios_test_data import GUEST_USERNAME
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID


@pytest.mark.cleanup(type="username", value=GUEST_USERNAME)
def test_guest_must_use_google_for_domain_quest(rv_driver):
    """A guest entering a domain-restricted quest's code is asked to sign in with Google first (not driven)."""
    guest = GuestJoinHelper(rv_driver)
    guest.open_dashboard()
    guest.enter_code(RESTRICTED_QUEST_ID)

    access = AccessHelper(rv_driver)
    assert access.wait_for_text("Access Required"), "A guest should be stopped at the Access Required step"
    assert access.wait_for_text("@randezvous.com", timeout=5), "The step should name the allowed domain"
    assert access.wait_for_text("Continue with Google", timeout=5), "The step should offer Google sign-in"
