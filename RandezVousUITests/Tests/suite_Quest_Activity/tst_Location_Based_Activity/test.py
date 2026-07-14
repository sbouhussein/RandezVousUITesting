import pytest

from helpers.custom_quest_helper import CustomQuestPage
from helpers.login_page_helper import LoginPageHelper
from helpers.profile_helper import ProfileHelper

@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_location_based_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "TestAutomationActivityQuest"
    activity = "Location Activity"

    set_simulator_location_via_driver(rv_driver)
    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    profile_helper = ProfileHelper(rv_driver)

    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)
    custom_quest.complete_location_activity(activity)

    custom_quest.click_exit_quest()
    profile_helper.log_out_if_logged_in()

def set_simulator_location_via_driver(rv_driver, lat=41.282778, lon=-157.829444):
    print("Forcing location via Appium Driver...")
    try:
        udid = rv_driver.capabilities.get('udid')
        print(f"Targeting active simulator UDID: {udid}")

        rv_driver.set_location(lat, lon, 0)

        if udid:
            import subprocess
            subprocess.run(["xcrun", "simctl", "location", udid, "clear"])
            subprocess.run(["xcrun", "simctl", "location", udid, "set", f"{lat},{lon}"])
            print("Location successfully hard-set via simctl.")

    except Exception as e:
        print(f"Failed to set location: {e}")

