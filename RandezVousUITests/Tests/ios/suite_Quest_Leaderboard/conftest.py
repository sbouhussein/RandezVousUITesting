import pytest

from helpers.ios.firebase_cleanup_helper import cleanup_user_data
from helpers.ios.ios_test_data import TEST_EMAIL


@pytest.fixture(autouse=True)
def leaderboard_cleanup():
    """Resets the test account's quest history, grants and leaderboard row before and after (the `second_user` is created and removed per test)."""
    cleanup_user_data(target_email=TEST_EMAIL)
    yield
    cleanup_user_data(target_email=TEST_EMAIL)
