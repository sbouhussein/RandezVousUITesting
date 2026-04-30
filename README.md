# RandezVous UI Testing

Automated UI test suite for the RandezVous iOS app, built with [Appium](https://appium.io) + [pytest](https://pytest.org). Tests run against a local iOS Simulator via XCUITest.

Future scope includes the RandezVous web app and admin dashboard (`/Users/samibouhussein/RandezVousSite/rvsite`).

---

## Repository Structure

```
RandezVousUITesting/
├── .env.example                      # Required environment variables (copy → .env)
├── .gitignore
├── README.md
│
├── private/                          # Gitignored — never committed
│   └── service-account-key.json      # Firebase Admin SDK key
│
├── scripts/                          # Standalone Firebase admin / data-reset scripts
│
└── RandezVousUITests/                # UI test suite root (run pytest from here)
    ├── conftest.py                   # Appium server + driver fixtures (shared setup/teardown)
    ├── pytest.ini                    # pytest config (test discovery settings)
    │
    ├── helpers/                      # Page Object Model classes, one file per screen/feature
    │   ├── custom_quest_helper.py    # QuestHelper, CustomQuestPage
    │   ├── edit_profile_helper.py
    │   ├── experience_helper.py
    │   ├── leaderboard_helper.py
    │   ├── logger_helper.py
    │   ├── login_page_helper.py      # LoginPageHelper, WelcomeToQuestHelper, ChooseUsernameHelper, StartAdventureHelper
    │   ├── profile_helper.py
    │   ├── quest_feed_helper.py
    │   ├── quest_page_helper.py
    │   ├── reset_test_setup_helper.py
    │   └── sign_in_overlay_helper.py
    │
    └── tests/
        └── suite_custom_quest_entry_point/
            ├── tst_enter_custom_quest_on_dashboard/
            ├── tst_joining_quest_after_logging_in/
            ├── tst_joining_quest_through_url/
            └── tst_log_in_with_code_entry_point/
```

---

## Setup

### Prerequisites

- Python 3.10+
- [Appium 2.x](https://appium.io/docs/en/2.0/) (`npm install -g appium`)
- Appium XCUITest driver (`appium driver install xcuitest`)
- Xcode + iOS Simulator (iPhone 17 Pro, iOS 26.4)
- RandezVous app installed on the simulator (`sbouhussein.github.io-rvsite.RandezVous`)

### Install Python dependencies

```bash
pip install appium-python-client selenium pytest python-dotenv
```

### Configure environment variables

```bash
cp .env.example .env
```

`.env.example` ships with placeholder values. You must update `UDID`, `DEVICE_NAME`, and `PLATFORM_VERSION` to match your simulator before running tests.

### Find your iOS simulator info

**List all available simulators:**

```bash
xcrun simctl list devices available
```

This prints every simulator grouped by OS version, e.g.:

```
== iOS 26.4 ==
    iPhone 17 Pro (02702BB3-0AE0-4167-9651-39F68787A375) (Shutdown)
```

Set your `.env` values from that output:

| Variable | Where to get it |
|---|---|
| `DEVICE_NAME` | The simulator name (e.g. `iPhone 17 Pro`) |
| `PLATFORM_VERSION` | The iOS version label (e.g. `26.4`) |
| `UDID` | The UUID in parentheses |

**Alternative — Xcode UI:**

Open Xcode → **Window → Devices and Simulators** → select the **Simulators** tab. The Identifier field is the UDID.

### Add the Firebase service account key

The key is not committed. Obtain it from the Firebase console:

> Firebase Console → Project Settings → Service Accounts → Generate new private key

Save the downloaded JSON to:

```
private/service-account-key.json
```

This path is gitignored. The `private/` directory is created manually — it is never committed.

---

## Running Tests

```bash
cd RandezVousUITests
pytest
```

pytest starts an Appium server once for the session, runs all tests, then shuts it down. Appium server logs are written to `logs/appium_server.log` (gitignored).

To run a single suite or test:

```bash
pytest tests/suite_custom_quest_entry_point/
pytest tests/suite_custom_quest_entry_point/tst_joining_quest_after_logging_in/
```

---

## Adding Tests

### 1. Create the test directory

Follow the naming convention — all `snake_case`:

```
tests/suite_<feature_area>/tst_<what_it_tests>/test.py
```

Example:

```
tests/suite_profile/tst_edit_display_name/test.py
```

### 2. Write the test function

Each `test.py` contains one test function named `test_<what_it_tests>`. Use a fixture from `conftest.py` as the argument:

| Fixture | Use when |
|---|---|
| `rv_driver` | App launches fresh (default) |
| `rv_driver_no_reset` | App must preserve state from a previous session |
| `safari_driver` | Test starts in Safari (URL deep-link flows) |

```python
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
```

### 3. Add helpers for new screens

Create a new file in `helpers/` named after the screen or feature: `<screen_name>_helper.py`.

---

## Style Guide

### Naming

| Thing | Convention | Example |
|---|---|---|
| Test directories | `snake_case` | `tst_joining_quest_after_logging_in` |
| Suite directories | `snake_case` | `suite_custom_quest_entry_point` |
| Helper files | `snake_case` | `quest_page_helper.py` |
| Helper classes | `PascalCase` | `CustomQuestPage` |
| Locator attributes | `snake_case` class-level | `start_quest_button = (...)` |
| Action methods | `snake_case` | `click_start_quest()` |
| Test functions | `test_<snake_case>` | `test_joining_quest_after_logging_in` |

### Helper class structure (Page Object Model)

Each helper class follows three sections in order:

```python
class MyScreenHelper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    # --- Locators (class-level tuples) ---
    some_button = (AppiumBy.ACCESSIBILITY_ID, "Button Label")

    # --- Actions ---
    def click_some_button(self):
        self.wait.until(EC.element_to_be_clickable(self.some_button)).click()
```

- Locators are class-level attributes (not `self.` in `__init__`) so they can be inspected without instantiation.
- Instance state (`driver`, `wait`) is set in `__init__`.
- Methods are actions only — no assertions inside helpers. Assertions belong in the test.
- Use `AppiumBy.IOS_CLASS_CHAIN` for elements that lack a unique Accessibility ID. Use `AppiumBy.XPATH` only as a last resort.
- When a standard `.click()` is unreliable (common on overlapping elements in XCUITest), use the native tap: `driver.execute_script('mobile: tap', {'element': el.id, 'x': 10, 'y': 10})`.

### Test functions

- One test function per file, no setup/teardown in the test itself — that lives in `conftest.py`.
- Prefer `assert` with a descriptive message over silent failures.
- Conditional navigation (`if welcome.verify_welcome_modal_is_displayed()`) is acceptable for screens that only appear on first launch or after state changes.
