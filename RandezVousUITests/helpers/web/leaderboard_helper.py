import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from helpers.web.base_helper import BaseHelper
from helpers.web.quest_test_data import leaderboard_url

_POINTS = re.compile(r"(\d+) pts")


class LeaderboardPageHelper(BaseHelper):
    """rvsite's /leaderboard/<org>/<quest> page: one list item per participant, in ranked order."""

    rows = (By.XPATH, "//ol[@aria-label='Leaderboard rankings']/li")
    row_username = (By.XPATH, ".//span[contains(@class, 'truncate')]")

    def open(self, qid):
        self.driver.get(leaderboard_url(qid))
        self.wait.until(EC.presence_of_element_located(self.rows))

    def get_rows(self):
        """[{"username", "points", "completed"}] in the page's order. rvsite sorts by the quest score only; it does
        not break ties by completion time the way the iOS app does."""
        rows = []
        for item in self.driver.find_elements(*self.rows):
            points = _POINTS.search(item.text)
            rows.append({
                "username": item.find_element(*self.row_username).text,
                "points": int(points.group(1)) if points else None,
                "completed": "Completed" in item.text,
            })
        return rows

    def get_row(self, qid, username, points=None, timeout=15):
        """Opens the quest's leaderboard and returns `username`'s row, waiting for `points` if given; None if it never shows."""
        deadline = time.monotonic() + timeout
        row = None
        while True:
            self.open(qid)
            row = next((r for r in self.get_rows() if r["username"] == username), None)
            if row and (points is None or row["points"] == points):
                return row
            if time.monotonic() > deadline:
                return row
            time.sleep(1)
