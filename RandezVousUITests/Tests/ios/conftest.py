import pytest

from helpers.common.access_data_helper import create_google_domain_password_user, delete_user_by_email, temporary_password_user
from helpers.ios.ios_test_data import (
    GOOGLE_DOMAIN_EMAIL, GOOGLE_DOMAIN_PASSWORD, GOOGLE_DOMAIN_UID, GOOGLE_DOMAIN_USERNAME,
    WRONG_GOOGLE_DOMAIN_EMAIL, WRONG_GOOGLE_DOMAIN_UID, WRONG_GOOGLE_DOMAIN_USERNAME,
)
from helpers.web.quest_test_data import (
    ORG_ID, SECOND_USER_EMAIL, SECOND_USER_PASSWORD, SECOND_USER_UID, SECOND_USER_USERNAME,
)


@pytest.fixture
def domain_user():
    """An account on the allowed domain that iOS can sign in to with a password (see create_google_domain_password_user);
    created for the test and deleted afterwards. Returns (email, password)."""
    create_google_domain_password_user(GOOGLE_DOMAIN_EMAIL, GOOGLE_DOMAIN_PASSWORD, GOOGLE_DOMAIN_UID, GOOGLE_DOMAIN_USERNAME)
    yield GOOGLE_DOMAIN_EMAIL, GOOGLE_DOMAIN_PASSWORD
    delete_user_by_email(GOOGLE_DOMAIN_EMAIL)


@pytest.fixture
def wrong_domain_user():
    """Like domain_user, but its fake Google provider is on a domain the restricted quests don't allow. Returns (email, password)."""
    create_google_domain_password_user(
        WRONG_GOOGLE_DOMAIN_EMAIL, GOOGLE_DOMAIN_PASSWORD, WRONG_GOOGLE_DOMAIN_UID, WRONG_GOOGLE_DOMAIN_USERNAME)
    yield WRONG_GOOGLE_DOMAIN_EMAIL, GOOGLE_DOMAIN_PASSWORD
    delete_user_by_email(WRONG_GOOGLE_DOMAIN_EMAIL)


@pytest.fixture
def second_user():
    """A throwaway email/password account (not on any restricted domain) for tests that need two users; returns (email, password, username)."""
    with temporary_password_user(SECOND_USER_EMAIL, SECOND_USER_PASSWORD, SECOND_USER_UID, SECOND_USER_USERNAME, ORG_ID):
        yield SECOND_USER_EMAIL, SECOND_USER_PASSWORD, SECOND_USER_USERNAME
