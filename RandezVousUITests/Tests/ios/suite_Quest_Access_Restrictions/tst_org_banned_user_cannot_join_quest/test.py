from helpers.common.access_data_helper import has_quest_grant
from helpers.ios import AccessHelper
from helpers.ios.ios_test_data import QUEST_ID, TEST_EMAIL

REASON = "Automated test restriction: org ban"


def test_org_banned_user_cannot_join_quest(rv_driver, restrict):
    """An org-wide ban blocks joining any of the org's quests."""
    restrict(TEST_EMAIL, level="org", reason=REASON)
    access = AccessHelper(rv_driver)
    access.try_join(QUEST_ID)

    assert access.wait_for_text(REASON), "The ban reason should be shown to the banned user"
    assert not access.is_joined(), "A banned user must not reach the quest"
    assert not has_quest_grant(TEST_EMAIL, QUEST_ID), "A banned user must not get a quest grant"
