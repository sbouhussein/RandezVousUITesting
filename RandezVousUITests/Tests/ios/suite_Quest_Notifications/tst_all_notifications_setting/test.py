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


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_all_notifications_setting(rv_driver):
    """With All Notifications, both an announcement and a feed post reach the lock screen with the right message."""
    CustomQuestPage(rv_driver).sign_in_and_join(keep_keychain=True)
    FeedHelper(rv_driver).open_feed()
    bell = NotificationHelper(rv_driver)
    bell.choose_setting(2)
    assert get_notification_setting(TEST_EMAIL, ORG_ID, QUEST_ID) == 2, "Choosing All Notifications should be saved to the quest"

    bell.lock_device()
    announcement = arrives(bell, "announcement", expected=True)
    post = arrives(bell, "post", expected=True)
    bell.unlock_device()
    assert announcement, "An announcement should reach the lock screen with All Notifications"
    assert post, "A feed post should reach the lock screen with All Notifications"
