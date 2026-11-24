import uuid
from datetime import datetime, timedelta, timezone

import pytest

from helpers.common.access_data_helper import delete_feed_posts, edited_quest, wait_for_feed_post
from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL, ORG_ID, TEST_USER_EMAIL

PROMPT_ACTIVITY_KEY = f"{ACTIVITY_QUEST_ID}-1002"
CASES = [  # (name, shared publicly, feed enabled, a feed comment is expected)
    ("public with the feed on", True, True, True),
    ("private with the feed on", False, True, False),
    ("public with the feed off", True, False, False),
]


@pytest.mark.parametrize("name,public,feed_on,expects_post", CASES, ids=[c[0] for c in CASES])
@pytest.mark.usefixtures("fresh_web_backend")
@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_prompt_feed_posting(desktop_safari_driver, name, public, feed_on, expects_post):
    """An open-prompt response reaches the quest feed only when it is shared publicly and the quest's feed is on."""
    driver = desktop_safari_driver
    text = f"ui-test-prompt-{uuid.uuid4().hex[:8]}"
    started = datetime.now(timezone.utc) - timedelta(seconds=10)  # margin for clock skew
    try:
        with edited_quest(ORG_ID, ACTIVITY_QUEST_ID, hasFeed=feed_on):  # restored even if the test fails
            driver.get(BASE_URL)
            HomepageHelper(driver).sign_in_and_find_quest(ACTIVITY_QUEST_ID)
            quest = QuestHelper(driver)
            quest.complete_prompt_activity(text, public=public)
            assert quest.verify_activity_completion("Prompt"), "The prompt activity should be recorded in every case"

            post = wait_for_feed_post(TEST_USER_EMAIL, ORG_ID, ACTIVITY_QUEST_ID, started, "comment",
                                      predicate=lambda p: p.get("message") == text, timeout=15 if expects_post else 8)
            assert (post is not None) == expects_post, f"Feed comment expected={expects_post} for a prompt {name}, got {post}"
            if expects_post:
                assert post["activityId"] == PROMPT_ACTIVITY_KEY, f"The comment is for the wrong activity: {post['activityId']}"
    finally:
        delete_feed_posts(TEST_USER_EMAIL, ORG_ID, ACTIVITY_QUEST_ID, started)
