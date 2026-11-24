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
EXPECTED = {0: (False, False), 1: (True, False), 2: (True, True)}  # setting -> (announcement, post)


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_switching_notification_settings(desktop_safari_driver):
    """Switching the setting changes what the user is notified of straight away, checked against both kinds of item each time."""
    setting = open_settings(desktop_safari_driver)
    for value in (1, 2, 0, 1):
        setting.choose_setting(value)
        assert get_notification_setting(TEST_USER_EMAIL, ORG_ID, ACTIVITY_QUEST_ID) == value, f"Setting {value} should be saved to the quest ({setting.error_text()})"
        announcement = user_notified(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "announcement")
        post = user_notified(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "post")
        assert (announcement, post) == EXPECTED[value], f"Setting {value}: expected (announcement, post) {EXPECTED[value]}, got {(announcement, post)}"
        arrived = (setting.push_arrives(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "announcement", EXPECTED[value][0]),
                   setting.push_arrives(ORG_ID, ACTIVITY_QUEST_ID, TEST_USER_EMAIL, "post", EXPECTED[value][1]))
        assert arrived == EXPECTED[value], f"Setting {value}: expected pushes shown (announcement, post) {EXPECTED[value]}, got {arrived}"
