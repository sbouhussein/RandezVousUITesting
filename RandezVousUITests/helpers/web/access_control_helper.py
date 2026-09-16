from selenium.webdriver.common.by import By
from helpers.web.base_helper import BaseHelper


class AccessControlHelper(BaseHelper):
    """Access-denied UI shared by QuestOnboarding, TeamView, and FeedPage: RestrictedBanner, the
    wrong-domain locked screen, and their "Switch accounts" / "Sign in with Google" remediation buttons."""

    restricted_banner_title = (By.XPATH, "//p[normalize-space()=\"You're restricted from this quest\"]")
    back_to_quest_link = (By.XPATH, "//a[contains(normalize-space(), 'Back to Quest')]")
    switch_accounts_button = (By.XPATH, "//button[normalize-space()='Switch accounts']")
    sign_in_with_google_button = (By.XPATH, "//button[contains(normalize-space(), 'Sign in with Google')]")

    # TeamView's isRestrictedTeaser screen (wrong-domain, no ban)
    restricted_quest_heading = (By.XPATH, "//h2[normalize-space()='Restricted Quest']")
    domain_requirement_text = (
        By.XPATH, "//*[contains(normalize-space(), 'Requires a') and contains(., 'Google account')]"
    )

    def is_restricted_banner_visible(self, custom_timeout=None):
        """The banned-user RestrictedBanner, regardless of which page rendered it."""
        return self.is_visible(self.restricted_banner_title, custom_timeout)

    def is_restricted_quest_screen_visible(self, custom_timeout=None):
        """TeamView's locked-quest screen for a signed-in, wrong-domain (not banned) user."""
        return self.is_visible(self.restricted_quest_heading, custom_timeout)

    def click_back_to_quest(self):
        self.click(self.back_to_quest_link)

    def click_switch_accounts(self):
        self.click(self.switch_accounts_button)
