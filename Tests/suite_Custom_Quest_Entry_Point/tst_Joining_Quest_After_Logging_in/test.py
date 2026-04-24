import subprocess
import time
import os
from appium import webdriver
from appium.options.ios import XCUITestOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from helpers.custom_quest_helper import CustomQuestPage, QuestHelper
from helpers.quest_page_helper import QuestsPage

# --- Configuration ---
LOG_FILE = "../../../appium_server.log"
APPIUM_PORT = "4723"


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

def run_caps():
    """Defines capabilities and starts the RandezVous session."""
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.automation_name = "XCUITest"
    options.device_name = "iPhone 17 Pro"
    options.platform_version = "26.2"
    options.udid = "02702BB3-0AE0-4167-9651-39F68787A375"
    options.bundle_id = "sbouhussein.github.io-rvsite.RandezVous"

    # Clean terminal settings
    options.set_capability("appium:showXcodeLog", False)
    options.set_capability("appium:useNewWDA", False)

    print("Launching RandezVous app...")
    driver = webdriver.Remote(f"http://127.0.0.1:{APPIUM_PORT}", options=options)
    return driver


# --- MAIN EXECUTION ---
server_process = None

try:
    server_process = start_appium_server()
    driver = run_caps()
    wait = WebDriverWait(driver, 15)
    custom_quest = CustomQuestPage(driver)
    quest_helper = QuestHelper(driver)

    print("Navigate to Quests Dashboard")
    quest_helper.navigate_to_quests_tab()

    print("Click Custom Quest Button")
    quest_helper.click_custom_quest_button()

    custom_quest.enter_quest_code("testautomationQuest")
    custom_quest.click_find_quest()

    custom_quest.click_start_quest()
    quest_helper.click_exit_quest()

    print("\nTest Passed")

except AssertionError as msg:
    print(msg)
except Exception as e:
    print(f"TECHNICAL ERROR: {e}")