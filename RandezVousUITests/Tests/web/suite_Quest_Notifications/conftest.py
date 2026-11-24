from datetime import datetime, timezone

import pytest

from helpers.common.notification_data_helper import delete_web_tokens
from helpers.web.quest_test_data import TEST_USER_EMAIL

EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def no_leftover_web_tokens():
    """The function pushes to every web token on the account; clear the dead ones earlier browsers registered, before and after."""
    delete_web_tokens(TEST_USER_EMAIL, EPOCH)
    yield
    delete_web_tokens(TEST_USER_EMAIL, EPOCH)
