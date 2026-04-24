import subprocess
import time
import os
from appium import webdriver
from appium.options.ios import XCUITestOptions
from selenium.webdriver.support.ui import WebDriverWait
from helpers.login_page_helper import WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper
from helpers.custom_quest_helper import QuestHelper
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

# --- Configuration ---
LOG_FILE = "../../../appium_server.log"
APPIUM_PORT = "4723"
SAFARI_BUNDLE_ID = "com.apple.mobilesafari"
QUEST_URL = "https://www.randezvous.com/quest/organization/test-3hmYPwC0cFa6zch5syk7/testautomationQuest/onboarding"


def start_appium_server():
    print(f"Starting Appium Server on port {APPIUM_PORT}...")
    process = subprocess.Popen(
        ["appium", "--port", APPIUM_PORT, "--log-level", "info"],
        preexec_fn=os.setsid
    )
    time.sleep(5)
    return process


def run_safari_caps():
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.automation_name = "XCUITest"
    options.device_name = "iPhone 17 Pro"
    options.platform_version = "26.2"
    options.udid = "02702BB3-0AE0-4167-9651-39F68787A375"
    # Start with Safari
    options.bundle_id = SAFARI_BUNDLE_ID

    options.set_capability("appium:showXcodeLog", False)

    print("Launching Safari...")
    driver = webdriver.Remote(f"http://127.0.0.1:{APPIUM_PORT}", options=options)
    return driver


# --- MAIN EXECUTION ---
server_process = None

try:
    server_process = start_appium_server()
    driver = run_safari_caps()
    wait = WebDriverWait(driver, 20)
    welcome = WelcomeToQuestHelper(driver)
    username_screen = ChooseUsernameHelper(driver)
    adventure = StartAdventureHelper(driver)
    quest_helper = QuestHelper(driver)

    # 1. Navigate to the URL
    print(f"Navigating to: {QUEST_URL}")
    driver.get(QUEST_URL)

    # 2. Click the 'OPEN' button in the Smart App Banner
    # Based on your XML: name="AppLinkBannerOpenButton" or label="OPEN"
    print("Handling Welcome Modal...")
    if welcome.verify_welcome_modal_is_displayed():
        welcome.click_lets_go()
    print("Entering Username: 'AutomationTester'...")
    username_screen.enter_username("AutomationTester2")

    if username_screen.is_join_button_enabled():
        username_screen.click_join_quest()

    print("Starting Adventure...")
    if adventure.verify_start_adventure_page_is_displayed():
        adventure.click_start_adventure()

    print("Exiting Quest via QuestHelper...")
    quest_helper.click_exit_quest()

    print("Test Passed")

except Exception as e:
    print(f"TECHNICAL ERROR: {e}")

finally:
    if 'driver' in locals():
        driver.quit()
    if server_process:
        os.killpg(os.getpgid(server_process.pid), 9)