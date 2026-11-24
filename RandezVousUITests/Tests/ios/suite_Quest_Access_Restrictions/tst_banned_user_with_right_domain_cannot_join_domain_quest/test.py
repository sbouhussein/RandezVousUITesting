from helpers.common.access_data_helper import has_quest_grant
from helpers.ios import AccessHelper
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID

REASON = "Automated test restriction: domain quest ban"


def test_banned_user_with_right_domain_cannot_join_domain_quest(rv_driver, domain_user, restrict):
    """An account on the allowed domain passes the domain check but is refused by its ban on the quest."""
    email, password = domain_user
    restrict(email, level="quest", qid=RESTRICTED_QUEST_ID, reason=REASON)
    access = AccessHelper(rv_driver)
    access.try_join(RESTRICTED_QUEST_ID, email, password)

    assert access.wait_for_text(REASON), "The ban reason should be shown, not the domain message"
    assert not access.is_joined(), "A banned user must not reach the quest"
    assert not has_quest_grant(email, RESTRICTED_QUEST_ID), "A banned user must not get a quest grant"
