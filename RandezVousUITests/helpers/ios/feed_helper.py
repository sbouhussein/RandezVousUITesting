import re
import xml.etree.ElementTree as ET

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC

from helpers.ios.base_helper import BaseHelper


class FeedHelper(BaseHelper):
    """The custom-quest Quest Feed; find posts by unique text, since the shared feed has many and rows aren't single elements."""

    card = (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeButton' AND label CONTAINS 'Quest Feed'")
    back_button = (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeButton' AND label == 'Back'")
    new_post_button = (AppiumBy.ACCESSIBILITY_ID, "New post")
    compose_field = (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeTextField")
    compose_post_button = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "Post"`]')

    _PROFILE_LABEL = re.compile(r"^View (.+)'s profile$")

    def is_card_visible(self):
        return self.is_visible(self.card, custom_timeout=5)

    def get_card_preview(self):
        """The card's latest-item line, e.g. "AutomatedTester: Prompt"."""
        label = self.driver.find_element(*self.card).get_attribute("label") or ""
        return label.split("Quest Feed, ", 1)[1] if "Quest Feed, " in label else ""

    def open_feed(self, max_scrolls=4):
        """Scrolls the quest screen until the Quest Feed card is on screen, opens it, and waits for the feed."""
        for _ in range(max_scrolls):
            if self.is_card_visible():
                break
            self.driver.execute_script("mobile: scroll", {"direction": "down"})
        self.wait.until(EC.element_to_be_clickable(self.card)).click()
        self.wait.until(EC.visibility_of_element_located(self.new_post_button))

    def close_feed(self):
        self.wait.until(EC.element_to_be_clickable(self.back_button)).click()

    def get_posts(self):
        """Rendered posts, newest first, as {"author", "texts", "posted_for", "in_response_to"}."""
        root = ET.fromstring(self.driver.page_source)
        posts, current = [], None
        for el in root.iter():
            if el.get("visible") != "true":
                continue
            kind, label = el.tag.replace("XCUIElementType", ""), el.get("label") or ""
            if kind == "Button":
                profile = self._PROFILE_LABEL.match(label)
                if profile:
                    current = {"author": profile.group(1), "texts": [], "posted_for": None, "in_response_to": None}
                    posts.append(current)
                elif current is not None and label.startswith("Posted for:, "):
                    current["posted_for"] = label.split(", ", 1)[1]
                elif current is not None and label.startswith("in response to, "):
                    current["in_response_to"] = label.split(", ", 1)[1]
                elif current is not None and label == "Comment":
                    current = None  # last element of a row
            elif kind == "StaticText" and current is not None and label:
                current["texts"].append(label)
        return posts

    def find_post(self, text):
        """First rendered post that has a line equal to `text`, or None."""
        return next((p for p in self.get_posts() if text in p["texts"]), None)

    def get_latest_post(self):
        posts = self.get_posts()
        return posts[0] if posts else None

    def compose_post(self, text):
        """Posts a free-form message from the feed's New post sheet and waits for the sheet to close."""
        self.wait.until(EC.element_to_be_clickable(self.new_post_button)).click()
        field = self.wait.until(EC.visibility_of_element_located(self.compose_field))
        field.send_keys(text)
        self.wait.until(EC.element_to_be_clickable(self.compose_post_button)).click()
        self.wait.until(EC.invisibility_of_element_located(self.compose_field))
