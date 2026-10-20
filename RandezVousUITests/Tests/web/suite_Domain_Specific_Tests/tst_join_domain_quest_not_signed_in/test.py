from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import RESTRICTED_QUEST_ID


def test_join_domain_quest_not_signed_in(desktop_safari_driver):
    """A signed-out visitor gets a Sign In modal on /find-quest and sees no quest content."""
    HomepageHelper(desktop_safari_driver).click_find_quest()
    quest = QuestHelper(desktop_safari_driver)
    quest.enter_quest_code(RESTRICTED_QUEST_ID)
    quest.click_find_quest()

    assert quest.is_find_quest_sign_in_prompt_visible(), "Expected a Sign In prompt for a signed-out visitor"
    assert "/find-quest" in desktop_safari_driver.current_url, "A signed-out visitor must not be taken to the quest"
    assert not quest.is_visible(quest.honor_activity_locator, custom_timeout=2), \
        "The restricted quest's activities must not be visible to a signed-out visitor"
