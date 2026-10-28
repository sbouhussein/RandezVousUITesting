import pytest

from helpers.ios.firebase_cleanup_helper import cleanup_user_data
from helpers.ios.ios_test_data import OTHER_EMAIL, TEST_EMAIL


@pytest.fixture(autouse=True)
def leaderboard_cleanup():
    """Resets quest history, grants and leaderboard rows for both test accounts before and after."""
    for email in (TEST_EMAIL, OTHER_EMAIL):
        cleanup_user_data(target_email=email)
    yield
    for email in (TEST_EMAIL, OTHER_EMAIL):
        cleanup_user_data(target_email=email)
