from helpers.common.access_data_helper import has_quest_grant
from helpers.ios import AccessHelper
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID


def test_join_domain_quest_blocked_for_wrong_google_domain(rv_driver, wrong_domain_user):
    """An account whose Google provider is on another domain is told the quest needs the allowed domain, is offered Switch Account, and never joins."""
    email, password = wrong_domain_user
    access = AccessHelper(rv_driver)
    access.try_join(RESTRICTED_QUEST_ID, email, password)

    assert access.wait_for_text("Requires an account from: @randezvous.com"), "The quest card should name the allowed domain"
    assert access.wait_for_text("doesn't have access", timeout=5), "The card should say the current account has no access"
    assert access.wait_for_text("Switch Account (Sign Out)", timeout=5), "A wrong-domain account should be offered Switch Account"
    assert not access.is_joined(timeout=3), "A wrong-domain account must not reach the quest"
    assert not has_quest_grant(email, RESTRICTED_QUEST_ID), "A wrong-domain account must not get a quest grant"
