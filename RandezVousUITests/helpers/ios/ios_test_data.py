"""Accounts, usernames and quest IDs the iOS tests share (all in randezvous-qa)."""
QUEST_ID = "test-automation-quest"
TEST_EMAIL = "oalson123@gmail.com"
TEST_PASSWORD = "OmarTest123"
TEST_USERNAME = "OmarTesting"
GUEST_USERNAME = "AutomatedTester"
# A second email/password account, on the allowed domain of the restricted quests.
OTHER_EMAIL = "test_user@randezvous.com"
OTHER_PASSWORD = "OmarTest123"
OTHER_USERNAME = "webrightdomain"

# An email/password account that also lists a fake google.com provider on an allowed domain (created per test by
# access_data_helper.create_google_domain_password_user), so iOS can sign in without Google's screen.
GOOGLE_DOMAIN_EMAIL = "ios_google_domain@randezvous.com"
GOOGLE_DOMAIN_UID = "qa-ios-google-domain-user"
GOOGLE_DOMAIN_PASSWORD = "OmarTest123"
GOOGLE_DOMAIN_USERNAME = "iosgoogledomain"
# Same trick with a Google provider on a domain the restricted quests don't allow.
WRONG_GOOGLE_DOMAIN_EMAIL = "ios_google_wrong_domain@gmail.com"
WRONG_GOOGLE_DOMAIN_UID = "qa-ios-google-wrong-domain-user"
WRONG_GOOGLE_DOMAIN_USERNAME = "iosgooglewrongdomain"
