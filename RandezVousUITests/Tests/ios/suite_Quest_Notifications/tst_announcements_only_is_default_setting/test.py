import time

import pytest

from helpers.common.access_data_helper import delete_subscriber, edited_quest, get_notification_setting
from helpers.ios import CustomQuestPage, FeedHelper, NotificationHelper
from helpers.ios.ios_test_data import QUEST_ID, TEST_EMAIL
from helpers.web.quest_test_data import ORG_ID


def wait_for_setting(timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        setting = get_notification_setting(TEST_EMAIL, ORG_ID, QUEST_ID)
        if setting is not None:
            return setting
        time.sleep(1)
    return None


@pytest.mark.cleanup(type="email", value=TEST_EMAIL)
def test_announcements_only_is_default_setting(rv_driver):
    """On a quest whose default notification setting is Announcements Only, a new member starts on it: notified of announcements, not of feed posts."""
    delete_subscriber(TEST_EMAIL, ORG_ID, QUEST_ID)
    with edited_quest(ORG_ID, QUEST_ID, defaultNotificationSetting=1):  # the app reads quests live; restored afterwards
        CustomQuestPage(rv_driver).sign_in_and_join(keep_keychain=True)
        FeedHelper(rv_driver).open_feed()
        default = wait_for_setting()
        assert default == 1, f"A new member should start on the quest's default, Announcements Only (1), got {default}"
        bell = NotificationHelper(rv_driver)
        bell.lock_device()
        item, announcement = bell.lock_screen_notification(ORG_ID, QUEST_ID, "announcement", expected=True)
        _, post = bell.lock_screen_notification(ORG_ID, QUEST_ID, "post", expected=False)
        bell.unlock_device()
        assert announcement and f"{item.title}, {item.body}" in announcement, f"An announcement should reach the lock screen on the default setting, got: {announcement}"
        assert not post, f"A feed post should not reach the lock screen on the default setting, got: {post}"
