from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

from helpers.ios.custom_quest_helper import CustomQuestPage


class PhotoUploadHelper(CustomQuestPage):
    """The photo activity's upload screen; the line under the buttons shows who can see the image, and the caption bar only exists for a Public upload on a quest with a feed."""

    PUBLIC = "Public"
    ADMIN_ONLY = "Admin Only"

    caption_button = (AppiumBy.ACCESSIBILITY_ID, "Add caption to feed post…")
    caption_field = (AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeTextField")
    caption_done_button = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "Done"`]')
    public_button = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "Public"`]')
    admin_only_button = (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`name == "Admin Only"`]')
    visibility_text = (AppiumBy.IOS_PREDICATE, "label BEGINSWITH 'Image will be visible to:'")
    send_button = (AppiumBy.IOS_PREDICATE, "label == 'Send'")

    def select_photo(self, activity="Photo"):
        """Opens the photo activity and picks the most recent image, leaving the screen ready to submit."""
        self.click_activity(activity)
        self.click_check_requirements()
        self.click_submit_photo_button()
        self.click_photo_button()
        self.select_most_recent_image()

    def select_visibility(self, option):
        locator = {self.PUBLIC: self.public_button, self.ADMIN_ONLY: self.admin_only_button}[option]
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def get_visibility_text(self):
        return self.wait.until(EC.visibility_of_element_located(self.visibility_text)).get_attribute("label")

    def is_caption_field_visible(self):
        try:
            return self.driver.find_element(*self.caption_button).is_displayed()
        except NoSuchElementException:
            return False

    def add_caption(self, text):
        self.wait.until(EC.element_to_be_clickable(self.caption_button)).click()
        self.wait.until(EC.visibility_of_element_located(self.caption_field)).send_keys(text)
        self.wait.until(EC.element_to_be_clickable(self.caption_done_button)).click()
        self.wait.until(EC.invisibility_of_element_located(self.caption_done_button))

    def submit(self):
        self.wait.until(EC.visibility_of_element_located(self.send_button)).click()

    def finish_upload(self):
        """After Send: closes the rating popup and the activity sheet and returns to the quest screen."""
        self.dismiss_rating_popup_if_present()
        self.click_out_of_activity()
        self.click_back()

    def upload_photo(self, visibility=PUBLIC, caption=None, activity="Photo"):
        """Whole flow: pick the photo, choose visibility, optionally caption (Public only), send, and return to the quest screen."""
        self.select_photo(activity)
        if visibility != self.PUBLIC:
            self.select_visibility(visibility)
        if caption:
            self.add_caption(caption)
        self.submit()
        self.finish_upload()
