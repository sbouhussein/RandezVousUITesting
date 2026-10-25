import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import BASE_URL, EXPIRED_QUEST_ID, TEST_USER_EMAIL
from helpers.web.quest_timing_helper import (
    EXPIRED_END_TIME, FUTURE_END_TIME, set_end_time, timing_route_exists, wait_until_joined,
)


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_expired_quest(desktop_safari_driver):
    """An expired quest blocks new joins but lets a returning user finish; leaves the quest expired."""
    driver = desktop_safari_driver
    if not timing_route_exists():
        pytest.skip("rvsite has no dev-only quest timing endpoint (POST /api/local-admin/quest/<org>/<qid>/timing); "
                    "this test can't flip the quest's end time without it.")
    nav, quest = HomepageHelper(driver), QuestHelper(driver)
    set_end_time(FUTURE_END_TIME)
    try:
        driver.get(BASE_URL)
        nav.sign_in_and_find_quest(EXPIRED_QUEST_ID)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(quest.honor_activity_locator))
        wait_until_joined(driver)

        set_end_time(EXPIRED_END_TIME)  # now ended: re-enter and finish both activities
        driver.get(BASE_URL)
        nav.find_quest(EXPIRED_QUEST_ID)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(quest.honor_activity_locator))
        quest.complete_honor_activity()
        quest.complete_prompt_activity("yes")

        assert quest.verify_quest_completion()  # those are the quest's only 2 activities
    finally:
        set_end_time(EXPIRED_END_TIME)
    # TODO: a user who finished every activity before the quest expired should still be able to complete it.
