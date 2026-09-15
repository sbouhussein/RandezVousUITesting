# RandezVous UI Testing

Automated UI test suite for RandezVous, built with [pytest](https://pytest.org). Covers two platforms:

- **iOS** — [Appium](https://appium.io) + XCUITest, driving the RandezVous app on a local iOS Simulator.
- **Web** — [Selenium](https://www.selenium.dev), driving a local checkout of the `rvsite` web app in Safari, Chrome, or Firefox.

---

## Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Repository Structure](#repository-structure)
- [Adding Tests](#adding-tests)
- [Style Guide](#style-guide)
- [Known Quirks](#known-quirks)

---

## Prerequisites

**Common**
- Python 3.10+

**iOS tests**
- [Appium 2.x](https://appium.io/docs/en/2.0/) (`npm install -g appium`)
- Appium XCUITest driver (`appium driver install xcuitest`)
- Xcode + iOS Simulator (iPhone 17 Pro, iOS 26.4)
- RandezVous app installed on the simulator (`sbouhussein.github.io-rvsite.RandezVous`)

**Web tests**
- Node.js (for running the `rvsite` dev servers)
- A local checkout of `rvsite`, cloned to **exactly** `/Users/omar/workspace/rvsite` — this path is hardcoded in `conftest.py`'s `web_servers` fixture.
- Safari (built in), and/or Chrome and/or Firefox if you want to run tests against them.

---

## Setup

### 1. Clone and install this repo

```bash
git clone https://github.com/sbouhussein/RandezVousUITesting
cd RandezVousUITesting
chmod +x setup.sh
./setup.sh          # creates .venv, installs requirements.txt
```

For iOS work, also install the Appium Inspector plugin (used for finding object names):

```bash
appium plugin install inspector
```

### 2. Firebase service account key

Not committed — obtain it from the Firebase console:

> Firebase Console → Project Settings → Service Accounts → Generate new private key

Save the downloaded JSON to `private/service-account-key.json` (gitignored; the `private/` directory isn't committed either).

### 3. iOS setup

- Open Xcode with the RandezVous repo and press ▶ to build and launch the simulator.
- In `conftest.py`, set `DEVICE_NAME`, `PLATFORM_VERSION`, and the simulator's `UDID`:
  Xcode → Window → Devices and Simulators (⇧⌘2) → Simulators tab → select your simulator → copy its **Identifier**.
- (Optional) PyCharm: [download](https://www.jetbrains.com/pycharm/download/?section=mac), then File → Open → this repo. Right-click a `test.py` → **Run 'Python tests in test'**.

### 4. Web setup

Web tests drive a **real local `rvsite` dev server** — they don't hit any deployed environment.

- Clone `rvsite` to `/Users/omar/workspace/rvsite` and run `npm install` there.
- `rvsite` needs its own `.env` configured (Firebase client config, App Check debug token, etc.) — see `rvsite`'s own `.env.example`.
- ⚠️ **Local-only backend change required:** `tst_complete_expired_quest` depends on a dev-only endpoint, `POST /api/local-admin/quest/:orgId/:questId/timing`, added to `rvsite/backend/routes/local-admin.js` during this test suite's development. As of writing, this change — along with a matching `allowEnded` fix in `backend/routes/activities.js` and a `hasJoined` fix in `src/components/QuestDetail.jsx` — is **uncommitted in the local `rvsite` checkout**, not yet pushed anywhere. If you're setting up on a fresh machine or a clean `rvsite` clone, that one test will fail until those three changes exist in `rvsite`. (These should get committed/pushed to `rvsite` at some point — ask before assuming they have been.)
- `npm start` in `rvsite` now points at its QA target (port 5174) — the test harness instead runs `npm run start:prod`, which — despite the name — is the plain local-dev setup (regular `.env`, port 5173) these tests are built around. You don't need to run anything manually; `conftest.py` starts and stops both servers automatically per test session.

---

## Running Tests

### From the command line

```bash
cd RandezVousUITesting
source .venv/bin/activate

# Run everything
pytest RandezVousUITests

# Run one suite or one test
pytest RandezVousUITests/Tests/web/suite_Quest_Activity
pytest RandezVousUITests/Tests/ios/suite_Quest_Activity/tst_Complete_Quest_From_Login/test.py

# Run by test name
pytest -k "complete_quest"
```

### From PyCharm

Right-click any `test.py` → **Run 'Python tests in test'**.

### Choosing a browser (web tests only)

Web tests default to Safari. Pass `--browser` to use Chrome or Firefox instead — no code changes needed, Selenium auto-downloads the matching driver the first time each browser runs:

```bash
pytest RandezVousUITests/Tests/web --browser=chrome
pytest RandezVousUITests/Tests/web --browser=firefox
```

### Running headless

```bash
# iOS: runs the simulator headless
pytest RandezVousUITests/Tests/ios/suite_Quest_Activity/tst_Complete_Quest_From_Login/test.py --headless

# Web: Chrome or Firefox only -- Safari has no headless mode
pytest RandezVousUITests/Tests/web --browser=chrome --headless
pytest RandezVousUITests/Tests/web --browser=firefox --headless
```

### Useful flags

| Flag | Effect |
|---|---|
| `-s` | Show `print()` output live, even for passing tests |
| `-v` | Verbose — list each test's name and result, not just dots |
| `--maxfail=1` | Stop the whole run at the first failure |
| `-k "name"` | Run only tests whose name matches |

Combine as needed, e.g. `pytest -s -v --maxfail=1 RandezVousUITests/Tests/web`.

---

## Repository Structure

```
RandezVousUITesting/
├── .env.example                       # Required env vars for iOS tests (copy → .env)
├── private/                           # Gitignored — never committed
│   └── service-account-key.json       # Firebase Admin SDK key
├── scripts/                           # Standalone Firebase admin / data-reset scripts
│
└── RandezVousUITests/                 # UI test suite root (run pytest from repo root)
    ├── conftest.py                    # Fixtures: Appium/Selenium drivers, web dev-server lifecycle, cleanup
    ├── pytest.ini                     # pytest config (test discovery, markers)
    │
    ├── helpers/
    │   ├── ios/                       # Page Object Model classes for Appium/XCUITest
    │   │   ├── base_helper.py
    │   │   ├── custom_quest_helper.py
    │   │   ├── firebase_cleanup_helper.py
    │   │   └── ...
    │   └── web/                       # Page Object Model classes for Selenium
    │       ├── base_helper.py         # Shared click()/is_visible() with stability waits
    │       ├── homepage_helper.py
    │       └── quest_helper.py
    │
    └── Tests/
        ├── ios/
        │   ├── suite_Custom_Quest_Entry_Point/
        │   └── suite_Quest_Activity/
        └── web/
            ├── suite_Custom_Quest_Entry_Point/
            ├── suite_Domain_Specific_Tests/
            └── suite_Quest_Activity/
```

Each test lives at `Tests/<platform>/suite_<feature_area>/tst_<what_it_tests>/test.py`.

---

## Adding Tests

### 1. Create the test directory

```
Tests/<ios|web>/suite_<feature_area>/tst_<what_it_tests>/test.py
```

Example: `Tests/web/suite_profile/tst_edit_display_name/test.py`

### 2. Write the test function

One test function per file, named `test_<what_it_tests>`. Take a driver fixture from `conftest.py` as the argument:

| Fixture | Platform | Use when |
|---|---|---|
| `rv_driver` | iOS | App launches fresh (default) |
| `rv_driver_no_reset` | iOS | App must preserve state from a previous session |
| `safari_driver` | iOS | Test starts in mobile Safari (URL deep-link flows) |
| `desktop_safari_driver` | Web | Any web test — despite the name, respects `--browser`/`--headless` |

### 3. Add helpers for new screens

Create a new file in `helpers/ios/` or `helpers/web/` named after the screen or feature: `<screen_name>_helper.py`.

---

## Style Guide

### Naming

| Thing | Convention | Example |
|---|---|---|
| Test directories | `snake_case` | `tst_joining_quest_after_logging_in` |
| Suite directories | `PascalCase`-ish, matches existing suites | `suite_Custom_Quest_Entry_Point` |
| Helper files | `snake_case` | `quest_helper.py` |
| Helper classes | `PascalCase` | `QuestHelper` |
| Locator attributes | `snake_case`, set in `__init__` | `self.start_quest_button = (...)` |
| Action methods | `snake_case` | `click_start_quest()` |
| Test functions | `test_<snake_case>` | `test_joining_quest_after_logging_in` |

### Helper classes (Page Object Model)

- Locators are set on `self` in `__init__`, alongside the driver and a default `WebDriverWait`/`wait`.
- Methods are actions only — no assertions inside helpers. Assertions belong in the test.
- iOS: use `AppiumBy.IOS_CLASS_CHAIN` for elements without a unique Accessibility ID; `AppiumBy.XPATH` only as a last resort. When `.click()` is unreliable on overlapping elements, use the native tap: `driver.execute_script('mobile: tap', {'element': el.id, 'x': 10, 'y': 10})`.
- Web: use `By`/`expected_conditions` from Selenium. Route clicks through `BaseHelper.click()` rather than raw `wait.until(...).click()` — it waits for the element's position to stop changing first, which raw waits don't (see [Known Quirks](#known-quirks)).

### Test functions

- One test function per file; setup/teardown lives in `conftest.py`, not the test.
- Prefer `assert` with a descriptive message over silent failures.
- Conditional navigation (e.g. `if welcome.verify_welcome_modal_is_displayed()`) is fine for screens that only appear on first launch or after state changes.

---

## Known Quirks

A few non-obvious things learned the hard way, in case something breaks mysteriously:

- **Click a button right after opening an accordion, and it silently fails.** `element_to_be_clickable` only checks displayed+enabled — not whether the element is still mid-CSS-transition (e.g. an accordion still animating open). `BaseHelper.click()` now waits for the element's on-screen position to stabilize first. Use it instead of raw `wait.until(...).click()`.
- **A dev-run quest doesn't reflect a Firestore edit for up to 10 minutes.** `rvsite`'s backend caches quest data (`TTL.QUEST`). The dev-only `POST /api/local-admin/quest/:orgId/:questId/timing` endpoint updates a quest's `startTime`/`endTime` *and* invalidates that cache immediately — use it instead of writing to Firestore directly when a test needs to flip a quest's timing mid-run.
- **A user "already joined" a quest, but `questHist` is missing.** `@pytest.mark.cleanup` only wipes the `questHist` *field* on the user doc — not the `questGrants` subcollection. `/api/quest/join` is idempotent: if a stale grant exists from an earlier run, it returns early and never rewrites `questHist`. Delete the leftover `questGrants/{questId}` doc before a test that needs a clean join.
- **Login intermittently fails with `auth/network-request-failed`.** Documented but unresolved — happens rarely, cause not fully pinned down. Not fixed by retrying inside `HomepageHelper.login()`; a `retry_web_login` autouse fixture in `conftest.py` retries the whole login step for any web test if this happens.
- **Safari has no headless mode and no `driver.get_log()`.** Both are Apple platform limitations, not something misconfigured. Use `--browser=chrome` or `--browser=firefox` if you need either.
- **`rvsite`'s dev server behaves oddly after many restarts in one session.** If tests that used to pass start failing at the same early step (e.g. the homepage's "Find Quest" button never becoming clickable) with no code change, try clearing Vite's cache: `rm -rf /Users/omar/workspace/rvsite/node_modules/.vite`.
