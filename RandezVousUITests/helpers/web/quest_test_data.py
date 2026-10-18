"""Single source of truth for the randezvous-qa fixtures, credentials and ports the web suites use, plus URL builders."""

# rvsite's QA dev server (`npm start`: Vite --mode qa on 5174 + backend on 3000, both against randezvous-qa).
WEB_PORT = "5174"
BACKEND_PORT = "3000"
BASE_URL = f"http://localhost:{WEB_PORT}"
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"

# Fixtures are (re)created by scripts/firebase/seed_qa_web_fixtures.py; change IDs here and re-run it.
ORG_ID = "test-org"

ACTIVITY_QUEST_ID = "web-activity-quest"                  # honor, photo, prompt, trivia, location; entered by code
EXPIRED_QUEST_ID = "web-expired-quest"                    # honor + prompt, end time in the past
TEAM_QUEST_ID = "web-team-open"                           # team-enabled, open access
DOMAIN_RESTRICTED_TEAM_QUEST_ID = "web-team-domain"       # team-enabled, randezvous.com only
OPEN_QUEST_ID = "web-open"                                # no team, open access
RESTRICTED_QUEST_ID = "web-restricted"                    # no team, randezvous.com only

# The geolocation the web tests mock when completing ACTIVITY_QUEST_ID's location activity.
ACTIVITY_QUEST_LOCATION = (41.282778, -157.829444)

TEST_USER_EMAIL = "oalson123@gmail.com"
TEST_USER_PASSWORD = "OmarTest123"
WRONG_DOMAIN_EMAIL = "unauthorized_domain_user@yahoo.com"
WRONG_DOMAIN_PASSWORD = "OmarTest123"
WRONG_DOMAIN_USERNAME = "webwrongdomain"      # usernames are lowercase, 3-20 chars of [a-z0-9_]
RIGHT_DOMAIN_EMAIL = "test_user@randezvous.com"
RIGHT_DOMAIN_PASSWORD = "OmarTest123"
RIGHT_DOMAIN_USERNAME = "webrightdomain"

# A fabricated Google-provider account on an allowed domain, signed in by custom token (no password); email/password accounts fail google_hd.
GOOGLE_DOMAIN_UID = "qa-web-google-domain-user"
GOOGLE_DOMAIN_EMAIL = "google_domain_user@randezvous.com"
GOOGLE_DOMAIN_USERNAME = "webgoogledomain"

# A fabricated Google account on the WRONG domain (gmail.com), rejected on the wrong-domain branch.
GOOGLE_WRONG_DOMAIN_UID = "qa-web-google-wrong-domain-user"
GOOGLE_WRONG_DOMAIN_EMAIL = "google_wrong_domain_user@gmail.com"
GOOGLE_WRONG_DOMAIN_USERNAME = "webgooglewrongdomain"


def onboarding_url(qid, org_id=ORG_ID, base_url=BASE_URL):
    return f"{base_url}/quest/organization/{org_id}/{qid}/onboarding"


def team_url(qid, org_id=ORG_ID, base_url=BASE_URL):
    return f"{base_url}/quest/organization/{org_id}/{qid}/team"


def feed_url(qid, org_id=ORG_ID, base_url=BASE_URL):
    return f"{base_url}/feed/organization/{org_id}/{qid}"


def quest_url(qid, org_id=ORG_ID, base_url=BASE_URL):
    return f"{base_url}/quest/organization/{org_id}/{qid}"
