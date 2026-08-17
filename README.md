# RandezVous UI Testing

Automated UI test suite for the RandezVous iOS app, built with [Appium](https://appium.io) + [pytest](https://pytest.org). Tests run against a local iOS Simulator via XCUITest.

Future scope includes the RandezVous web app and admin dashboard (`/Users/samibouhussein/RandezVousSite/rvsite`).

---
### Prerequisites

- Python 3.10+
- [Appium 2.x](https://appium.io/docs/en/2.0/) (`npm install -g appium`)
- Appium XCUITest driver (`appium driver install xcuitest`)
- Xcode + iOS Simulator (iPhone 17 Pro, iOS 26.4)
- RandezVous app installed on the simulator (`sbouhussein.github.io-rvsite.RandezVous`)

## Setup

- Download xcuitest which is the ios driver
  - https://appium.github.io/appium-xcuitest-driver/latest/getting-started/installation/
  
- Clone this repo: 
  - https://github.com/sbouhussein/RandezVousUITesting

- Navigate to RandezVousUITesting and run these commands
  - "chmod +x setup.sh"
  - "./setup.sh"
  - This will install NVM, Node.js and Appium

- Install Appium Inspector which is used for knowing object names
  - Run this command: "appium plugin install inspector"

### Installing Pycharm and opening the repo

- Link to Install Pycharm: https://www.jetbrains.com/pycharm/download/?section=mac
- Open the repo by clicking on File > Open and navigate to the repo in your file explorer

### Running a Test in PyCharm

- Open Xcode with the RandezVous Repo open 

- And click on the play button in order to build and launch the simulator

- Navigate to conftest.py in Pycharm and update these values 
  - DEVICE_NAME
  - PLATFORM_VERSION
  - UDID
    - Open Xcode.
    - In the top menu bar, click Window > Devices and Simulators (or press Shift + Command + 2). 
    - Click on the Simulators tab at the top of the window that appears. 
    - Select your specific simulator model from the list on the left. 
    - On the right side, you will see a field labeled Identifier. That is your UDID. You can right-click it to copy it.

- After RandezVous installs on the simulator go to PyCharm and double-click or right-click on the test.py of the test you want run and click Run 'Python tests in test'

### Add the Firebase service account key

The key is not committed. Obtain it from the Firebase console:

> Firebase Console → Project Settings → Service Accounts → Generate new private key

Save the downloaded JSON to:

```
private/service-account-key.json
```

This path is gitignored. The `private/` directory is created manually — it is never committed.

### Running a Test on the command line

- Open a terminal and navigate to the project.
  - ex. cd /Users/omar/PycharmProjects/PythonProject
  
- Run this command: "source .venv/bin/activate"

- If you want to run all the tests then run this command: "pytest RandezVousUITests"

- If you want to run only a specific test then you have to type the command above and the directory of where it is located
  - ex. "pytest RandezVousUITests/Tests/ios/suite_Quest_Activity/tst_Complete_Quest_From_Login/test.py"

- If you want to run it by name then you can run this command and keep the quotes around Name of Test: pytest -k "Name of Test"

- If you want to run all tests then from the same directory above run this command: "pytest RandezVousUITests/Tests/"

### Running a Test headless

- If you don't want to run a test using the simulator, you must specify when running the test on the command line by adding "--headless" at the end of your test directory where the test lives
  - ex. "pytest RandezVousUITests/Tests/suite_Quest_Activity/tst_Complete_Quest_From_Login/test.py --headless"

  
### Helpful Pytest Commands & Flags

When running tests from the command line, you can use these flags to customize your test execution and make debugging easier:

- `-s` (Show Prints):** By default, pytest hides your `print()` statements if a test passes. Use this flag to force pytest to print all console logs in real-time.
- `-v` (Verbose):** Provides a more detailed output in the terminal, listing the exact names of the tests that are passing or failing instead of just showing minimal dots.
- `--maxfail=1` (Stop on First Failure):** Aborts the entire test run the moment a single test fails. This is incredibly useful for debugging without waiting for a long suite to finish.

- Example Usage:
To run a test with detailed logging and stop immediately if it fails, combine the flags:
`pytest -s -v --maxfail=1`

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

- Locators are class-level attributes (not `self.` in `__init__`) so they can be inspected without instantiation.
- Instance state (`driver`, `wait`) is set in `__init__`.
- Methods are actions only — no assertions inside helpers. Assertions belong in the test.
- Use `AppiumBy.IOS_CLASS_CHAIN` for elements that lack a unique Accessibility ID. Use `AppiumBy.XPATH` only as a last resort.
- When a standard `.click()` is unreliable (common on overlapping elements in XCUITest), use the native tap: `driver.execute_script('mobile: tap', {'element': el.id, 'x': 10, 'y': 10})`.

### Test functions

- One test function per file, no setup/teardown in the test itself — that lives in `conftest.py`.
- Prefer `assert` with a descriptive message over silent failures.
- Conditional navigation (`if welcome.verify_welcome_modal_is_displayed()`) is acceptable for screens that only appear on first launch or after state changes.
