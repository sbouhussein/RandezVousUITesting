import re
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.ios.ios_test_data import TEST_USERNAME


class LeaderboardHelper:
    """Custom-quest leaderboard (CustomLeaderboardView); each row is one element labeled like "Rank 2, OmarTesting, 25 points", so assert on username and points, not rank."""

    open_button = (AppiumBy.IOS_PREDICATE, "label == 'Leaderboard'")
    nav_bar = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeNavigationBar[`name == "Leaderboard"`]')
    back_button = (AppiumBy.ACCESSIBILITY_ID, "BackButton")
    find_me_button = (AppiumBy.ACCESSIBILITY_ID, "Find Me")
    empty_state_text = (AppiumBy.IOS_PREDICATE, "label BEGINSWITH 'Users who have attempted quests from'")
    row = (AppiumBy.IOS_PREDICATE, 'label MATCHES "^(Rank [0-9]+|Unranked), .*, [0-9]+ points$"')

    _ROW_LABEL = re.compile(r"^(?:Rank (\d+)|Unranked), (.+?)(?:, team of (\d+))?, (\d+) points$")

    # Scoring (functions/scoring.js): 100 per activity unless pointValues overrides it, plus a completion bonus.
    STARTING_POINTS = 25
    POINTS_PER_ACTIVITY = 100
    COMPLETION_BONUS = 250

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    @classmethod
    def expected_score(cls, activities_completed=0, quest_completed=False):
        """The score a user should have after joining and completing `activities_completed` activities."""
        score = cls.STARTING_POINTS + activities_completed * cls.POINTS_PER_ACTIVITY
        return score + cls.COMPLETION_BONUS if quest_completed else score

    def get_score(self, username, expected_points=None, timeout=20):
        """Opens the leaderboard and returns `username`'s points, or None; pass `expected_points` to wait for scoring."""
        self.open()
        row = self.get_row(username, points=expected_points, timeout=timeout)
        return row["points"] if row else None

    def score_check(self, username=TEST_USERNAME, **scoring):
        """(expected, actual) points for `username`, where `scoring` is passed to expected_score."""
        expected = self.expected_score(**scoring)
        return expected, self.get_score(username, expected_points=expected)

    def scores_for(self, username, **scoring):
        """(expected, every row's points for `username`), for guests whose name repeats across leftover rows."""
        expected = self.expected_score(**scoring)
        self.open()
        self.get_row(username, points=expected)
        return expected, [r["points"] for r in self.get_rows_for(username)]

    def open(self):
        self.wait.until(EC.element_to_be_clickable(self.open_button)).click()
        self.wait.until(EC.visibility_of_element_located(self.nav_bar))

    def close(self):
        self.wait.until(EC.element_to_be_clickable(self.back_button)).click()

    def is_displayed(self):
        try:
            return self.wait.until(EC.visibility_of_element_located(self.nav_bar)).is_displayed()
        except Exception:
            return False

    def is_empty_state_displayed(self):
        try:
            return self.driver.find_element(*self.empty_state_text).is_displayed()
        except NoSuchElementException:
            return False

    def tap_find_me(self):
        """Scrolls to my own row; the button only exists when my row isn't pinned to the bottom."""
        self.wait.until(EC.element_to_be_clickable(self.find_me_button)).click()

    def is_find_me_displayed(self):
        try:
            return self.driver.find_element(*self.find_me_button).is_displayed()
        except NoSuchElementException:
            return False

    @classmethod
    def parse_row_label(cls, label):
        """-> {"rank": int|None, "username": str, "team_size": int|None, "points": int}, or None."""
        match = cls._ROW_LABEL.match(label or "")
        if not match:
            return None
        rank, username, team_size, points = match.groups()
        return {
            "rank": int(rank) if rank else None,
            "username": username,
            "team_size": int(team_size) if team_size else None,
            "points": int(points),
        }

    def get_visible_rows(self):
        """Parsed rows currently rendered; the list is lazy, so off-screen rows are missing."""
        rows = []
        for element in self.driver.find_elements(*self.row):
            parsed = self.parse_row_label(element.get_attribute("label"))
            if parsed:
                rows.append(parsed)
        return rows

    def get_rows_for(self, username):
        return [r for r in self.get_visible_rows() if r["username"] == username]

    def get_row(self, username, points=None, timeout=20):
        """First row for `username`, polling until it appears (and shows `points` if given); use get_rows_for for duplicate usernames."""
        deadline = time.monotonic() + timeout
        tapped_find_me = False
        last_seen = None
        while True:
            matches = self.get_rows_for(username)
            if matches:
                last_seen = matches[0]
                if points is None or last_seen["points"] == points:
                    return last_seen
            if time.monotonic() > deadline:
                return last_seen
            if not tapped_find_me and self.is_find_me_displayed():
                self.tap_find_me()
                tapped_find_me = True
            time.sleep(1)
