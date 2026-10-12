import pytest

from helpers.web.access_control_helper import AccessControlHelper
from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_test_data import ORG_ID, TEAM_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, team_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_team_view_shows_restricted_banner_when_banned(desktop_safari_driver, banned_user):
    """QUEST_ONBOARDING_UX.md row 6b/13: TeamView now shows RestrictedBanner for a banned
    user instead of an empty "Join a Team" picker."""
    driver = desktop_safari_driver
    banned_user(TEST_USER_EMAIL, ORG_ID, TEAM_QUEST_ID)

    nav = HomepageHelper(driver)
    nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    nav.wait_until_signed_in()

    driver.get(team_url(TEAM_QUEST_ID))

    access = AccessControlHelper(driver)
    assert access.is_restricted_banner_visible(custom_timeout=30), (
        "Expected TeamView to show the RestrictedBanner for a banned user."
    )
    assert access.is_visible(access.back_to_quest_link), "Expected a way back to the quest page."
