from helpers.common.access_data_helper import has_quest_grant
from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import GOOGLE_DOMAIN_EMAIL, ORG_ID, RESTRICTED_QUEST_ID


def test_banned_signed_out_visitor_must_sign_in_for_domain_quest(desktop_safari_driver, banned_user):
    """With a ban on file, a signed-out visitor is still stopped at sign-in and gets no quest content or grant."""
    banned_user(GOOGLE_DOMAIN_EMAIL, ORG_ID, RESTRICTED_QUEST_ID)
    HomepageHelper(desktop_safari_driver).click_find_quest()
    quest = QuestHelper(desktop_safari_driver)
    quest.enter_quest_code(RESTRICTED_QUEST_ID)
    quest.click_find_quest()

    assert quest.is_find_quest_sign_in_prompt_visible(), "Expected a Sign In prompt for a signed-out visitor"
    assert "/find-quest" in desktop_safari_driver.current_url, "A signed-out visitor must not be taken to the quest"
    assert not quest.is_visible(quest.honor_activity_locator, custom_timeout=2), \
        "The restricted quest's activities must not be visible to a signed-out visitor"
    assert not has_quest_grant(GOOGLE_DOMAIN_EMAIL, RESTRICTED_QUEST_ID), "A signed-out visit must not create a grant"
