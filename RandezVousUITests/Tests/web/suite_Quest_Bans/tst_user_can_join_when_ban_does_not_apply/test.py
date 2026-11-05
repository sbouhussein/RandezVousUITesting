from datetime import timedelta

import pytest

from helpers.common.access_data_helper import clear_stale_grant, has_quest_grant
from helpers.web import HomepageHelper, OnboardingPageHelper, QuestHelper
from helpers.web.quest_test_data import (
    ACTIVITY_QUEST_ID, OPEN_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url,
)

EXPIRED = timedelta(hours=-1)
CASES = [
    ("ban on a different quest", dict(level="quest", qid=ACTIVITY_QUEST_ID)),
    ("expired quest ban", dict(level="quest", qid=OPEN_QUEST_ID, expires_in=EXPIRED)),
    ("expired org ban", dict(level="org", expires_in=EXPIRED)),
]


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_user_can_join_when_ban_does_not_apply(desktop_safari_driver, restrict):
    """Bans for another quest or that have expired don't stop the user from joining."""
    nav = HomepageHelper(desktop_safari_driver)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.wait_until_signed_in()
    for name, restriction in CASES:
        clear_stale_grant(TEST_USER_EMAIL, OPEN_QUEST_ID)
        restrict(TEST_USER_EMAIL, **restriction)
        desktop_safari_driver.get(onboarding_url(OPEN_QUEST_ID))
        OnboardingPageHelper(desktop_safari_driver).click_start_quest()
        quest = QuestHelper(desktop_safari_driver)

        assert quest.is_visible(quest.honor_activity_locator, custom_timeout=30), f"Should join with {name}"
        assert has_quest_grant(TEST_USER_EMAIL, OPEN_QUEST_ID), f"No grant written ({name})"
