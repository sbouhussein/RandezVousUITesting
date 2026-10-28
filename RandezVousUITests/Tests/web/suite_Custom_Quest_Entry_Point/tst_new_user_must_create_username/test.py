import pytest

from helpers.common.access_data_helper import create_user_without_username, delete_user_by_email
from helpers.web import HomepageHelper
from helpers.web.quest_test_data import TEST_USER_PASSWORD as PASSWORD

EMAIL = "web_no_username@randezvous.com"


@pytest.fixture
def new_account():
    create_user_without_username(EMAIL, PASSWORD)
    yield
    delete_user_by_email(EMAIL)


def test_new_user_must_create_username(desktop_safari_driver, new_account):
    """An account with no username is asked to create one before it can use quests."""
    nav = HomepageHelper(desktop_safari_driver)
    nav.login(EMAIL, PASSWORD)

    assert nav.is_create_username_visible(), "Expected the 'Create Your Username' step for an account with no username"
