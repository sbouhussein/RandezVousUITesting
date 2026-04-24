import os
import time
import subprocess
from appium import webdriver
from appium.options.ios import XCUITestOptions
from helpers.login_page_helper import WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper
from helpers.sign_in_overlay_helper import SignInOverlayHelper
from helpers.custom_quest_helper import QuestHelper

# --- Configuration ---
LOG_FILE = "../../../appium_server.log"
APPIUM_PORT = "4723"
APPIUM_SERVER_URL = f"http://127.0.0.1:{APPIUM_PORT}"


def start_appium_server():
    """Starts the Appium server and redirects output to a file."""
    print(f"Starting Appium Server on port {APPIUM_PORT}...")
    log_fd = open(LOG_FILE, "w")

    process = subprocess.Popen(
        ["appium", "--port", APPIUM_PORT, "--log-level", "info"],
        stdout=log_fd,
        stderr=log_fd,
        preexec_fn=os.setsid
    )

    time.sleep(5)
    print(f"Server started. Logs are being sent to {LOG_FILE}")
    return process


def get_driver():
    """Configures XCUITestOptions and initializes the driver."""
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.device_name = "iPhone 17 Pro"
    options.automation_name = "XCUITest"
    options.bundle_id = "sbouhussein.github.io-rvsite.RandezVous"
    options.udid = "02702BB3-0AE0-4167-9651-39F68787A375"
    options.no_reset = True

    print(f"Launching {options.bundle_id} on {options.device_name}...")
    return webdriver.Remote(APPIUM_SERVER_URL, options=options)


def run_test():
    driver = None
    server_process = None

    try:
        server_process = start_appium_server()
        driver = get_driver()

        # Initialize Helpers
        dashboard = SignInOverlayHelper(driver)
        welcome = WelcomeToQuestHelper(driver)
        username_screen = ChooseUsernameHelper(driver)
        adventure = StartAdventureHelper(driver)
        quest_helper = QuestHelper(driver)

        print("Navigate to Quests Dashboard...")
        quest_helper.navigate_to_quests_tab()
        print("Checking Quests Dashboard...")
        if dashboard.verify_dashboard_is_displayed():
            print(f"Entering Quest Code: 'testautomationQuest'...")
            dashboard.enter_custom_quest_code("testautomationQuest")
        else:
            raise Exception("Quests Dashboard not detected.")

        print("Handling Welcome Modal...")
        if welcome.verify_welcome_modal_is_displayed():
            welcome.click_lets_go()

        print("Entering Username: 'AutomationTester'...")
        username_screen.enter_username("AutomationTester")

        if username_screen.is_join_button_enabled():
            username_screen.click_join_quest()

        print("Starting Adventure...")
        if adventure.verify_start_adventure_page_is_displayed():
            adventure.click_start_adventure()

        print("Exiting Quest via QuestHelper...")
        quest_helper.click_exit_quest()

        print("Test Completed Successfully.")

    except Exception as e:
        print(f"TEST FAILED: {str(e)}")

    finally:
        if driver:
            print("Cleaning up Driver...")
            driver.quit()
        if server_process:
            print("Shutting down Appium Server...")
            server_process.terminate()


if __name__ == "__main__":
    run_test()