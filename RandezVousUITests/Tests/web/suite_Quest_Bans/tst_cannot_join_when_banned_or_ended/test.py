import pytest

from helpers.common.access_data_helper import clear_stale_grant, has_quest_grant, unban_user
from helpers.web import AccessControlHelper, HomepageHelper, OnboardingPageHelper
from helpers.web.quest_test_data import (
    EXPIRED_QUEST_ID, OPEN_QUEST_ID, ORG_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url,
)

BAN_CASES = [
    ("org-wide ban", dict(level="org")),
    ("ban filed under another uid", dict(level="quest", qid=OPEN_QUEST_ID, doc_id="old-deleted-account-uid")),
]


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_cannot_join_when_banned_or_ended(desktop_safari_driver, restrict):
    """Banned users get the restricted banner and an ended quest is viewable but not joinable; none gets access."""
    driver = desktop_safari_driver
    nav, access, onboarding = HomepageHelper(driver), AccessControlHelper(driver), OnboardingPageHelper(driver)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.wait_until_signed_in()

    for name, restriction in BAN_CASES:
        clear_stale_grant(TEST_USER_EMAIL, OPEN_QUEST_ID)
        doc_id = restrict(TEST_USER_EMAIL, **restriction)
        driver.get(onboarding_url(OPEN_QUEST_ID))
        onboarding.click_start_quest()

        assert access.is_restricted_banner_visible(custom_timeout=15), f"Expected the restricted banner ({name})"
        assert not has_quest_grant(TEST_USER_EMAIL, OPEN_QUEST_ID), f"A banned join must not create a grant ({name})"
        unban_user(ORG_ID, doc_id)  # so the next case isn't also blocked by this one

    clear_stale_grant(TEST_USER_EMAIL, EXPIRED_QUEST_ID)
    driver.get(onboarding_url(EXPIRED_QUEST_ID))
    assert access.is_quest_ended_banner_visible(custom_timeout=15), "Expected the 'This quest ended' banner"
    onboarding.click_view_quest()
    assert not has_quest_grant(TEST_USER_EMAIL, EXPIRED_QUEST_ID), "Viewing an ended quest must not grant access"
