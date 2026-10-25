import pytest

from helpers.ios import AccessHelper, GuestJoinHelper
from helpers.ios.ios_test_data import GUEST_USERNAME
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID, RIGHT_DOMAIN_EMAIL


@pytest.mark.cleanup(type="username", value=GUEST_USERNAME)
def test_banned_guest_must_use_google_for_domain_quest(rv_driver, restrict):
    """With a ban on file, a guest on the Quests tab is still sent to Google sign-in instead of joining."""
    restrict(RIGHT_DOMAIN_EMAIL, level="quest", qid=RESTRICTED_QUEST_ID)
    guest = GuestJoinHelper(rv_driver)
    guest.open_dashboard()
    guest.enter_code(RESTRICTED_QUEST_ID)

    access = AccessHelper(rv_driver)
    assert access.wait_for_text("Access Required"), "A guest should be stopped at the Access Required step"
    assert access.wait_for_text("Continue with Google", timeout=5), "The step should offer Google sign-in"
    assert not access.is_joined(timeout=3), "A guest must not join a domain-restricted quest"
