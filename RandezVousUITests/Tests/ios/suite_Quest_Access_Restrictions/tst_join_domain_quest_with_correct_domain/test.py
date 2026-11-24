from helpers.common.access_data_helper import has_quest_grant
from helpers.ios import AccessHelper
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID


def test_join_domain_quest_with_correct_domain(rv_driver, domain_user):
    """An account whose Google provider is on the allowed domain joins the domain-restricted quest (no Google screen)."""
    email, password = domain_user
    access = AccessHelper(rv_driver)
    access.try_join(RESTRICTED_QUEST_ID, email, password)

    assert access.is_joined(timeout=20), "An account on the allowed domain should join the restricted quest"
    assert has_quest_grant(email, RESTRICTED_QUEST_ID), "Joining should write a questGrants doc"
