# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Automated UI test suite for the RandezVous product, built with Appium + Selenium + pytest. Covers:
- **iOS app** (`tests/ios/`) — driven via Appium/XCUITest against a local iOS Simulator.
- **Web app** (`tests/web/`) — driven via Selenium against a local Desktop Safari, pointed at a React app the test suite spins up itself (backend on port 3000, Vite dev server on port 5173, located at `WEB_APP_PATH` — a repo checked out alongside this one's parent directory, default `../../RandezVousSite/rvsite`).

Both platforms share one Firebase backend, which tests clean up via the Firebase Admin SDK.

## Setup

```
./setup.sh                 # creates .venv, installs requirements.txt
source .venv/bin/activate
cp .env.example .env       # then fill in device/simulator values
```

Required one-time manual steps (not scriptable):
- Appium Inspector: `appium plugin install inspector`
- Appium XCUITest driver: `appium driver install xcuitest`
- Firebase service account key → save to `private/service-account-key.json` (gitignored, not committed; `firebase_init` in `conftest.py` hard-fails at session start if this file is missing)
- `.env` values `DEVICE_NAME` / `PLATFORM_VERSION` / `UDID` must match the actual Simulator (Xcode → Window → Devices and Simulators)

## Common commands

```bash
# Run everything
pytest RandezVousUITests

# Run one test (path convention: tests/<suite>/tst_<name>/test.py)
pytest RandezVousUITests/tests/ios/suite_quest_activity/tst_complete_quest_from_login/test.py

# Run by test name
pytest -k "complete_quest_from_login"

# Headless (no visible simulator window)
pytest RandezVousUITests/tests/ios/suite_quest_activity/tst_complete_quest_from_login/test.py --headless

# Verbose + stop on first failure + show prints
pytest -s -v --maxfail=1
```

`pytest.ini` (in `RandezVousUITests/`) sets `testpaths = tests`, discovers files named exactly `test.py`, and always runs with `-v -s --capture=tee-sys`. `pythonpath = .` means imports in tests/helpers are rooted at `RandezVousUITests/` (e.g. `from helpers.ios.login_page_helper import LoginPageHelper`).

Every test run auto-generates an HTML dashboard in `RandezVousUITests/reports/Execution_Report_<timestamp>.html` (aggregated logs, failure line/screenshot per test) — this is a `pytest_sessionfinish` hook in `conftest.py`, not `pytest-html`.

## Architecture

### conftest.py — shared fixtures (session root: `RandezVousUITests/`)

- **`appium_server`** (session scope): kills anything already on `APPIUM_PORT`, launches `appium` as a subprocess, logs to `RandezVousUITests/Tests/logs/appium_server.log`.
- **`firebase_init`** (session scope, autouse): initializes `firebase_admin` from `private/service-account-key.json`. Fails the whole session immediately if the key is missing.
- **`rv_driver`**: fresh Appium session against the RandezVous iOS app (`RV_BUNDLE_ID`), full reset each test. Default fixture for iOS tests.
- **`rv_driver_no_reset`**: same but `noReset=True` — use when a test needs to preserve app state from a prior session.
- **`safari_driver`**: Appium session against mobile Safari (`SAFARI_BUNDLE_ID`) — for iOS deep-link flows that start in a browser.
- **`desktop_safari_driver`**: native macOS Desktop Safari, navigates to `http://localhost:5173`, clears local/session storage, waits for React to hydrate. Used by all web tests.
- **`restart_node_server_for_web`** (function scope, autouse, only for tests under a `/web/` path): kills anything on ports 3000/5173, runs `npm start` in `WEB_APP_PATH` (starts backend + Vite together), polls both ports until ready (20s timeout each), tears down after the test. This means **web tests require the `RandezVousSite/rvsite` repo to be checked out and runnable** at `WEB_APP_PATH`.
- **`setup_teardown`** (autouse): reads the `@pytest.mark.cleanup(type=..., value=..., score=...)` marker and calls `cleanup_user_data()` from `helpers/ios/firebase_cleanup_helper.py` to wipe Firestore test fields (`username`, `questHist`, optionally `score`) by username or email, directly against Firebase. Most tests that log in as a real seeded test account carry this marker.
- Both driver fixtures pass `FIREBASE_APP_CHECK_DEBUG_TOKEN` (if set) as a process arg so Firebase App Check accepts requests from the automation build.

### Page Object Model — `helpers/`

Split by platform: `helpers/ios/` and `helpers/web/`, each with its own `base_helper.py` defining `BaseHelper` (wraps `WebDriverWait`, exposes `is_visible()` / `click()`). The web `click()` additionally scrolls the element into view and falls back to a JS click if a native click is intercepted (common with sticky headers/overlays).

Convention per helper class:
- Locators are **class-level attributes**, not set in `__init__`, so they're inspectable without instantiating.
- `__init__` only sets `driver` / `wait`.
- Methods are **actions only** — no `assert` inside helpers; assertions belong in the test file.
- iOS: prefer `AppiumBy.IOS_CLASS_CHAIN` for elements without a unique Accessibility ID; `AppiumBy.XPATH` is last resort. When `.click()` is unreliable on overlapping XCUITest elements, use `driver.execute_script('mobile: tap', {'element': el.id, 'x': .., 'y': ..})`.

### Tests — `tests/{ios,web}/suite_<feature_area>/tst_<what_it_tests>/test.py`

One test function per file, named `test_<what_it_tests>`, taking a driver fixture as its argument. No setup/teardown logic in the test itself (lives in `conftest.py`). Conditional navigation (e.g. `if welcome.verify_welcome_modal_is_displayed(): ...`) is acceptable for screens that only appear on first launch or after specific state changes.

### scripts/firebase/

Standalone Firebase Admin scripts (not part of the pytest suite) for direct data manipulation — e.g. `delete_account.py`, `firebase_admin_client.py`. Use these for one-off data resets outside of test runs.

## Naming conventions

| Thing | Convention | Example |
|---|---|---|
| Test/suite directories | `snake_case` | `tst_joining_quest_after_logging_in`, `suite_custom_quest_entry_point` |
| Helper files | `snake_case` | `quest_page_helper.py` |
| Helper classes | `PascalCase` | `CustomQuestPage` |
| Locator attributes | `snake_case` class-level | `start_quest_button = (...)` |
| Action methods | `snake_case` | `click_start_quest()` |
| Test functions | `test_<snake_case>` | `test_joining_quest_after_logging_in` |

## Secrets / gitignored paths

Never read or commit: `.env`, `private/` (contains `service-account-key.json`). `.claude/` is also gitignored locally.
