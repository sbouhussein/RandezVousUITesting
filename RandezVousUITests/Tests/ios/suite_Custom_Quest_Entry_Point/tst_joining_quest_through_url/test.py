import pytest

from helpers.ios import GuestJoinHelper
from helpers.ios.device_helper import RV_BUNDLE_ID
from helpers.ios.ios_test_data import GUEST_USERNAME

QUEST_URL = "https://www.randezvous.com/quest/organization/test-org/test-automation-quest/onboarding"


@pytest.mark.cleanup(type="username", value=GUEST_USERNAME)
def test_joining_quest_through_url(rv_driver):
    rv_driver.get(QUEST_URL)
    rv_driver.execute_script("mobile: deepLink", {"url": QUEST_URL, "bundleId": RV_BUNDLE_ID})
    GuestJoinHelper(rv_driver).finish_onboarding()
