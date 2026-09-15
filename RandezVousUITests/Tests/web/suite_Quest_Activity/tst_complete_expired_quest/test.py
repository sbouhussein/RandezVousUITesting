import time

import requests

import pytest
from firebase_admin import auth as fb_auth, firestore
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper

ORG_ID = "test-3hmYPwC0cFa6zch5syk7"
QUEST_ID = "ExpiredTestQuest"
EXPIRED_END_TIME = "2026-09-06T14:05:00Z"
FUTURE_END_TIME = "2031-02-28T21:14:00Z"

TIMING_URL = f"http://localhost:3000/api/local-admin/quest/{ORG_ID}/{QUEST_ID}/timing"
PROFILE_URL = "http://localhost:3000/api/user/profile"


def _set_quest_end_time(end_time):
    """Flips endTime via the dev-only local-admin route, which also
    invalidates the quest-data cache (no 10min TTL.QUEST wait needed)."""
    requests.post(TIMING_URL, json={"endTime": end_time}, timeout=10).raise_for_status()


def _wait_until_joined(driver, quest_id, timeout=15):
    """Polls the profile for questHist[quest_id] -- the activity list can
    render before useAutoJoinQuest's join call actually lands."""
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
    deadline = time.time() + timeout
    while time.time() < deadline:
        profile = requests.get(PROFILE_URL, cookies=cookies, timeout=10).json()
        if profile and profile.get("questHist", {}).get(quest_id):
            return
        time.sleep(0.5)
    raise TimeoutError(f"questHist['{quest_id}'] never appeared -- join didn't land.")


def _clear_stale_grant(email, quest_id):
    """Deletes any leftover questGrants doc: join() is idempotent, so a
    grant left from an earlier run would skip rewriting questHist."""
    uid = fb_auth.get_user_by_email(email).uid
    firestore.client().collection("Users").document(uid).collection("questGrants").document(quest_id).delete()


@pytest.mark.cleanup(type="email", value="oalson123@gmail.com")
def test_complete_expired_quest(desktop_safari_driver):
    """Expiration blocks new participation, not a returning user finishing
    what they already joined (see QuestDetail.jsx's isQuestActive and
    activities.js's checkQuestActive(..., { allowEnded: true })). Leaves
    ExpiredTestQuest expired afterward either way."""
    email = "oalson123@gmail.com"
    password = "OmarTest123"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    _clear_stale_grant(email, QUEST_ID)
    _set_quest_end_time(FUTURE_END_TIME)
    try:
        print("--- Phase 1: active -- join only ---")
        desktop_safari_driver.get("http://localhost:5173")
        nav.login(email, password)
        nav.find_quest(QUEST_ID)
        WebDriverWait(desktop_safari_driver, 30).until(
            EC.visibility_of_element_located(quest.honor_activity_locator)
        )
        _wait_until_joined(desktop_safari_driver, QUEST_ID)

        print("--- Phase 2: ended -- re-enter and finish both activities ---")
        _set_quest_end_time(EXPIRED_END_TIME)
        desktop_safari_driver.get("http://localhost:5173")
        nav.find_quest(QUEST_ID)
        WebDriverWait(desktop_safari_driver, 30).until(
            EC.visibility_of_element_located(quest.honor_activity_locator)
        )
        quest.complete_honor_activity()
        quest.complete_prompt_activity("yes")

        # These are the quest's only 2 activities, so finishing both also
        # auto-completes the quest (celebration screen covers the page).
        assert quest.verify_quest_completion() is True
    finally:
        _set_quest_end_time(EXPIRED_END_TIME)
