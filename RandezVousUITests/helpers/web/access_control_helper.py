from selenium.webdriver.common.by import By
from helpers.web.base_helper import BaseHelper


class AccessControlHelper(BaseHelper):
    """Access-denied UI shared by QuestOnboarding, TeamView and FeedPage."""

    restricted_banner_title = (By.XPATH, "//p[normalize-space()=\"You're restricted from this quest\"]")
    back_to_quest_link = (By.XPATH, "//a[contains(normalize-space(), 'Back to Quest')]")
    switch_accounts_button = (By.XPATH, "//button[normalize-space()='Switch accounts']")
    sign_in_with_google_button = (By.XPATH, "//button[contains(normalize-space(), 'Sign in with Google')]")

    # QuestOnboarding's AccessErrorPanel message for a Google account on the wrong domain
    wrong_domain_message = (
        By.XPATH, "//p[contains(normalize-space(), 'requires a @') and contains(., 'You are signed in with @')]"
    )

    ended_banner = (By.XPATH, "//span[contains(normalize-space(), 'This quest ended')]")

    # TeamView's isRestrictedTeaser screen (wrong-domain, no ban)
    restricted_quest_heading = (By.XPATH, "//h2[normalize-space()='Restricted Quest']")
    domain_requirement_text = (
        By.XPATH, "//*[contains(normalize-space(), 'Requires a') and contains(., 'Google account')]"
    )

    def is_wrong_domain_message_visible(self, custom_timeout=None):
        """The AccessErrorPanel's "requires a @<domain> account. You are signed in with @<other>" text."""
        return self.is_visible(self.wrong_domain_message, custom_timeout)

    def get_wrong_domain_message(self):
        return self.driver.find_element(*self.wrong_domain_message).text

    def is_quest_ended_banner_visible(self, custom_timeout=None):
        """QuestOnboarding's 'This quest ended on <date>' banner (ended quests are viewable, not joinable)."""
        return self.is_visible(self.ended_banner, custom_timeout)

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
