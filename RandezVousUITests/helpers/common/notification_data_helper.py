"""Checks which quest notifications the deployed Cloud Function sends, without needing a device to receive them.

The function (sendCustomQuestFeedNotification) sends to every subscriber whose setting allows the item, then deletes
any device token FCM rejects. A malformed "sentinel" token on the user is therefore deleted exactly when the user was
selected. A control subscriber on All Notifications gets its own sentinel, so "not notified" is only concluded once the
function is known to have processed the item."""
import time
import uuid
from contextlib import contextmanager

from firebase_admin import auth as fb_auth, firestore, messaging

from helpers.common.access_data_helper import _feed_ref, _require_qa, _subscriber_ref

CONTROL_UID = "qa-notification-control"
TEST_AUTHOR = "testauthor"
AUTHOR_UID = "qa-notification-author"  # the function never notifies an item's author, so posts come from someone else


def _db():
    return firestore.client()


def _tokens(uid):
    return _db().collection("Users").document(uid).collection("NotificationTokens")


def _sentinel():
    return f"sentinel-{uuid.uuid4().hex[:12]}:" + "A" * 140  # well-formed enough for FCM to reject it as invalid


def _feed_item(kind, author_uid, stamp):
    """Announcements are shaped like rvsite's admin tool writes them; posts are free-form comments by another account.
    `stamp` (a time) makes each message distinguishable from notifications left on the lock screen by earlier runs."""
    if kind == "announcement":
        return {"type": "announcement", "title": "Test announcement", "message": f"Automated test announcement, please ignore ({stamp})",
                "author": {"id": "x", "username": "Admin", "icon": -10}}
    return {"type": "comment", "message": f"Automated test post, please ignore ({stamp})", "author": {"id": author_uid, "username": TEST_AUTHOR}}


def notification_text(kind, stamp):
    """(title, body) the function puts in the push for an item sent by `_feed_item`."""
    if kind == "announcement":
        return "Test announcement", f"Automated test announcement, please ignore ({stamp})"
    return f"@{TEST_AUTHOR} posted to your quest", f"Automated test post, please ignore ({stamp})"


def user_notified(org_id, qid, email, kind, timeout=60):
    """Posts a `kind` ("announcement" or "post") item to the quest feed and returns whether `email` was selected for a notification.
    Raises if the function never handled the item (control sentinel still there after `timeout`)."""
    _require_qa()
    uid = fb_auth.get_user_by_email(email).uid
    quest = _db().collection("Organizations").document(org_id).collection("quests").document(qid)
    user_token, control_token = _sentinel(), _sentinel()
    quest.collection("subscribers").document(CONTROL_UID).set({"notificationSetting": 2, "uid": CONTROL_UID})
    _tokens(CONTROL_UID).document(control_token).set({"platform": "ios", "createdAt": firestore.SERVER_TIMESTAMP})
    _tokens(uid).document(user_token).set({"platform": "ios", "createdAt": firestore.SERVER_TIMESTAMP})
    item = _feed_item(kind, AUTHOR_UID, time.strftime("%H:%M:%S"))
    item["timestamp"] = firestore.SERVER_TIMESTAMP
    ref = _feed_ref(org_id, qid).add(item)[1]
    try:
        deadline = time.monotonic() + timeout
        while _tokens(CONTROL_UID).document(control_token).get().exists:
            if time.monotonic() > deadline:
                raise RuntimeError("The notification function never handled the feed item (control token was not removed)")
            time.sleep(3)
        return not _tokens(uid).document(user_token).get().exists
    finally:
        ref.delete()
        _tokens(uid).document(user_token).delete()
        _tokens(CONTROL_UID).document(control_token).delete()
        quest.collection("subscribers").document(CONTROL_UID).delete()


def _token_is_live(token):
    """True if FCM still accepts the token (a dry run sends nothing)."""
    try:
        messaging.send(messaging.Message(token=token, data={"check": "1"}), dry_run=True)
        return True
    except Exception:
        return False


def wait_for_web_token(email, since, timeout=45):
    """Waits until the browser has registered a push token for `email` after `since` (a datetime) that FCM accepts; False if none does.
    The page registers a token more than once and the first can be replaced, so a token that merely exists isn't enough.
    Sending before then reaches no browser."""
    _require_qa()
    uid = fb_auth.get_user_by_email(email).uid
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for d in _tokens(uid).where("platform", "==", "web").stream():
            data = d.to_dict()
            if data.get("createdAt") and data["createdAt"] > since and _token_is_live(data["token"]):
                return True
        time.sleep(2)
    return False


def delete_web_tokens(email, since):
    """Removes the web push tokens a test run registered (those created after `since`) so they don't pile up on the account."""
    _require_qa()
    uid = fb_auth.get_user_by_email(email).uid
    for d in _tokens(uid).where("platform", "==", "web").stream():
        if d.to_dict().get("createdAt") and d.to_dict()["createdAt"] > since:
            d.reference.delete()


class SentItem:
    def __init__(self, title, body, processed):
        self.title, self.body, self._processed = title, body, processed

    def wait_processed(self, timeout=60):
        """Waits until the function has handled the item (a control subscriber's sentinel token was removed); raises if it never does."""
        self._processed(timeout)


@contextmanager
def sent_item(org_id, qid, kind):
    """Posts an announcement or feed post and yields a SentItem with the title and message the push should carry.
    A control subscriber on All Notifications tells wait_processed() when the function has run. Everything is deleted on exit."""
    _require_qa()
    quest = _db().collection("Organizations").document(org_id).collection("quests").document(qid)
    control_token = _sentinel()
    quest.collection("subscribers").document(CONTROL_UID).set({"notificationSetting": 2, "uid": CONTROL_UID})
    _tokens(CONTROL_UID).document(control_token).set({"platform": "ios", "createdAt": firestore.SERVER_TIMESTAMP})
    stamp = time.strftime("%H:%M:%S")
    item = _feed_item(kind, AUTHOR_UID, stamp)
    item["timestamp"] = firestore.SERVER_TIMESTAMP
    ref = _feed_ref(org_id, qid).add(item)[1]

    def processed(timeout):
        deadline = time.monotonic() + timeout
        while _tokens(CONTROL_UID).document(control_token).get().exists:
            if time.monotonic() > deadline:
                raise RuntimeError("The notification function never handled the feed item (control token was not removed)")
            time.sleep(2)

    try:
        yield SentItem(*notification_text(kind, stamp), processed)
    finally:
        ref.delete()
        _tokens(CONTROL_UID).document(control_token).delete()
        quest.collection("subscribers").document(CONTROL_UID).delete()
