"""Direct Firestore setup/teardown for quest-access scenarios (bans, stale grants) with no test-facing API.
Mirrors the restriction schema in rvsite's backend/lib/restrictionUtils.js -- keep in sync if that changes.
Assumes firebase_admin is already initialized (conftest.py's firebase_init fixture)."""
from firebase_admin import auth as fb_auth, firestore


def clear_stale_grant(email, qid):
    """Deletes any leftover questGrants doc so it doesn't skip the ban check on /join (which is idempotent)."""
    uid = fb_auth.get_user_by_email(email).uid
    firestore.client().collection("Users").document(uid).collection("questGrants").document(qid).delete()


def ban_user_from_quest(email, org_id, qid, reason="Automated test restriction"):
    """Creates a quest-level restriction for `email`, as if an org admin banned them from `qid`."""
    uid = fb_auth.get_user_by_email(email).uid
    firestore.client().collection("Organizations").document(org_id).collection("restricted").document(uid).set({
        "restrictionLevel": "quest",
        "questId": qid,
        "endDate": None,
        "internalReason": "",
        "externalReason": reason,
        "targetEmail": email.strip().lower(),
        "bannedAt": firestore.SERVER_TIMESTAMP,
        "bannedBy": "automation",
    })
    return uid


def unban_user(org_id, uid):
    firestore.client().collection("Organizations").document(org_id).collection("restricted").document(uid).delete()
