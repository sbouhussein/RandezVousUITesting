from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ExperienceHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        # Navigation
        self.back_button = (AppiumBy.ACCESSIBILITY_ID, "BackButton")
        self.nav_header = (AppiumBy.ACCESSIBILITY_ID, "Your Experience")

        # Quests & Info
        self.exit_quest_btn = (AppiumBy.ACCESSIBILITY_ID, "Exit Custom Quest Experience")
        self.quest_hint_text = (AppiumBy.ACCESSIBILITY_ID, "You can reenter via the \"Quests\" tab up until the end date.")
        self.our_mission_btn = (AppiumBy.ACCESSIBILITY_ID, "Our Mission")
        self.adventurer_guide_btn = (AppiumBy.ACCESSIBILITY_ID, "Adventurer Guide")

        # External & Feedback
        self.visit_site_btn = (AppiumBy.ACCESSIBILITY_ID, "Visit Our Site")
        self.send_feedback_btn = (AppiumBy.ACCESSIBILITY_ID, "Send Feedback")

        # Premium Section
        self.try_premium_btn = (AppiumBy.ACCESSIBILITY_ID, "Try RandezVous Premium")
        self.why_premium_btn = (AppiumBy.ACCESSIBILITY_ID, "Why Premium?")
        self.restore_purchases_btn = (AppiumBy.ACCESSIBILITY_ID, "Restore Purchases")

        # Account Actions (Hidden/Bottom of scroll)
        self.logout_btn = (AppiumBy.ACCESSIBILITY_ID, "Log out")
        self.delete_account_btn = (AppiumBy.ACCESSIBILITY_ID, "Delete Account")

    def exit_custom_quest(self):
        self.wait.until(EC.element_to_be_clickable(self.exit_quest_btn)).click()

    def logout(self):
        self.driver.execute_script("mobile: scroll", {
            "direction": "down",
            "name": "Log out"
        })
        self.wait.until(EC.element_to_be_clickable(self.logout_btn)).click()

    def delete_account(self):
        self.driver.execute_script("mobile: scroll", {
            "direction": "down",
            "name": "Delete Account"
        })
        self.wait.until(EC.element_to_be_clickable(self.delete_account_btn)).click()

    def click_back(self):
        self.wait.until(EC.element_to_be_clickable(self.back_button)).click()