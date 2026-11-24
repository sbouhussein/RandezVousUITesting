import pytest

from helpers.common.access_data_helper import get_notification_setting
from helpers.common.notification_data_helper import user_notified
from helpers.web import HomepageHelper, NotificationSettingHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL, ORG_ID, TEST_USER_EMAIL


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_all_activity_notifications_setting(desktop_safari_driver):
    """With All activity, the user is selected for both an announcement and a feed post."""
    driver = desktop_safari_driver
    driver.get(BASE_URL)
    HomepageHelper(driver).sign_in_and_find_quest(ACTIVITY_QUEST_ID)
    setting = NotificationSettingHelper(driver)
    setting.grant_browser_permission()
    setting.choose_setting(2)
    assert get_notification_setting(TEST_USER_EMAIL, ORG_ID, ACTIVITY_QUEST_ID) == 2, f"All activity should be saved to the quest ({setting.error_text()})"

    assert user_notified(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "announcement"), "An announcement should notify an All activity user"
    assert user_notified(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "post"), "A feed post should notify an All activity user"
    assert setting.push_arrives(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "announcement", True), "The announcement's push should show in the browser"
    assert setting.push_arrives(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "post", True), "The post's push should show in the browser"
