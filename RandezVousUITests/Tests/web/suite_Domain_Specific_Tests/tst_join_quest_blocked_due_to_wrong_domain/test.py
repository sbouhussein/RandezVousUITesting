import time

import pytest

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import BASE_URL, RESTRICTED_QUEST_ID, WRONG_DOMAIN_EMAIL, WRONG_DOMAIN_PASSWORD


@pytest.mark.cleanup(type="email", value=WRONG_DOMAIN_EMAIL)
def test_join_quest_blocked_wrong_domain(desktop_safari_driver):
    desktop_safari_driver.get(BASE_URL)
    nav, quest = HomepageHelper(desktop_safari_driver), QuestHelper(desktop_safari_driver)
    time.sleep(2)
    nav.login(WRONG_DOMAIN_EMAIL, WRONG_DOMAIN_PASSWORD)
    nav.click_find_quest()
    quest.enter_quest_code(RESTRICTED_QUEST_ID)
    quest.click_find_quest()

    message = quest.get_restriction_message()
    print(f"Restriction message: '{message}'")
    assert message, "Expected domain restriction message when entering with unauthorized account."
