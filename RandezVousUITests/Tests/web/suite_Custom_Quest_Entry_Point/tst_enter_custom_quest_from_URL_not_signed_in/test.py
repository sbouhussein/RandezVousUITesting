import pytest

from helpers.web import HomepageHelper, QuestHelper
from helpers.web.quest_test_data import ACTIVITY_QUEST_ID, BASE_URL, TEST_USER_EMAIL, onboarding_url


@pytest.mark.cleanup(type="email", value=TEST_USER_EMAIL)
def test_enter_custom_quest_from_url_not_signed_in(desktop_safari_driver):
    desktop_safari_driver.get(BASE_URL)
    desktop_safari_driver.get(onboarding_url(ACTIVITY_QUEST_ID))
    HomepageHelper(desktop_safari_driver).click_guest_button()
    quest = QuestHelper(desktop_safari_driver)
    quest.open_trivia_complete_form()

    assert quest.is_sign_in_required_modal_visible(), "A guest trying to complete an activity should be prompted to sign in"
