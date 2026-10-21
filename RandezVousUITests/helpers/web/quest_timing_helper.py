"""Dev-only backend routes for the expired-quest test: flipping a quest's end time and waiting for a join to land."""
import time

import requests

from helpers.web.quest_test_data import BACKEND_URL, EXPIRED_QUEST_ID, ORG_ID

EXPIRED_END_TIME = "2026-09-06T14:05:00Z"
FUTURE_END_TIME = "2031-02-28T21:14:00Z"
TIMING_URL = f"{BACKEND_URL}/api/local-admin/quest/{ORG_ID}/{EXPIRED_QUEST_ID}/timing"
PROFILE_URL = f"{BACKEND_URL}/api/user/profile"


def set_end_time(end_time):
    """Sets the quest's endTime via the dev-only route, which also invalidates the quest cache."""
    requests.post(TIMING_URL, json={"endTime": end_time}, timeout=10).raise_for_status()


def timing_route_exists():
    """False if rvsite has no dev-only timing route (it returns 404), so the test can't flip the end time."""
    return requests.post(TIMING_URL, json={"endTime": EXPIRED_END_TIME}, timeout=10).status_code != 404


def wait_until_joined(driver, quest_id=EXPIRED_QUEST_ID, timeout=15):
    """Polls the profile for questHist[quest_id]; the activity list can render before the join lands."""
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
    deadline = time.time() + timeout
    while time.time() < deadline:
        profile = requests.get(PROFILE_URL, cookies=cookies, timeout=10).json()
        if profile and profile.get("questHist", {}).get(quest_id):
            return
        time.sleep(0.5)
    raise TimeoutError(f"questHist['{quest_id}'] never appeared; the join didn't land.")
