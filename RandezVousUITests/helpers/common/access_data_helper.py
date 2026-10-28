"""Direct Firestore setup/teardown for quest-access scenarios (bans, stale grants) shared by iOS and web.
Mirrors the restriction schema in rvsite's backend/lib/restrictionUtils.js; needs firebase_init (randezvous-qa)."""
import json
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import firebase_admin
from firebase_admin import auth as fb_auth, firestore, storage

QA_PROJECT = "randezvous-qa"
QA_BUCKET = "randezvous-qa.firebasestorage.app"


def _require_qa():
    """Guards the helpers that delete or overwrite data: they only run against the QA project."""
    project = firebase_admin.get_app().project_id
    if project != QA_PROJECT:
        raise RuntimeError(f"Refusing to change data: Admin app is on '{project}', not '{QA_PROJECT}'.")


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


def create_user_without_username(email, password):
    """Creates an email/password account with no username, as a brand-new sign-up has before it picks one."""
    _require_qa()
    delete_user_by_email(email)
    return fb_auth.create_user(email=email, password=password).uid


def delete_user_by_email(email):
    """Removes the account and its Users doc, if present."""
    _require_qa()
    try:
        uid = fb_auth.get_user_by_email(email).uid
    except fb_auth.UserNotFoundError:
        return
    firestore.client().collection("Users").document(uid).delete()
    fb_auth.delete_user(uid)


@contextmanager
def edited_quest(org_id, qid, **fields):
    """Temporarily sets top-level fields on a QA quest doc and always puts the originals back.
    A field the quest didn't have is deleted again, not left as null.
    Edit before the browser loads the quest: rvsite caches quest definitions per server process."""
    _require_qa()
    ref = firestore.client().collection("Organizations").document(org_id).collection("quests").document(qid)
    original = ref.get().to_dict() or {}
    ref.update(fields)
    try:
        yield
    finally:
        ref.update({k: original[k] if k in original else firestore.DELETE_FIELD for k in fields})


def preload_progress(email, org_id, qid, completed_ids):
    """Gives `email` a grant and finished activities on `qid`, as if they were completed while it was active.
    completed_ids maps typeKey ("honor challenge:1000") to "<qid>-<activityId>"."""
    _require_qa()
    uid = fb_auth.get_user_by_email(email).uid
    user_ref = firestore.client().collection("Users").document(uid)
    user_ref.collection("questGrants").document(qid).set({
        "grantedAt": firestore.SERVER_TIMESTAMP,
        "questPath": {"questType": "organization", "orgId": org_id, "uid": None, "qid": qid},
    })
    user_ref.set({"questHist": {qid: {"orgId": org_id, "completedIds": completed_ids}}}, merge=True)


def quest_completed_date(email, qid):
    """The user's questHist completedDate for `qid`, or None if the quest isn't completed."""
    uid = fb_auth.get_user_by_email(email).uid
    hist = (firestore.client().collection("Users").document(uid).get().to_dict() or {}).get("questHist", {})
    return (hist.get(qid) or {}).get("completedDate")


def event_start(offset):
    """A customStartString (UTC ISO, as the admin form writes it) `offset` from now; negative is in the past."""
    return (datetime.now(timezone.utc) + offset).strftime("%Y-%m-%dT%H:%M:%SZ")


@contextmanager
def edited_activity(org_id, qid, activity_id, **fields):
    """Temporarily sets fields on one activity in the quest's Storage activity file (e.g. customStartString)
    and always restores the original file. Edit before the app or browser loads the quest."""
    _require_qa()
    blob = storage.bucket(QA_BUCKET).blob(f"OrganizationQuests/{org_id}/Quests/{qid}/{qid}.json")
    original = blob.download_as_bytes()
    activities = json.loads(original)
    target = next(a for a in activities if a["id"] == activity_id)
    target.update(fields)
    blob.upload_from_string(json.dumps(activities), content_type="application/json")
    try:
        yield
    finally:
        blob.upload_from_string(original, content_type="application/json")
