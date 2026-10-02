import pytest

from helpers.web.access_control_helper import AccessControlHelper
from helpers.web.firebase_test_data_helper import clear_stale_grant
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_test_data import (
    DOMAIN_RESTRICTED_TEAM_QUEST_ID, WRONG_DOMAIN_EMAIL, WRONG_DOMAIN_PASSWORD, team_url,
)


@pytest.mark.cleanup(type="email", value=WRONG_DOMAIN_EMAIL)
def test_team_view_shows_locked_screen_for_wrong_domain(desktop_safari_driver):
    """QUEST_ONBOARDING_UX.md row 13: TeamView now shows a locked-quest screen for a
    wrong-domain user instead of an empty "Join a Team" picker."""
    driver = desktop_safari_driver
    # A stale grant would bypass the domain check (canViewQuestDetails in backend/routes/quests.js).
    clear_stale_grant(WRONG_DOMAIN_EMAIL, DOMAIN_RESTRICTED_TEAM_QUEST_ID)

    nav = HomepageHelper(driver)
    nav.login(WRONG_DOMAIN_EMAIL, WRONG_DOMAIN_PASSWORD)
    nav.wait_until_signed_in()

    driver.get(team_url(DOMAIN_RESTRICTED_TEAM_QUEST_ID))

    access = AccessControlHelper(driver)
    assert access.is_restricted_quest_screen_visible(custom_timeout=30), (
        "Expected TeamView's locked-quest screen for a wrong-domain user."
    )
    assert access.is_visible(access.domain_requirement_text), "Expected the required-domain hint."
    assert access.is_visible(access.switch_accounts_button), "Expected a 'Switch accounts' remediation button."
