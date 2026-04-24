import os
import time
from appium import webdriver
from appium.options.ios import XCUITestOptions
from helpers.login_page_helper import LoginPageHelper, WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper
from helpers.custom_quest_helper import QuestHelper, CustomQuestPage
import subprocess

# --- Configuration ---
LOG_FILE = "../../../appium_server.log"
APPIUM_PORT = "4723"
APPIUM_SERVER_URL = f"http://127.0.0.1:{APPIUM_PORT}"

def start_appium_server():
    """Starts the Appium server and redirects output to a file."""
    print(f"Starting Appium Server on port {APPIUM_PORT}...")

    process = subprocess.Popen(
        ["appium", "--port", APPIUM_PORT, "--log-level", "info"],
        preexec_fn=os.setsid  # Ensures child processes die with the parent on macOS
    )

    # Wait for the server to be ready
    time.sleep(5)
    print(f"Server started. Logs are being sent to {LOG_FILE}")
    return process

def get_driver():
    """Configures XCUITestOptions and initializes the driver."""
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.device_name = "iPhone 17 Pro"  # Matches your simulator
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
        quest_helper = QuestHelper(driver)
        login_page = LoginPageHelper(driver)
        quest_page = CustomQuestPage(driver)
        welcome_to_quest = WelcomeToQuestHelper(driver)
        choose_username_helper = ChooseUsernameHelper(driver)
        start_adventure_helper = StartAdventureHelper(driver)

        if login_page.verify_login_page_is_displayed():
            print("Clicking 'Login with Code")
            login_page.click_login_with_code()
        else:
            print("Login page not detected; checking if already inside app.")

        print("Entering Quest Code")
        quest_page.enter_quest_code("testautomationQuest")

        print("Finding and Starting Quest")
        quest_page.click_find_quest()
        welcome_to_quest.click_lets_go()
        choose_username_helper.enter_username("AutomatedTester")
        choose_username_helper.click_join_quest()
        start_adventure_helper.click_start_adventure()

        print("Exit Quest")
        quest_helper.click_exit_quest()

        print("Test Passed")

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