from helpers.custom_quest_helper import CustomQuestPage, QuestHelper


def test_joining_quest_after_logging_in(rv_driver):
    custom_quest = CustomQuestPage(rv_driver)
    quest_helper = QuestHelper(rv_driver)

    quest_helper.navigate_to_quests_tab()
    quest_helper.click_custom_quest_button()
    custom_quest.enter_quest_code("testautomationQuest")
    custom_quest.click_find_quest()
    custom_quest.click_start_quest()
    quest_helper.click_exit_quest()
