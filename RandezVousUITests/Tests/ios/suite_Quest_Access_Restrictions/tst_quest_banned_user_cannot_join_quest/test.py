from helpers.common.access_data_helper import has_quest_grant
from helpers.ios import AccessHelper
from helpers.ios.ios_test_data import QUEST_ID, TEST_EMAIL

REASON = "Automated test restriction: quest ban"


def test_quest_banned_user_cannot_join_quest(rv_driver, restrict):
    """A user with an active ban on this quest sees the ban reason and doesn't join."""
    restrict(TEST_EMAIL, level="quest", qid=QUEST_ID, reason=REASON)
    access = AccessHelper(rv_driver)
    access.try_join(QUEST_ID)

    assert access.wait_for_text(REASON), "The ban reason should be shown to the banned user"
    assert not access.is_joined(), "A banned user must not reach the quest"
    assert not has_quest_grant(TEST_EMAIL, QUEST_ID), "A banned user must not get a quest grant"
