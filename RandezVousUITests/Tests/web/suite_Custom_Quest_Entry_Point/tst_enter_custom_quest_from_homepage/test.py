from helpers.web.homepage_helper import HomepageHelper
from helpers.web.quest_helper import QuestHelper


def test_find_quest_flow(desktop_safari_driver):
    desktop_safari_driver.get("http://localhost:5173")
    quest_code = "TestAutomationActivityQuest"

    nav = HomepageHelper(desktop_safari_driver)
    quest = QuestHelper(desktop_safari_driver)

    nav.click_find_quest()
    quest.enter_quest_code(quest_code)
    quest.click_find_quest()

