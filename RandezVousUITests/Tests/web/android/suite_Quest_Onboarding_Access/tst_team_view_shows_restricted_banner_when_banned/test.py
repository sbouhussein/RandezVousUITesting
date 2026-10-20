import pytest

from helpers.web import AccessControlHelper, HomepageHelper
from helpers.web.quest_test_data import ORG_ID, TEAM_QUEST_ID, TEST_USER_EMAIL, team_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_team_view_shows_restricted_banner_when_banned(desktop_safari_driver, banned_user):
    """TeamView shows RestrictedBanner for a banned user."""
    banned_user(TEST_USER_EMAIL, ORG_ID, TEAM_QUEST_ID)
    HomepageHelper(desktop_safari_driver).sign_in_and_open(team_url(TEAM_QUEST_ID))

    access = AccessControlHelper(desktop_safari_driver)
    assert access.is_restricted_banner_visible(custom_timeout=30), "Expected TeamView to show the RestrictedBanner"
    assert access.is_visible(access.back_to_quest_link), "Expected a way back to the quest page"
