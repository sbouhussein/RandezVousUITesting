"""Seeds the randezvous-qa web fixtures (idempotent; QA only): quests cloned from `test-automation-quest` plus the test accounts."""
import copy
import datetime
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import firebase_admin
from firebase_admin import auth, credentials, firestore, storage

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "RandezVousUITests"))
from helpers.web import quest_test_data as data  # noqa: E402

QA_PROJECT = "randezvous-qa"
QA_BUCKET = "randezvous-qa.firebasestorage.app"
KEY_PATH = REPO_ROOT / "private" / "service-account-key-qa.json"
TEMPLATE_QID = "test-automation-quest"

UTC = datetime.timezone.utc
ACTIVE_START = datetime.datetime(2026, 9, 17, 3, 0, tzinfo=UTC)
ACTIVE_END = datetime.datetime(2030, 9, 17, 3, 0, tzinfo=UTC)
EXPIRED_START = datetime.datetime(2026, 8, 1, 14, 0, tzinfo=UTC)
EXPIRED_END = datetime.datetime(2026, 9, 6, 14, 5, tzinfo=UTC)

# activityTypes entries read "<type> challenge:<id>" -- the type prefix isn't the validation method name for honor.
TYPE_PREFIX = {"honorCode": "honor", "photo": "photo", "prompt": "prompt", "location": "location"}

RESTRICTED_POLICY = {"type": "google_hd", "allowedDomains": ["randezvous.com"]}


def activity(aid, name, method, **extra):
    """One entry of a quest's activities JSON; `name` is the card heading the web helpers locate on."""
    entry = {
        "id": aid, "name": name, "description": "", "address": "", "customStartString": "",
        "eligibleValidationMethods": [method], "price": {"value": 0, "unknown": True},
        "indoor": False, "atHome": False, "todo": [], "estimatedLength": "", "siteLink": "",
        "showDetailed": False,
    }
    entry.update(extra)
    return entry


HONOR = activity(1000, "Honor Code Activity", "honorCode")
PHOTO = activity(1001, "Photo Activity", "photo")
PROMPT = activity(1002, "Prompt Activity", "prompt")
TRIVIA = activity(1003, "Trivia Activity", "prompt")
LOCATION = activity(1004, "Location Activity", "location",
                    address="Web test location (mocked via geolocation override)",
                    coordinates={"latitude": data.ACTIVITY_QUEST_LOCATION[0],
                                 "longitude": data.ACTIVITY_QUEST_LOCATION[1]})

# (qid, title, description, activities, extras). `prompts`/`answers` map activity id -> text.
FIXTURES = [
    dict(qid=data.ACTIVITY_QUEST_ID, title="Web Activity Quest",
         description="Web UI tests: one of every activity type.",
         activities=[HONOR, PHOTO, PROMPT, TRIVIA, LOCATION],
         prompts={"1002": "Say Something", "1003": 'Type "Trivia"'}, answers={"1003": ["Trivia"]}),
    dict(qid=data.EXPIRED_QUEST_ID, title="Web Expired Quest",
         description="Web UI tests: a quest whose end time has passed.",
         activities=[HONOR, PROMPT], prompts={"1002": "Say Something"}, answers={},
         start=EXPIRED_START, end=EXPIRED_END),
    dict(qid=data.TEAM_QUEST_ID, title="Web Team Quest (open)",
         description="Web UI tests: team-enabled, open to any account.",
         activities=[HONOR], team=True),
    dict(qid=data.DOMAIN_RESTRICTED_TEAM_QUEST_ID, title="Web Team Quest (randezvous.com only)",
         description="Web UI tests: team-enabled, restricted to randezvous.com Google accounts.",
         activities=[HONOR], team=True, policy=RESTRICTED_POLICY),
    dict(qid=data.OPEN_QUEST_ID, title="Web Open Quest",
         description="Web UI tests: no teams, open to any account.",
         activities=[HONOR]),
    dict(qid=data.RESTRICTED_QUEST_ID, title="Web Restricted Quest (randezvous.com only)",
         description="Web UI tests: no teams, restricted to randezvous.com Google accounts.",
         activities=[HONOR], policy=RESTRICTED_POLICY),
]

# (email, password, username); a username-less account never leaves /login, so each needs one.
ACCOUNTS = [
    (data.TEST_USER_EMAIL, data.TEST_USER_PASSWORD, None),
    (data.WRONG_DOMAIN_EMAIL, data.WRONG_DOMAIN_PASSWORD, data.WRONG_DOMAIN_USERNAME),
    (data.RIGHT_DOMAIN_EMAIL, data.RIGHT_DOMAIN_PASSWORD, data.RIGHT_DOMAIN_USERNAME),
]


def init():
    cred = credentials.Certificate(str(KEY_PATH))
    if cred.project_id != QA_PROJECT:
        sys.exit(f"Refusing to seed: {KEY_PATH.name} belongs to '{cred.project_id}', not '{QA_PROJECT}'.")
    firebase_admin.initialize_app(cred, {"storageBucket": QA_BUCKET})
    return firestore.client(), storage.bucket()


def seed_quest(db, bucket, template, fx):
    qid = fx["qid"]
    doc = copy.deepcopy(template)
    doc.update(
        id=qid, questCode=qid, title=fx["title"], description=fx["description"],
        orgId=data.ORG_ID, visible=True, hasFeed=True,
        activityTypes=[f"{TYPE_PREFIX[a['eligibleValidationMethods'][0]]} challenge:{a['id']}" for a in fx["activities"]],
        activityPrompts=fx.get("prompts", {}), activityPromptAnswers=fx.get("answers", {}),
        accessPolicy=fx.get("policy"),
        startTime=fx.get("start", ACTIVE_START), endTime=fx.get("end", ACTIVE_END),
        infoUpdatedAt=firestore.SERVER_TIMESTAMP,
    )
    doc.pop("teamSetup", None)
    if fx.get("team"):
        doc["teamSetup"] = {"enabled": True}

    org = db.collection("Organizations").document(data.ORG_ID)
    org.collection("quests").document(qid).set(doc)
    bucket.blob(f"OrganizationQuests/{data.ORG_ID}/Quests/{qid}/{qid}.json").upload_from_string(
        json.dumps(fx["activities"]), content_type="application/json")
    db.collection("quest_index").document(qid).set(
        {"qid": qid, "orgId": data.ORG_ID, "createdAt": firestore.SERVER_TIMESTAMP})
    org.update({"privateQids": firestore.ArrayUnion([qid])})
    print(f"  quest  {qid}")


def seed_account(db, email, password, username):
    try:
        user = auth.get_user_by_email(email)
        state = "exists"
    except auth.UserNotFoundError:
        user = auth.create_user(email=email, password=password, email_verified=True)
        state = "created"
    if username:
        # Mirrors POST /api/user/create-username; merge keeps fields the backend already wrote.
        clash = list(db.collection("Users").where("username", "==", username).limit(1).stream())
        if clash and clash[0].id != user.uid:
            sys.exit(f"Username '{username}' is already taken by another QA user.")
        db.collection("Users").document(user.uid).set(
            {"username": username, "uid": user.uid, "email": email,
             "lastUpdated": firestore.SERVER_TIMESTAMP}, merge=True)
    print(f"  user   {email} ({state}{', username ' + username if username else ''})")


def seed_google_account(db, uid, email, username):
    """Fabricates a Google-provider user (a `google.com` providerData entry) via import_users(); idempotent, QA only."""
    record = auth.ImportUserRecord(
        uid=uid, email=email, email_verified=True, display_name=f"QA {username}",
        provider_data=[auth.UserProvider(uid=f"qa-google-{uid}", provider_id="google.com", email=email,
                                         display_name=f"QA {username}")])
    result = auth.import_users([record])
    if result.failure_count:
        sys.exit(f"import_users failed for {email}: {[e.reason for e in result.errors]}")
    clash = list(db.collection("Users").where("username", "==", username).limit(1).stream())
    if clash and clash[0].id != uid:
        sys.exit(f"Username '{username}' is already taken by another QA user.")
    db.collection("Users").document(uid).set(
        {"username": username, "uid": uid, "email": email, "lastUpdated": firestore.SERVER_TIMESTAMP}, merge=True)
    providers = [p.provider_id for p in auth.get_user(uid).provider_data]
    print(f"  user   {email} (google.com provider, uid {uid}, username {username}; providers now {providers})")


def main():
    db, bucket = init()
    org = db.collection("Organizations").document(data.ORG_ID)
    if not org.get().exists:
        sys.exit(f"Organizations/{data.ORG_ID} not found in {QA_PROJECT}.")
    template_ref = org.collection("quests").document(TEMPLATE_QID).get()
    if not template_ref.exists:
        sys.exit(f"Template quest {TEMPLATE_QID} not found in {QA_PROJECT}; can't clone fixtures.")
    template = template_ref.to_dict()

    print(f"Seeding {QA_PROJECT} web fixtures (org {data.ORG_ID}):")
    for fx in FIXTURES:
        seed_quest(db, bucket, template, fx)
    for email, password, username in ACCOUNTS:
        seed_account(db, email, password, username)
    seed_google_account(db, data.GOOGLE_DOMAIN_UID, data.GOOGLE_DOMAIN_EMAIL, data.GOOGLE_DOMAIN_USERNAME)
    seed_google_account(db, data.GOOGLE_WRONG_DOMAIN_UID, data.GOOGLE_WRONG_DOMAIN_EMAIL,
                        data.GOOGLE_WRONG_DOMAIN_USERNAME)
    print("Done.")


if __name__ == "__main__":
    main()
