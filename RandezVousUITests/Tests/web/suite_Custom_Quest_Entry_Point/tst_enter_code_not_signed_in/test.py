from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import OPEN_QUEST_ID


def test_enter_code_not_signed_in(desktop_safari_driver):
    """A signed-out visitor who enters a normal quest's code is asked to sign in and sees no quest content."""
    HomepageHelper(desktop_safari_driver).click_find_quest()
    quest = QuestHelper(desktop_safari_driver)
    quest.enter_quest_code(OPEN_QUEST_ID)
    quest.click_find_quest()

    assert quest.is_find_quest_sign_in_prompt_visible(), "Expected a Sign In prompt for a signed-out visitor"
    assert not quest.is_visible(quest.honor_activity_locator, custom_timeout=2), "No quest content before sign-in"
