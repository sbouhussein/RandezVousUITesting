import pytest

from helpers.common.access_data_helper import get_notification_setting
from helpers.common.notification_data_helper import user_notified
from helpers.web import HomepageHelper, NotificationSettingHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL, ORG_ID, TEST_USER_EMAIL


def open_settings(driver):
    driver.get(BASE_URL)
    HomepageHelper(driver).sign_in_and_find_quest(ACTIVITY_QUEST_ID)
    setting = NotificationSettingHelper(driver)
    setting.grant_browser_permission()
    return setting


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_no_notifications_setting(desktop_safari_driver):
    """With None, the user is selected for neither an announcement nor a feed post."""
    setting = open_settings(desktop_safari_driver)
    setting.choose_setting(1)  # start from a subscription so None is a real change
    setting.choose_setting(0)
    assert get_notification_setting(TEST_USER_EMAIL, ORG_ID, ACTIVITY_QUEST_ID) == 0, f"None should be saved to the quest ({setting.error_text()})"

    assert not user_notified(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "announcement"), "An announcement should not notify a None user"
    assert not user_notified(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "post"), "A feed post should not notify a None user"
    assert not setting.push_arrives(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "announcement", False), "No push should show for an announcement"
    assert not setting.push_arrives(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "post", False), "No push should show for a post"
