import time

import pytest
import requests
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper
from helpers.web.quest_test_data import (
    BACKEND_URL, BASE_URL, EXPIRED_QUEST_ID, ORG_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD,
)

QUEST_ID = EXPIRED_QUEST_ID
EXPIRED_END_TIME = "2026-09-06T14:05:00Z"
FUTURE_END_TIME = "2031-02-28T21:14:00Z"

TIMING_URL = f"{BACKEND_URL}/api/local-admin/quest/{ORG_ID}/{QUEST_ID}/timing"
PROFILE_URL = f"{BACKEND_URL}/api/user/profile"


def _set_quest_end_time(end_time):
    """Sets endTime via the dev-only local-admin route, which also invalidates the quest cache."""
    requests.post(TIMING_URL, json={"endTime": end_time}, timeout=10).raise_for_status()


def _wait_until_joined(driver, quest_id, timeout=15):
    """Polls the profile for questHist[quest_id]; the activity list can render before the join lands."""
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
    deadline = time.time() + timeout
    while time.time() < deadline:
        profile = requests.get(PROFILE_URL, cookies=cookies, timeout=10).json()
        if profile and profile.get("questHist", {}).get(quest_id):
            return
        time.sleep(0.5)
    raise TimeoutError(f"questHist['{quest_id}'] never appeared -- join didn't land.")


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_complete_expired_quest(desktop_safari_driver):
    """Expiration blocks new participation, not a returning user finishing what they already joined
    (QuestDetail.jsx's isQuestActive, activities.js's checkQuestActive(..., { allowEnded: true })).
    Leaves the quest expired afterward either way."""

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    # rvsite main no longer has the dev-only timing route; skip rather than fail until it's back.
    probe = requests.post(TIMING_URL, json={"endTime": EXPIRED_END_TIME}, timeout=10)
    if probe.status_code == 404:
        pytest.skip("rvsite has no dev-only quest timing endpoint (POST /api/local-admin/quest/<org>/<qid>/timing); "
                    "this test can't flip the quest's end time without it.")

    _set_quest_end_time(FUTURE_END_TIME)
    try:
        print("--- Phase 1: active -- join only ---")
        desktop_safari_driver.get(BASE_URL)
        nav.login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        nav.find_quest(QUEST_ID)
        WebDriverWait(desktop_safari_driver, 30).until(
            EC.visibility_of_element_located(quest.honor_activity_locator)
        )
        _wait_until_joined(desktop_safari_driver, QUEST_ID)

        print("--- Phase 2: ended -- re-enter and finish both activities ---")
        _set_quest_end_time(EXPIRED_END_TIME)
        desktop_safari_driver.get(BASE_URL)
        nav.find_quest(QUEST_ID)
        WebDriverWait(desktop_safari_driver, 30).until(
            EC.visibility_of_element_located(quest.honor_activity_locator)
        )
        quest.complete_honor_activity()
        quest.complete_prompt_activity("yes")

        # These are the quest's only 2 activities, so finishing both auto-completes the quest.
        assert quest.verify_quest_completion()
    finally:
        _set_quest_end_time(EXPIRED_END_TIME)

    # TODO: cover a user who finished every activity (or reached the points to win) before the quest
    # expired: seed the grant and completed activities in Firestore, then check the quest can still be
    # completed after the end date.