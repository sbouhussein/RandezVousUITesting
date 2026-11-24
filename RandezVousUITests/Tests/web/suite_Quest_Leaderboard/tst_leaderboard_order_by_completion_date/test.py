import pytest

from helpers.common.access_data_helper import user_uid
from helpers.ios.firebase_cleanup_helper import cleanup_user_data
from helpers.web import HomepageHelper, LeaderboardPageHelper, OnboardingPageHelper, QuestHelper
from helpers.web.quest_test_data import OPEN_QUEST_ID, TEST_USER_EMAIL, TEST_USER_PASSWORD, onboarding_url, quest_url

TEST_USERNAME = "OmarTesting"


def finish_quest(driver, accounts, email):
    password, _ = accounts[email]
    HomepageHelper(driver).sign_in_and_open(onboarding_url(OPEN_QUEST_ID), email, password)
    OnboardingPageHelper(driver).click_start_quest()
    quest = QuestHelper(driver)
    assert quest.is_visible(quest.honor_activity_locator, custom_timeout=30), f"{email} should land on the quest after joining"
    driver.get(quest_url(OPEN_QUEST_ID))
    quest.complete_honor_activity()
    assert quest.verify_quest_completion(), f"{email} finishing the only activity should finish the quest"


# rvsite sorts the leaderboard by quest score only, so equal scores come back in descending uid order (Firestore's tie-break), not completion order (iOS breaks ties by date).
@pytest.mark.xfail(strict=True, reason="Application gap: rvsite's leaderboard has no completion-time tie-break")
def test_leaderboard_order_by_completion_date(desktop_safari_driver, second_user):
    """Two users finish the same quest with equal scores; the one who finished first is listed first."""
    second_email, second_password, second_username = second_user
    accounts = {TEST_USER_EMAIL: (TEST_USER_PASSWORD, TEST_USERNAME), second_email: (second_password, second_username)}
    cleanup_user_data(target_email=TEST_USER_EMAIL)
    first, second = sorted(accounts, key=user_uid)  # the smaller uid finishes first, so the descending-uid tie order can't pass by luck
    driver = desktop_safari_driver
    finish_quest(driver, accounts, first)
    HomepageHelper(driver).sign_out()
    finish_quest(driver, accounts, second)

    LeaderboardPageHelper(driver).open(OPEN_QUEST_ID)
    names = [row["username"] for row in LeaderboardPageHelper(driver).get_rows()]
    first_name, second_name = accounts[first][1], accounts[second][1]
    assert names.index(first_name) < names.index(second_name), f"The earlier finisher ({first_name}) should be listed first, got {names}"
