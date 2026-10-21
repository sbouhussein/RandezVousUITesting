"""Admin-SDK access to the quest feed and photo data for the Quest Feed tests, QA project only."""
import io
import os
import time
import urllib.parse
import uuid
from datetime import datetime, timezone

import firebase_admin
import requests
from firebase_admin import auth, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter

from helpers.ios.ios_test_data import (  # noqa: F401  (re-exported for the feed tests)
    OTHER_EMAIL, OTHER_PASSWORD, OTHER_USERNAME, QUEST_ID, TEST_EMAIL, TEST_PASSWORD, TEST_USERNAME,
)

QA_PROJECT = "randezvous-qa"
QA_BUCKET = "randezvous-qa.firebasestorage.app"
ORG_ID = "test-org"
# The Photo activity of test-automation-quest (feed imagePost docs and the user's photo arrays use this key).
PHOTO_ACTIVITY_KEY = f"{QUEST_ID}-1001"


def unique_text(prefix="ui-test"):
    """A caption/post text no other run can share, so a test can tell its own post from the 47+ already there."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def utc_now():
    return datetime.now(timezone.utc)


def _db():
    project = firebase_admin.get_app().project_id
    if project != QA_PROJECT:
        raise RuntimeError(f"Refusing to touch feed data: Admin app is on '{project}', not '{QA_PROJECT}'.")
    return firestore.client()


def _uid(email):
    return auth.get_user_by_email(email).uid


def _feed_ref(db):
    return db.collection("Organizations").document(ORG_ID).collection("quests").document(QUEST_ID).collection("feed")


def get_feed_posts(email=TEST_EMAIL, since=None, post_type=None):
    """Feed docs `email` authored, newest first, optionally limited by `since` and `post_type`."""
    db = _db()
    uid = _uid(email)
    query = _feed_ref(db)
    if since is not None:
        # One range filter only: combining it with an author equality filter would need a composite index.
        query = query.where(filter=FieldFilter("timestamp", ">=", since))
    posts = []
    for doc in query.stream():
        data = doc.to_dict()
        if (data.get("author") or {}).get("id") != uid:
            continue
        if post_type and data.get("type") != post_type:
            continue
        posts.append({**data, "id": doc.id})
    return sorted(posts, key=lambda p: p["timestamp"], reverse=True)


def wait_for_feed_post(email=TEST_EMAIL, since=None, post_type=None, predicate=None, timeout=20):
    """Polls until a matching post exists (the app writes it a moment after the upload) and returns it, or None."""
    deadline = time.monotonic() + timeout
    while True:
        for post in get_feed_posts(email, since=since, post_type=post_type):
            if predicate is None or predicate(post):
                return post
        if time.monotonic() > deadline:
            return None
        time.sleep(1)


def delete_feed_posts_since(email=TEST_EMAIL, since=None):
    """Deletes the feed docs `email` authored at or after `since`. Returns how many were removed."""
    if since is None:
        raise ValueError("delete_feed_posts_since needs `since`; refusing to delete a user's whole feed history.")
    posts = get_feed_posts(email, since=since)
    ref = _feed_ref(_db())
    for post in posts:
        ref.document(post["id"]).delete()
    return len(posts)


def delete_user_feed_posts(email=TEST_EMAIL):
    """Deletes every feed post `email` has authored on the test quest; returns the count."""
    posts = get_feed_posts(email)
    ref = _feed_ref(_db())
    for post in posts:
        ref.document(post["id"]).delete()
    return len(posts)


def photo_visibility(email=TEST_EMAIL, activity_key=PHOTO_ACTIVITY_KEY):
    """Where the user's photo for `activity_key` is filed: 'public', 'private', 'both', or None."""
    data = _db().collection("Users").document(_uid(email)).get().to_dict() or {}
    public = activity_key in (data.get("imageSubmitted") or [])
    private = activity_key in (data.get("imageSubmittedPriv") or [])
    return "both" if public and private else "public" if public else "private" if private else None


def clear_photo_submission(email=TEST_EMAIL, activity_key=PHOTO_ACTIVITY_KEY):
    """Removes the activity from the user's public/private photo arrays so a test starts with none on file."""
    _db().collection("Users").document(_uid(email)).update({
        "imageSubmitted": firestore.ArrayRemove([activity_key]),
        "imageSubmittedPriv": firestore.ArrayRemove([activity_key]),
    })


def photo_storage_path(email=TEST_EMAIL, private=True, activity_key=PHOTO_ACTIVITY_KEY):
    """Where the backend files `email`'s photo for the activity in Cloud Storage."""
    folder = "Private/" if private else ""
    return f"OrganizationQuests/{ORG_ID}/Quests/{QUEST_ID}/Images/{activity_key}/{folder}{_uid(email)}.jpg"


def get_stored_photo(email=TEST_EMAIL, private=True):
    """The stored photo as a PIL image (read via the Admin SDK), or None if nothing is stored."""
    from PIL import Image
    _db()  # QA-only guard
    blob = storage.bucket(QA_BUCKET).blob(photo_storage_path(email, private))
    if not blob.exists():
        return None
    return Image.open(io.BytesIO(blob.download_as_bytes())).convert("RGB")


def is_org_admin(email, org_id=ORG_ID):
    """True if the account holds an admin/owner custom claim for the org (how rvsite decides who is an admin)."""
    claims = auth.get_user_by_email(email).custom_claims or {}
    return claims.get(org_id) in ("admin", "owner")


def _web_api_key():
    """The QA web API key, read from the rvsite checkout's .env.qa (the same place the web app gets it)."""
    from conftest import WEB_APP_PATH
    env_file = os.path.join(os.path.abspath(WEB_APP_PATH), ".env.qa")
    with open(env_file) as f:
        for line in f:
            if line.startswith("VITE_FIREBASE_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"\'')
    raise RuntimeError(f"VITE_FIREBASE_API_KEY not found in {env_file}")


def storage_read_status(email, object_path):
    """HTTP status of a Storage read made as `email` (200 if the rules allow it, 403 if not)."""
    custom = auth.create_custom_token(_uid(email)).decode()
    exchange = requests.post(
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken",
        params={"key": _web_api_key()}, json={"token": custom, "returnSecureToken": True}, timeout=20)
    exchange.raise_for_status()
    id_token = exchange.json()["idToken"]
    url = f"https://firebasestorage.googleapis.com/v0/b/{QA_BUCKET}/o/{urllib.parse.quote(object_path, safe='')}"
    return requests.get(url, params={"alt": "media"}, headers={"Authorization": f"Firebase {id_token}"},
                        timeout=20).status_code


def delete_stored_photos(email=TEST_EMAIL):
    """Deletes `email`'s public and private Photo files from Storage; returns the count."""
    _db()  # QA-only guard
    bucket = storage.bucket(QA_BUCKET)
    deleted = 0
    for private in (True, False):
        blob = bucket.blob(photo_storage_path(email, private))
        if blob.exists():
            blob.delete()
            deleted += 1
    return deleted


def reset_photo_state(email=TEST_EMAIL):
    """Start-of-test clean slate: none of `email`'s feed posts or stored Photo files. Returns (posts, files) removed."""
    removed = delete_user_feed_posts(email), delete_stored_photos(email)
    print(f"Cleared {removed[0]} feed post(s) and {removed[1]} stored photo(s) for {email}")
    return removed


def stored_photo_matches(expected_colors, private=True, email=TEST_EMAIL, tolerance=40):
    """True if the stored photo's lower-left and upper-right quarters are `expected_colors` (JPEG shifts colors a bit)."""
    photo = get_stored_photo(email, private)
    if photo is None:
        return False
    points = [(photo.width // 4, photo.height * 3 // 4), (photo.width * 3 // 4, photo.height // 4)]
    return all(all(abs(a - b) <= tolerance for a, b in zip(photo.getpixel(pt), color))
               for pt, color in zip(points, expected_colors))


def private_photo_read_statuses(owner_email, other_email):
    """Storage read status of the owner's private photo as (owner, other); expect (200, 403)."""
    path = photo_storage_path(owner_email, private=True)
    return storage_read_status(owner_email, path), storage_read_status(other_email, path)
