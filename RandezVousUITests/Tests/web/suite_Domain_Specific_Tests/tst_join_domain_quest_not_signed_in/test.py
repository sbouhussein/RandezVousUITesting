from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID


def test_join_domain_quest_not_signed_in(desktop_safari_driver):
    """A signed-out visitor gets a Sign In modal on /find-quest and sees no quest content."""
    driver = desktop_safari_driver
    nav = HomepageHelper(driver)
    quest = QuestHelper(driver)

    nav.click_find_quest()
    quest.enter_quest_code(RESTRICTED_QUEST_ID)
    quest.click_find_quest()

    assert quest.is_find_quest_sign_in_prompt_visible(), \
        "Expected a Sign In prompt for a signed-out visitor looking up a quest code"
    assert "/find-quest" in driver.current_url, \
        f"A signed-out visitor must not be taken to the quest, got: {driver.current_url}"
    assert not quest.is_visible(quest.honor_activity_locator, custom_timeout=2), \
        "The restricted quest's activities must not be visible to a signed-out visitor"
