import pytest

from helpers.common.access_data_helper import clear_stale_grant
from helpers.web import AccessControlHelper, HomepageHelper
from helpers.web.quest_test_data import (
    DOMAIN_RESTRICTED_TEAM_QUEST_ID, WRONG_DOMAIN_EMAIL, WRONG_DOMAIN_PASSWORD, team_url,
)


@pytest.mark.cleanup(type="email", value=WRONG_DOMAIN_EMAIL)
def test_team_view_shows_locked_screen_for_wrong_domain(desktop_safari_driver):
    """TeamView shows a locked-quest screen for a wrong-domain user."""
    clear_stale_grant(WRONG_DOMAIN_EMAIL, DOMAIN_RESTRICTED_TEAM_QUEST_ID)  # a stale grant skips the domain check
    HomepageHelper(desktop_safari_driver).sign_in_and_open(
        team_url(DOMAIN_RESTRICTED_TEAM_QUEST_ID), WRONG_DOMAIN_EMAIL, WRONG_DOMAIN_PASSWORD)

    access = AccessControlHelper(desktop_safari_driver)
    assert access.is_restricted_quest_screen_visible(custom_timeout=30), "Expected TeamView's locked-quest screen"
    assert access.is_visible(access.domain_requirement_text), "Expected the required-domain hint"
    assert access.is_visible(access.switch_accounts_button), "Expected a 'Switch accounts' button"
