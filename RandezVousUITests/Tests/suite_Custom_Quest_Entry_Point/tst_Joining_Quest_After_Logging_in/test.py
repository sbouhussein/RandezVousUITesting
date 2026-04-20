import subprocess
import time
import os
from appium import webdriver
from appium.options.ios import XCUITestOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from logger_helper import setup_logger

current_dir = os.path.dirname(os.path.abspath(__file__))
logger, execution_log_path = setup_logger(current_dir)
APPIUM_LOG_FILE = os.path.join(current_dir, "appium_server.log")
APPIUM_PORT = "4723"

def start_appium_server():
    """Starts Appium and sends the 'wall of text' to appium_server.log"""
    logger.info("Initializing Appium Server...")

    log_fd = open(APPIUM_LOG_FILE, "w")
    process = subprocess.Popen(
        ["appium", "--port", APPIUM_PORT, "--log-level", "info"],
        stdout=log_fd,
        stderr=log_fd,
        preexec_fn=os.setsid
    )

    time.sleep(5)
    logger.info(f"✅ Appium Server active. Raw logs: {APPIUM_LOG_FILE}")
    return process


def run_caps():
    """Starts the session and logs the progress"""
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.automation_name = "XCUITest"
    options.device_name = "iPhone 17 Pro"
    options.platform_version = "26.2"
    options.udid = "02702BB3-0AE0-4167-9651-39F68787A375"
    options.bundle_id = "sbouhussein.github.io-rvsite.RandezVous"
    options.set_capability("appium:showXcodeLog", False)
    options.set_capability("appium:useNewWDA", False)

    logger.info("📱 Launching RandezVous application...")
    return webdriver.Remote(f"http://127.0.0.1:{APPIUM_PORT}", options=options)


# --- EXECUTION ---
server_process = None

try:
    server_process = start_appium_server()
    driver = run_caps()
    wait = WebDriverWait(driver, 15)

    logger.info("🚀 Starting: Join Custom Quest Flow")

    # Step 1: Quests Tab
    quests_tab = wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "scroll.fill")))
    quests_tab.click()
    logger.info("Step 1: Quests Tab clicked.")

    # Step 2: Custom Overlay
    custom_quest_btn = wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Custom")))
    custom_quest_btn.click()
    logger.info("Step 2: Custom Quest overlay opened.")

    # Step 3: Input Code
    input_field = driver.find_element(AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeTextField[`value == "Custom Code"`]')
    input_field.send_keys("testautomationQuest")
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Find Quest").click()
    logger.info("Step 3: Quest code entered and searched.")

    # Step 4: The "Start Quest" Interaction
    logger.info("Step 4: Locating 'Start Quest' button...")
    start_btn = wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Start Quest")))

    driver.execute_script('mobile: tap', {'element': start_btn.id, 'x': 10, 'y': 10})
    logger.info("✅ Native tap sent to Start Quest button.")

    logger.info("🏁 TEST COMPLETE: All steps passed.")

except Exception as e:
    logger.error(f"❌ TEST FAILED: {str(e)}")

finally:
    if server_process:
        logger.info("Shutting down Appium server...")
        os.killpg(os.getpgid(server_process.pid), 9)