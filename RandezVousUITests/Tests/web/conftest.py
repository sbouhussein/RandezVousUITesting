import pytest

from helpers.common.access_data_helper import ban_user_from_quest, clear_stale_grant, restrict_user, unban_user
from helpers.web.quest_test_data import ORG_ID


@pytest.fixture
def banned_user():
    """Factory: bans (email, org_id, qid), clearing any stale grant first. Always unbans on teardown."""
    bans = []

    def _ban(email, org_id, qid):
        clear_stale_grant(email, qid)
        uid = ban_user_from_quest(email, org_id, qid)
        bans.append((org_id, uid))
        return uid

    yield _ban

    for org_id, uid in bans:
        unban_user(org_id, uid)


@pytest.fixture
def restrict():
    """Factory for restrictions in the test org (see restrict_user); every one is removed on teardown."""
    created = set()

    def make(email, **kwargs):
        doc_id = restrict_user(email, ORG_ID, **kwargs)
        created.add(doc_id)
        return doc_id

    yield make
    for doc_id in created:
        unban_user(ORG_ID, doc_id)
