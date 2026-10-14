# RandezVous UI Testing

Automated UI test suite for RandezVous, built with [pytest](https://pytest.org). Covers:

- **iOS** — [Appium](https://appium.io) + XCUITest, driving the RandezVous app on a local iOS Simulator.
- **Web** — [Selenium](https://www.selenium.dev), driving a local checkout of the `rvsite` web app in Safari, Chrome, or Firefox.
- **Android** — [Appium](https://appium.io) + UiAutomator2, driving `rvsite` in real mobile Chrome on a local Android emulator/device (`android_chrome_driver`). RV's Trusted Web Activity app is already live on Google Play; this setup could later drive it directly instead of just the web flow it launches from.

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
- A local checkout of `rvsite` anywhere on disk. Set its path via `WEB_APP_PATH` in `.env` (defaults to `../../RandezVousSite/rvsite`, relative to wherever `pytest` is run from — see `.env.example`).
- Safari (built in), and/or Chrome and/or Firefox if you want to run tests against them.

**Android tests**
- The Appium UiAutomator2 driver (`appium driver install uiautomator2`). The Android SDK, `adb`, a Google Play system image and the AVD are installed for you by `./setup.sh` (via `scripts/setup_android.sh`, several GB; `SKIP_ANDROID=1 ./setup.sh` skips it). Android Studio is optional.
- An AVD (Android Studio → Device Manager) built from a system image with Google Play/Google APIs, so it ships with a real Chrome — plain AOSP images don't
- Android SDK platform-tools (`adb`) on `PATH` — Android Studio installs these but doesn't always add them to `PATH`
- The Appium server needs `ANDROID_HOME`/`ANDROID_SDK_ROOT` set too (not just `adb` on `PATH`) — `conftest.py`'s `appium_server` fixture defaults it to `~/Library/Android/sdk` if unset and that path exists; export it yourself if your SDK lives elsewhere
- The AVD booted before running tests (Device Manager, or `emulator -avd <name>` from the command line)

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

Not committed — obtain it from the **`randezvous-qa`** Firebase project (this suite never uses prod):

> Firebase Console → `randezvous-qa` → Project Settings → Service Accounts → Generate new private key

Save the downloaded JSON to `private/service-account-key-qa.json` (gitignored; the `private/` directory isn't committed either). `conftest.py`'s `firebase_init` hard-fails at session start if it's missing.

### 3. iOS setup

- Build the app from the main RandezVous iOS repo (`RandevousMain`) with the **"RandezVous QA"** scheme (it embeds `GoogleService-Info-QA.plist`, so the app talks to `randezvous-qa`), then launch it on the simulator.
- Register your `FIREBASE_APP_CHECK_DEBUG_TOKEN` in Firebase Console → `randezvous-qa` → App Check → Manage debug tokens, or `joinQuest` returns "unauthenticated".
- iOS tests use the QA quest `test-automation-quest`.
- In `.env` (not `conftest.py`, which just reads it), set `DEVICE_NAME`, `PLATFORM_VERSION`, and the simulator's `UDID`:
  Xcode → Window → Devices and Simulators (⇧⌘2) → Simulators tab → select your simulator → copy its **Identifier**. iOS tests also need `--udid <that identifier>` on the pytest command line (PyCharm: "Additional arguments").
- (Optional) PyCharm: [download](https://www.jetbrains.com/pycharm/download/?section=mac), then File → Open → this repo. Before running anything: Settings → Tools → Python Integrated Tools → **Default test runner = pytest**, interpreter = the repo's `.venv`, working directory = `RandezVousUITests/`. Then right-click a `test.py` → **Run 'pytest in test.py'**. If the Run window shows `python .../test.py` and "Process finished with exit code 0", PyCharm ran the file as a plain script (nothing was tested) — delete that run configuration and re-run through pytest. PyCharm also needs `npm`/`appium` on its `PATH` (launch it from a terminal where nvm is loaded), because the harness starts both.

### 4. Web setup

Web tests drive a **real local `rvsite` dev server** — they don't hit any deployed environment.

- Clone `rvsite` anywhere and run `npm install` there, then point `WEB_APP_PATH` (in this repo's `.env`) at it.
- `rvsite` needs its own `.env` configured (Firebase client config, App Check debug token, etc.) — see `rvsite`'s own `.env.example`.
- The harness runs `npm start` in `rvsite` — its **QA target** (Vite `--mode qa` on port 5174 + backend on 3000, using rvsite's `.env.qa` and `backend/.env.qa`, which must be filled in). Never `start:prod`. You don't need to run anything manually; `conftest.py` starts and stops both servers automatically per test session.
- Seed the QA fixtures once: `python scripts/firebase/seed_qa_web_fixtures.py` (see [Web fixtures live in randezvous-qa](#web-fixtures-live-in-randezvous-qa)).

### 5. Android setup

- Create and boot an AVD as described in [Prerequisites](#prerequisites), then set `ANDROID_DEVICE_NAME` / `ANDROID_PLATFORM_VERSION` in `.env` to match it.
- Nothing else to configure: `android_chrome_driver` auto-detects the booted emulator via `adb devices`, and forwards its loopback ports to the host's dev servers (`adb reverse`) so it reaches `http://localhost:5174` the same way every other web driver does. Set `ANDROID_UDID` in `.env` only if more than one emulator/device is attached at once.
- Headless Android isn't wired up the way `--headless` works for iOS/Chrome/Firefox — a headless AVD has to be launched with `emulator -no-window` at the emulator level, before Appium ever connects.

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
├── .env.example                       # Required env vars (copy → .env)
├── setup.sh                           # One-shot setup: venv, deps, .env, npm install, Android SDK/AVD
├── private/                           # Gitignored — never committed
│   └── service-account-key-qa.json    # Firebase Admin SDK key (randezvous-qa)
├── docs/                              # Plans/notes, e.g. DOMAIN_HAPPY_PATH_TEST_PLAN.md
├── scripts/
│   ├── setup_android.sh               # Installs Android SDK, adb, Google Play image, AVD (called by setup.sh)
│   └── firebase/                      # Standalone Firebase admin scripts (QA only)
│       └── seed_qa_web_fixtures.py    # Idempotent: creates the web-* quests and test accounts in randezvous-qa
│
└── RandezVousUITests/                 # UI test suite root (run pytest from repo root)
    ├── conftest.py                    # Fixtures: Appium/Selenium drivers, web dev-server lifecycle, cleanup
    ├── pytest.ini                     # pytest config (test discovery, markers)
    │
    ├── fixtures/                      # Static files, e.g. sample_photo.png seeded into the iOS simulator
    │
    ├── helpers/
    │   ├── common/                    # Shared by iOS + Android (DeviceHelperBase)
    │   ├── android/                   # Android device helper
    │   ├── ios/                       # Page Object Model classes for Appium/XCUITest
    │   │   ├── base_helper.py
    │   │   ├── custom_quest_helper.py
    │   │   ├── firebase_cleanup_helper.py
    │   │   └── ...
    │   └── web/                       # Page Object Model classes for Selenium
    │       ├── base_helper.py         # Shared click()/is_visible() with stability waits
    │       ├── homepage_helper.py     # Login (retries a stalled Firebase sign-in), find-quest
    │       ├── quest_helper.py
    │       ├── quest_test_data.py     # Single source of truth: ports, org, quest IDs, test accounts
    │       ├── google_identity_helper.py  # Signs in as a fabricated Google-provider QA user (custom token)
    │       └── firebase_test_data_helper.py  # Bans/grants/etc. set directly via the Admin SDK
    │
    └── Tests/
        ├── ios/
        │   ├── suite_Custom_Quest_Entry_Point/
        │   └── suite_Quest_Activity/
        └── web/
            ├── android/               # Quest-onboarding suite (only one test uses the Android emulator)
            │   └── suite_Quest_Onboarding_Access/
            ├── suite_Custom_Quest_Entry_Point/
            ├── suite_Domain_Specific_Tests/   # incl. domain-restricted happy + unhappy paths
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
| `mobile_chrome_driver` | Web | Desktop Chrome spoofing an Android user-agent — cheap phone-layout checks, not real intent-link behavior |
| `android_chrome_driver` | Android | Test needs real mobile Chrome / Android's actual intent-link resolution (e.g. deep-link flows) |

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
- **Sign-in sometimes stalls on `/login`, and Firebase later reports `auth/network-request-failed`.** The Auth request hangs (form still filled in, no error) and the Firebase SDK stays broken until the page reloads, so clicking Sign In again doesn't help. `HomepageHelper.login()` and `login_from_url()` now detect the stall (or the error text), reload the login page, re-enter the credentials and resubmit, up to 3 times (`_submit_credentials`); the older `retry_web_login` fixture in `conftest.py` still wraps `login()` as a backstop. Root cause is **not** found: the network path to Google tested healthy (240 requests, 0 failures) and 12/12 back-to-back sign-ins in headless Chrome and 9/9 in a direct-load Safari probe succeeded, so suspect something in the real test flow or desktop Safari itself. Still intermittent in Safari (seen on `tst_enter_custom_quest_from_URL_signed_in`); the retry's effectiveness isn't proven.
- **Safari has no headless mode and no `driver.get_log()`.** Both are Apple platform limitations, not something misconfigured. Use `--browser=chrome` or `--browser=firefox` if you need either.
- **`rvsite`'s dev server behaves oddly after many restarts in one session.** If tests that used to pass start failing at the same early step (e.g. the homepage's "Find Quest" button never becoming clickable) with no code change, try clearing Vite's cache: `rm -rf <rvsite>/node_modules/.vite`.
- **An Android emulator's `localhost` is itself, not your Mac.** `android_chrome_driver` still navigates to `http://localhost:5174`/`:3000` like every other web driver — it works around Android's loopback by running `adb reverse` on setup instead of teaching test code a separate `10.0.2.2`-style URL. Drive the emulator manually outside this fixture and you'll need to do the same.

### Web fixtures live in randezvous-qa

Everything runs against `randezvous-qa`: the iOS app (QA scheme), the web servers (`npm start` → Vite `--mode qa` on 5174 + backend on 3000) and every Firebase Admin call. Web fixtures (quests under org `test-org`, the test accounts and their usernames) are defined once in `RandezVousUITests/helpers/web/quest_test_data.py` and created by `python scripts/firebase/seed_qa_web_fixtures.py` — re-run it after editing that file or whenever QA data is reset. A test account needs a `username` or rvsite parks it on "Create Your Username" and it never leaves `/login`.

Web-suite caveats: `tst_complete_expired_quest` skips itself while rvsite `main` lacks the dev-only quest `timing` endpoint; `tst_join_domain_quest_not_signed_in` is an unfinished stub (not collected); the domain-restricted happy path signs in as a fabricated Google-provider QA user (`google_domain_user@randezvous.com`, created by the seed script, signed in by custom token — see `helpers/web/google_identity_helper.py`), and a second one on the wrong domain (`google_wrong_domain_user@gmail.com`) covers the refusal path; and the iOS Safari "fallback" and "deep link" tests are mutually exclusive (one needs the RV app uninstalled), so one always skips.

- **Desktop Safari takes over your screen.** Safari has no headless mode, the fixture maximizes its window, and Safari automation brings its window to the front on every command, so you can't work in other apps while web tests run. Use `--browser chrome --headless` for day-to-day runs (no window, lighter, no leak risk) and keep Safari for deliberate runs.
- **`driver.quit()` leaves `Safari --automation` running.** Each Safari session is its own process, and it survives `quit()` indefinitely; a stale one makes the next session fail with "The Safari instance is already paired with a different session". The desktop fixture ends its own session's process after `quit()` (and prints "Safari automation processes left after teardown: N", which should be 0), and web sessions sweep leaked `--automation` processes at start and end. Killing a run mid-test (`pkill`, Ctrl-C) can still orphan one — the next web run's start-of-session sweep cleans it up. Your own Safari (a process without `--automation`) is never touched.
- **An idle Android emulator hogs the Mac.** Left running it used ~77% CPU and most free RAM, which slowed everything else (and made browser tests time out). Shut it down (`adb emu kill`) when you aren't running Android tests, or start it with `-no-window`.
- **Bare `pytest` collects nothing.** The committed `pytest.ini` says `testpaths = tests` but the folder is `Tests`; always pass an explicit path (`pytest Tests/web/...`).
