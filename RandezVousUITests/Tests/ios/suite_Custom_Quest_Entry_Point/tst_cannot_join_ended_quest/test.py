import pytest

from helpers.common.access_data_helper import has_quest_grant
from helpers.ios import AccessHelper
from helpers.ios.ios_test_data import TEST_EMAIL
from helpers.web.quest_test_data import EXPIRED_QUEST_ID


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_cannot_join_ended_quest(rv_driver):
    """Joining a quest whose end time has passed is refused with an explanation and writes no grant."""
    access = AccessHelper(rv_driver)
    access.try_join(EXPIRED_QUEST_ID)

    assert access.wait_for_text("This quest has ended and can no longer be joined."), "The ended-quest message should show"
    assert not access.is_joined(), "An ended quest must not be joined"
    assert not has_quest_grant(TEST_EMAIL, EXPIRED_QUEST_ID), "An ended quest must not write a grant"
