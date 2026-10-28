import pytest

from helpers.ios import CustomQuestPage, GuestJoinHelper, LoginPageHelper, QuestHelper
from helpers.ios.device_helper import RV_BUNDLE_ID
from helpers.ios.firebase_cleanup_helper import cleanup_user_data
from helpers.ios.ios_test_data import GUEST_USERNAME, TEST_EMAIL, TEST_PASSWORD

QUEST_URL = "https://www.randezvous.com/quest/organization/test-org/test-automation-quest/onboarding"


def open_link(driver):
    driver.get(QUEST_URL)
    driver.execute_script("mobile: deepLink", {"url": QUEST_URL, "bundleId": RV_BUNDLE_ID})


@pytest.mark.cleanup(type="username", value=GUEST_USERNAME)
def test_joining_quest_through_url(rv_driver):
    """The quest link joins a guest (after picking a username), then a signed-in user straight into the quest."""
    guest, quest, app = GuestJoinHelper(rv_driver), CustomQuestPage(rv_driver), QuestHelper(rv_driver)
    app.sign_out_if_signed_in()  # a login left in the keychain would skip the guest username step
    open_link(rv_driver)
    guest.finish_onboarding()
    quest.click_exit_quest()

    cleanup_user_data(target_email=TEST_EMAIL)
    app.sign_out_if_signed_in()
    LoginPageHelper(rv_driver).login_with_credentials(TEST_EMAIL, TEST_PASSWORD)
    open_link(rv_driver)
    guest.continue_past_welcome()
    guest.start_adventure()

    assert quest.is_visible(quest.primary_exit_quest_button, custom_timeout=20), "A signed-in user should land in the quest"
    assert not guest.choose_username.verify_choose_username_page_is_displayed(), "A signed-in user needs no new username"
