import subprocess
import time

import pytest

from helpers.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.login_page_helper import LoginPageHelper
from helpers.profile_helper import ProfileHelper


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_location_based_activity(rv_driver):
    email = "oalson123@gmail.com"
    password = "OmarTest123"
    quest = "TestAutomationActivityQuest"
    activity = "Location Activity"
    score = "125"

    set_simulator_location_via_driver(rv_driver)
    custom_quest = CustomQuestPage(rv_driver)
    login_helper = LoginPageHelper(rv_driver)
    profile_helper = ProfileHelper(rv_driver)

    login_helper.login_with_credentials(email, password)
    custom_quest.join_custom_quest(quest)
    custom_quest.complete_location_activity(activity)

    custom_quest.click_exit_quest()
    profile_helper.log_out_if_logged_in(True, score)

def set_simulator_location_via_driver(rv_driver, lat=40.741895, lon=-73.989308):
    print("Forcing location via Appium Driver...")
    try:
        udid = rv_driver.capabilities['02702BB3-0AE0-4167-9651-39F68787A375']
        print(f"Targeting active simulator UDID: {udid}")

        rv_driver.execute_script('mobile: setLocation', {
            'latitude': lat,
            'longitude': lon
        })

        import subprocess
        subprocess.run(["xcrun", "simctl", "location", udid, "clear"])
        subprocess.run(["xcrun", "simctl", "location", udid, "set", f"{lat},{lon}"])

        print("Location command sent and cleared.")
    except Exception as e:
        print(f"Failed to set location: {e}")