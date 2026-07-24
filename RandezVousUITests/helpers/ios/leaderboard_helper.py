from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LeaderboardHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

        # --- Locators ---
        self._header_title = (By.ACCESSIBILITY_ID, "Leaderboard")
        self._back_button = (By.ACCESSIBILITY_ID, "BackButton")
        self._org_label = (By.ACCESSIBILITY_ID, "Test Organization Leaders by Quest")

        # Horizontal Category Selectors
        self._category_scroll_view = (By.XPATH, "//XCUIElementTypeScrollView")
        self._category_buttons = (By.XPATH, "//XCUIElementTypeScrollView//XCUIElementTypeButton")

        # Leaderboard List Items
        self._collection_view = (By.XPATH, "//XCUIElementTypeCollectionView")
        self._player_cells = (By.XPATH, "//XCUIElementTypeCollectionView//XCUIElementTypeCell")

        # Action Buttons
        self._find_me_button = (By.ACCESSIBILITY_ID, "Find Me")

    # --- Properties ---

    @property
    def header(self):
        return self.driver.find_element(*self._header_title)

    @property
    def back_button(self):
        return self.driver.find_element(*self._back_button)

    @property
    def find_me_button(self):
        return self.driver.find_element(*self._find_me_button)

    @property
    def player_list(self):
        return self.driver.find_elements(*self._player_cells)

    # --- Actions ---

    def wait_for_screen_load(self):
        """Ensures the leaderboard content is visible."""
        self.wait.until(EC.visibility_of_element_located(self._header_title))
        self.wait.until(EC.presence_of_element_located(self._collection_view))

    def tap_back(self):
        self.back_button.click()

    def select_category_by_index(self, index):
        """Taps a quest category button in the horizontal scroll bar."""
        categories = self.driver.find_elements(*self._category_buttons)
        if index < len(categories):
            categories[index].click()

    def get_player_data_by_rank(self, rank):
        """
        Retrieves player details from the list.
        :param rank: 0-based index (0 for 1st place).
        :return: Dict containing username and score.
        """
        players = self.player_list
        if rank < len(players):
            cell = players[rank]
            # [1] maps to name, [2] maps to score value in provided XML
            return {
                "username": cell.find_element(By.XPATH, ".//XCUIElementTypeStaticText[1]").get_attribute("value"),
                "score": cell.find_element(By.XPATH, ".//XCUIElementTypeStaticText[2]").get_attribute("value")
            }
        return None

    def tap_find_me(self):
        self.find_me_button.click()