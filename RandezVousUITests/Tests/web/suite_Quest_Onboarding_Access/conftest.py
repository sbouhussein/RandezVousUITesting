import pytest

from helpers.web.firebase_test_data_helper import ban_user_from_quest, clear_stale_grant, unban_user


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
