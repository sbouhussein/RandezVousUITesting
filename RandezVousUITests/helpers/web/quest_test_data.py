"""Single source of truth for IDs/credentials the access-control suites
(suite_Quest_Onboarding_Access, suite_Domain_Specific_Tests) exercise, plus URL builders per quest surface."""

BASE_URL = "http://localhost:5173"
ORG_ID = "test-3hmYPwC0cFa6zch5syk7"

TEAM_QUEST_ID = "KiRNgaKImQ4ooCKLfLH0"                    # team-enabled, open access
DOMAIN_RESTRICTED_TEAM_QUEST_ID = "5gbhKSXqlIo9Id9q8cL1"   # team-enabled, randezvous.com only
OPEN_QUEST_ID = "BgCEoAqZVZMiJdIz9kes"                     # no team, open access
RESTRICTED_QUEST_ID = "ZmDCYKTwmuEWkR89ZA1X"               # no team, randezvous.com only

TEST_USER_EMAIL = "oalson123@gmail.com"
TEST_USER_PASSWORD = "OmarTest123"
WRONG_DOMAIN_EMAIL = "unauthorized_domain_user@yahoo.com"
WRONG_DOMAIN_PASSWORD = "OmarTest123"


def onboarding_url(qid, org_id=ORG_ID, base_url=BASE_URL):
    return f"{base_url}/quest/organization/{org_id}/{qid}/onboarding"


def team_url(qid, org_id=ORG_ID, base_url=BASE_URL):
    return f"{base_url}/quest/organization/{org_id}/{qid}/team"


def feed_url(qid, org_id=ORG_ID, base_url=BASE_URL):
    return f"{base_url}/feed/organization/{org_id}/{qid}"


def quest_url(qid, org_id=ORG_ID, base_url=BASE_URL):
    return f"{base_url}/quest/organization/{org_id}/{qid}"
