from helpers.common.access_data_helper import has_quest_grant
from helpers.ios import AccessHelper
from helpers.ios.ios_test_data import OTHER_EMAIL, OTHER_PASSWORD, TEST_EMAIL, TEST_PASSWORD
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID


def test_email_password_user_must_use_google_for_domain_quest(rv_driver):
    """Email/password accounts can't join a domain-restricted quest, even with an email on the allowed domain
    (spoofed org email): access needs a Google sign-in, which Switch Account starts (not driven)."""
    access = AccessHelper(rv_driver)
    for email, password in ((TEST_EMAIL, TEST_PASSWORD), (OTHER_EMAIL, OTHER_PASSWORD)):
        access.sign_in(email, password)
        access.find_quest(RESTRICTED_QUEST_ID)
        assert access.wait_for_text("Requires an account from: @randezvous.com"), f"{email} should see the requirement"
        assert access.wait_for_text("doesn't have access", timeout=5), f"{email} should be told it lacks access"

        access.click_start_quest()
        assert not access.is_joined(), f"{email} must not reach the restricted quest"
        assert not has_quest_grant(email, RESTRICTED_QUEST_ID), f"{email} must not get a quest grant"
        assert access.wait_for_text("Switch Account", timeout=5), f"{email} should be offered Switch Account"
