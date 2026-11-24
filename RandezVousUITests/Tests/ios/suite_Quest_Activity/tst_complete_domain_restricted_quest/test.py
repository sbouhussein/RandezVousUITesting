from helpers.common.access_data_helper import edited_quest
from helpers.ios import CustomQuestPage, DeviceHelper, LeaderboardHelper
from helpers.ios.ios_test_data import GOOGLE_DOMAIN_USERNAME
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, ACTIVITY_QUEST_LOCATION, ORG_ID

DOMAIN_POLICY = {"type": "google_hd", "allowedDomains": ["randezvous.com"]}


def test_complete_domain_restricted_quest(rv_driver, domain_user):
    """An account on the allowed domain joins a domain-restricted quest with every activity type and completes it."""
    email, password = domain_user
    with edited_quest(ORG_ID, ACTIVITY_QUEST_ID, accessPolicy=DOMAIN_POLICY):  # restored even if the test fails
        quest = CustomQuestPage(rv_driver)
        quest.sign_in_and_join(email, password, ACTIVITY_QUEST_ID)
        DeviceHelper(rv_driver).set_simulator_location(*ACTIVITY_QUEST_LOCATION)
        quest.complete_all_activities()
        quest.dismiss_quest_completion_overlay()

        expected, actual = LeaderboardHelper(rv_driver).score_check(
            GOOGLE_DOMAIN_USERNAME, activities_completed=5, quest_completed=True)
        assert actual == expected, f"Expected {expected} points after completing the quest, got {actual}"
