from datetime import timedelta

from helpers.common.access_data_helper import has_quest_grant
from helpers.ios import AccessHelper
from helpers.ios.ios_test_data import QUEST_ID, TEST_EMAIL
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, OPEN_QUEST_ID

EXPIRED = timedelta(hours=-1)
CASES = [
    ("ban on a different quest", dict(level="quest", qid=OPEN_QUEST_ID), QUEST_ID),
    ("expired quest ban", dict(level="quest", qid=OPEN_QUEST_ID, expires_in=EXPIRED), OPEN_QUEST_ID),
    ("expired org ban", dict(level="org", expires_in=EXPIRED), ACTIVITY_QUEST_ID),
]


def test_user_can_join_when_ban_does_not_apply(rv_driver, restrict):
    """Bans that don't apply let the user join. Each case joins a different quest (a held grant skips the ban
    check) from a fresh sign-in, replacing the one restriction doc."""
    access = AccessHelper(rv_driver)
    for name, restriction, quest in CASES:
        restrict(TEST_EMAIL, **restriction)
        access.try_join(quest)
        assert access.is_joined(timeout=15), f"Joining {quest} should succeed with an unapplicable {name}"
        assert has_quest_grant(TEST_EMAIL, quest), f"No grant was written for {quest} ({name})"
