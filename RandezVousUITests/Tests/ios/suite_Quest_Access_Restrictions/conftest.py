import pytest

from helpers.common.access_data_helper import restrict_user, unban_user
from helpers.ios.firebase_cleanup_helper import cleanup_user_data
from helpers.web.quest_test_data import ORG_ID, RIGHT_DOMAIN_EMAIL, TEST_USER_EMAIL


@pytest.fixture(autouse=True)
def access_cleanup():
    """Resets quest history and grants for both test accounts before and after, so a join is always fresh."""
    for email in (TEST_USER_EMAIL, RIGHT_DOMAIN_EMAIL):
        cleanup_user_data(target_email=email)
    yield
    for email in (TEST_USER_EMAIL, RIGHT_DOMAIN_EMAIL):
        cleanup_user_data(target_email=email)


@pytest.fixture
def restrict():
    """Factory for restrictions in the test org; every one it creates is removed on teardown, pass or fail."""
    created = set()

    def make(email, **kwargs):
        doc_id = restrict_user(email, ORG_ID, **kwargs)
        created.add(doc_id)
        return doc_id

    yield make
    for doc_id in created:
        unban_user(ORG_ID, doc_id)
