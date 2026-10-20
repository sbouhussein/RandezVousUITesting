"""Direct Firestore setup/teardown for quest-access scenarios (bans, stale grants) shared by iOS and web.
Mirrors the restriction schema in rvsite's backend/lib/restrictionUtils.js; needs firebase_init (randezvous-qa)."""
from datetime import datetime, timedelta, timezone

from firebase_admin import auth as fb_auth, firestore


def clear_stale_grant(email, qid):
    """Deletes any leftover questGrants doc so it doesn't skip the ban check on /join (which is idempotent)."""
    uid = fb_auth.get_user_by_email(email).uid
    firestore.client().collection("Users").document(uid).collection("questGrants").document(qid).delete()


def restrict_user(email, org_id, level="quest", qid=None, expires_in=None, doc_id=None,
                  reason="Automated test restriction"):
    """Creates a restriction as if an org admin banned `email`, and returns the restricted doc's id.

    level: "quest" (needs `qid`) or "org". expires_in: None for no end date, else a timedelta from now
    (negative = already expired). doc_id: key the doc under another uid, to model a banned person who
    re-registered with the same email; the join check also matches on `targetEmail`."""
    if level == "quest" and not qid:
        raise ValueError("A quest-level restriction needs qid")
    doc_id = doc_id or fb_auth.get_user_by_email(email).uid
    data = {
        "restrictionLevel": level,
        "endDate": None if expires_in is None else datetime.now(timezone.utc) + expires_in,
        "internalReason": "",
        "externalReason": reason,
        "targetEmail": email.strip().lower(),
        "bannedAt": firestore.SERVER_TIMESTAMP,
        "bannedBy": "automation",
    }
    if level == "quest":
        data["questId"] = qid
    firestore.client().collection("Organizations").document(org_id).collection("restricted").document(doc_id).set(data)
    return doc_id


def ban_user_from_quest(email, org_id, qid, reason="Automated test restriction"):
    """A permanent quest-level restriction for `email`; returns the uid it is keyed under."""
    return restrict_user(email, org_id, level="quest", qid=qid, reason=reason)


def unban_user(org_id, uid):
    firestore.client().collection("Organizations").document(org_id).collection("restricted").document(uid).delete()


def has_quest_grant(email, qid):
    """True if `email` has a questGrants doc for `qid`, which /api/quest/join writes only after its checks pass."""
    uid = fb_auth.get_user_by_email(email).uid
    return firestore.client().collection("Users").document(uid).collection("questGrants").document(qid).get().exists
