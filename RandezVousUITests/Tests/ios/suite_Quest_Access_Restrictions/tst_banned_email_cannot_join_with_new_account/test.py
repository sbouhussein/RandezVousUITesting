from helpers.common.access_data_helper import has_quest_grant
from helpers.ios import AccessHelper
from helpers.ios.ios_test_data import QUEST_ID, TEST_EMAIL

REASON = "Automated test restriction: banned under another uid"


def test_banned_email_cannot_join_with_new_account(rv_driver, restrict):
    """A ban recorded under a different uid still blocks an account with the same email (re-registration)."""
    restrict(TEST_EMAIL, level="quest", qid=QUEST_ID, doc_id="qa-ios-previous-account-uid", reason=REASON)
    access = AccessHelper(rv_driver)
    access.try_join(QUEST_ID)

    assert access.wait_for_text(REASON), "The ban reason should be shown to the banned user"
    assert not access.is_joined(), "A banned user must not reach the quest"
    assert not has_quest_grant(TEST_EMAIL, QUEST_ID), "A banned user must not get a quest grant"
