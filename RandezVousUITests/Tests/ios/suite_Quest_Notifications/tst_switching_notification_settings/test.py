import pytest

from helpers.common.access_data_helper import get_notification_setting
from helpers.ios import CustomQuestPage, FeedHelper, NotificationHelper
from helpers.ios.ios_test_data import QUEST_ID, TEST_EMAIL
from helpers.web.quest_test_data import ORG_ID


def arrives(bell, kind, expected):
    """Sends `kind` while locked; returns whether a lock-screen notification arrived, asserting that one that does carries the right title and message."""
    item, label = bell.lock_screen_notification(ORG_ID, QUEST_ID, kind, expected)
    if label:
        assert f"{item.title}, {item.body}" in label, f"The {kind} notification should read '{item.title}' / '{item.body}', but the lock screen shows: {label}"
    return bool(label)

EXPECTED = {0: (False, False), 1: (True, False), 2: (True, True)}  # setting -> (announcement, post) reach the lock screen


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_switching_notification_settings(rv_driver):
    """Switching the setting changes what reaches the lock screen straight away, checked against both kinds of item each time."""
    CustomQuestPage(rv_driver).sign_in_and_join(keep_keychain=True)
    FeedHelper(rv_driver).open_feed()
    bell = NotificationHelper(rv_driver)
    for setting in (1, 2, 0, 1):
        bell.choose_setting(setting)
        assert get_notification_setting(TEST_EMAIL, ORG_ID, QUEST_ID) == setting, f"Setting {setting} should be saved to the quest"
        bell.lock_device()
        got = (arrives(bell, "announcement", EXPECTED[setting][0]), arrives(bell, "post", EXPECTED[setting][1]))
        bell.unlock_device()
        assert got == EXPECTED[setting], f"Setting {setting}: expected (announcement, post) on the lock screen {EXPECTED[setting]}, got {got}"
