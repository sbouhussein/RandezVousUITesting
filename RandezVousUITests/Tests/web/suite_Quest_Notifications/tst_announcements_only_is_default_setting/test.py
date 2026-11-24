import pytest

from helpers.common.access_data_helper import delete_subscriber, edited_quest
from helpers.web import HomepageHelper, NotificationSettingHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL, ORG_ID, TEST_USER_EMAIL


# Application gap: joining on web never writes a subscriber doc, so a quest's default notification setting isn't applied (iOS applies it).
@pytest.mark.xfail(strict=True, reason="Application gap: rvsite doesn't apply a quest's default notification setting; a new web member sees None")
@pytest.mark.usefixtures("fresh_web_backend")
@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_announcements_only_is_default_setting(desktop_safari_driver):
    """On a quest whose default notification setting is Announcements only, a new member starts on it."""
    driver = desktop_safari_driver
    delete_subscriber(TEST_USER_EMAIL, ORG_ID, ACTIVITY_QUEST_ID)
    with edited_quest(ORG_ID, ACTIVITY_QUEST_ID, defaultNotificationSetting=1):  # restored afterwards; edited before the page loads (rvsite caches quests)
        driver.get(BASE_URL)
        HomepageHelper(driver).sign_in_and_find_quest(ACTIVITY_QUEST_ID)
        setting = NotificationSettingHelper(driver)
        setting.grant_browser_permission()
        assert setting.current_label() == NotificationSettingHelper.LABELS[1], f"Default should be Announcements only, got {setting.current_label()}"
