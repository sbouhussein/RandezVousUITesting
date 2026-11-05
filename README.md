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
- (Optional) PyCharm: [download](https://www.jetbrains.com/pycharm/download/?section=mac), then File → Open → this repo. Set Settings → Tools → Python Integrated Tools → **Default test runner = pytest**, interpreter = the repo's `.venv`, working directory = `RandezVousUITests/`, then right-click a `test.py` → **Run 'pytest in test.py'**. If the Run window shows `python .../test.py`, PyCharm ran it as a plain script (nothing was tested): delete that run configuration and re-run through pytest. Launch PyCharm from a terminal where nvm is loaded, since the harness needs `npm`/`appium` on `PATH`.

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
    │   ├── common/                    # Shared: DeviceHelperBase, access_data_helper (bans, grants, temporary quest/activity edits via the Admin SDK)
    │   ├── android/                   # Android device helper
    │   ├── ios/                       # Page Object Model classes for Appium/XCUITest
    │   │   ├── base_helper.py
    │   │   ├── custom_quest_helper.py
    │   │   ├── access_helper.py       # Join attempts that get refused (bans, ended, domain)
    │   │   ├── guest_join_helper.py   # Guest onboarding: dashboard code entry, welcome, username, start
    │   │   ├── ios_test_data.py       # Shared iOS constants: quest ID, test accounts, usernames
    │   │   ├── leaderboard_helper.py  # Leaderboard screen and the expected score for a given progress
    │   │   ├── feed_helper.py         # Quest Feed screen
    │   │   ├── photo_upload_helper.py # Photo upload screen (Public / Admin Only, caption)
    │   │   ├── feed_data_helper.py    # Admin-SDK feed/photo/Storage data for the feed tests
    │   │   ├── firebase_cleanup_helper.py
    │   │   └── ...
    │   └── web/                       # Page Object Model classes for Selenium
    │       ├── base_helper.py         # Shared click()/is_visible() with stability waits
    │       ├── homepage_helper.py     # Login (retries a stalled Firebase sign-in), find-quest
    │       ├── quest_helper.py
    │       ├── quest_test_data.py     # Single source of truth: ports, org, quest IDs, test accounts
    │       └── google_identity_helper.py  # Signs in as a fabricated Google-provider QA user (custom token)
    │
    └── Tests/
        ├── ios/
        │   ├── suite_Custom_Quest_Entry_Point/
        │   ├── suite_Quest_Access_Restrictions/   # Bans and domain-restricted quests
        │   ├── suite_Quest_Activity/
        │   ├── suite_Quest_Feed/                  # Quest Feed posts and photo visibility
        │   └── suite_Quest_Leaderboard/           # Starting points, completion bonus, ordering
        └── web/
            ├── android/               # Quest-onboarding suite (only one test uses the Android emulator)
            │   └── suite_Quest_Onboarding_Access/
            ├── suite_Custom_Quest_Entry_Point/
            ├── suite_Domain_Specific_Tests/   # incl. domain-restricted happy + unhappy paths
            ├── suite_Quest_Activity/
            └── suite_Quest_Bans/              # Banned or ended quests can't be joined; bans that don't apply
```

Each test lives at `Tests/<platform>/suite_<feature_area>/tst_<what_it_tests>/test.py`.

### iOS suites

| Suite | Covers |
|---|---|
| `suite_Custom_Quest_Entry_Point` | Joining a custom quest (code, URL as a guest and then signed in, dashboard, guest username), and refusal when the quest has ended |
| `suite_Quest_Activity` | Completing each activity type and whole quests, with leaderboard score checks, and completing an activity that has a start time (event) |
| `suite_Quest_Feed` | A Public photo posts to the feed (and the Public / Admin Only toggle), an Admin Only photo stays out of it and can't be read by a non-admin, and a free-form post |
| `suite_Quest_Access_Restrictions` | Refused joins from a quest or org-wide ban, a ban held under another uid with the same email, and bans that don't apply (other quest, expired); domain-restricted quests for a guest and for email/password accounts |
| `suite_Quest_Leaderboard` | Starting points after joining, the completion bonus, and equal scores listed by who finished first |

Notes:

- **Feed tests** find their own post by a unique caption because the shared feed holds many posts. They delete only what the test account authored, and the private-photo test also deletes that account's stored photos. Its Storage read check takes the QA web API key from `.env.qa` in the rvsite checkout (`WEB_APP_PATH`).
- **Access tests** write bans straight to Firestore (`helpers/common/access_data_helper.py`) and remove them afterwards, pass or fail.
- **Not automated on iOS:** joining a domain-restricted quest as a real Google user (correct or wrong domain). The app decides from the account's `google.com` provider and Google's sign-in sheet can't be driven, so the web suite covers it with fabricated Google users. The "Switch Account (Sign Out)" button starts that Google sign-in, so tests only check it is offered.
- **Leaderboard:** scoring defaults are 25 starting points, 100 per activity and a 250 completion bonus (`functions/scoring.js`); `LeaderboardHelper.expected_score` mirrors them, so a change there needs the helper updated. Equal scores share a rank number, so ordering tests compare row order. The one-activity quest is `OPEN_QUEST_ID` (the `web-open` fixture).
- **Start a guest test signed out.** A login left in the simulator's keychain survives the app's full reset and makes a link open the "already signed in" welcome with no username step, so guest tests call `sign_out_if_signed_in()` first.
- **A guest's "Exit Quest"** leaves immediately; accounts may get a confirmation sheet (`click_exit_quest` handles both).

### Web suites

| Suite | Covers |
|---|---|
| `suite_Custom_Quest_Entry_Point` | Entering a quest from the homepage and by link (signed in and out), a signed-out visitor entering a code, and a new account with no username |
| `suite_Domain_Specific_Tests` | Domain-restricted quests: wrong domain (email/password and Google), correct domain, not signed in, and a banned user (signed out, and on the correct domain) |
| `suite_Quest_Bans` | An org-wide ban, a ban held under another uid, or an ended quest can't be joined; bans for another quest or expired ones don't block |
| `suite_Quest_Activity` | Each activity type and its failure cases, whole quests (including points-to-win and domain-restricted), finishing an ended quest, and activities with a start time |
| `android/suite_Quest_Onboarding_Access` | Onboarding, team and feed pages: the restricted banner, wrong-provider sign-in, and deep-link / fallback behavior per platform |

Notes:

- **Temporary QA edits.** A few tests change a shared QA quest and put it back: `edited_quest` (Firestore fields, e.g. `pointsToWin`, `accessPolicy`) and `edited_activity` (an activity in the quest's Storage file, e.g. `customStartString`) in `helpers/common/access_data_helper.py`. Both restore in a `finally` (a killed run can leave an edit behind, so re-run the seed if a quest looks wrong). rvsite keeps quest definitions in a 10-minute in-memory cache that is shared by every web test in a run (the servers start once per session), so these tests also use the `fresh_web_backend` fixture, which restarts rvsite's backend before the test (so the edit is seen) and after it (so the edited quest isn't served to later tests); make the edit before the page loads.
- **Event window (from rvsite's `ActivityCompletion.jsx`).** An activity with a start time unlocks 1 hour before the start; only location activities also close, 24 hours after it. Other types stay open.
- **An ended quest on web** isn't joined: onboarding shows "This quest ended" and a "View Quest" button and never sends the join request. The backend also refuses per-activity completions after the end but still allows the final complete-quest call, which `tst_complete_expired_quest` relies on (it seeds a grant and finished activities, then lets the page finish the quest).
- `Tests/web/conftest.py` holds the shared `banned_user` and `restrict` fixtures (restrictions are always removed afterwards).

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

Create a new file in `helpers/ios/` or `helpers/web/` named after the screen or feature: `<screen_name>_helper.py`. Add its classes to that package's `__init__.py` so tests can import them with `from helpers.ios import ...` (or `helpers.web`).

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
- **A dev-run quest doesn't reflect a Firestore edit for up to 10 minutes.** `rvsite`'s backend caches quest data (`TTL.QUEST`) in memory, and the web servers start once per session, so every test in a run shares that cache. The old dev-only `POST /api/local-admin/quest/:orgId/:questId/timing` endpoint, which invalidated it, no longer exists in rvsite `main`. A test that edits a quest (`edited_quest` / `edited_activity`) should opt in to `fresh_web_backend` (restarts the backend before and after) and edit before the page loads; without it the edit passes when the test is run alone and fails in a full run.
- **A user "already joined" a quest, but `questHist` is missing.** `@pytest.mark.cleanup` only wipes the `questHist` *field* on the user doc — not the `questGrants` subcollection. `/api/quest/join` is idempotent: if a stale grant exists from an earlier run, it returns early and never rewrites `questHist`. Delete the leftover `questGrants/{questId}` doc before a test that needs a clean join.
- **Sign-in sometimes stalls on `/login`, and Firebase later reports `auth/network-request-failed`.** The Auth request hangs and the SDK stays broken until the page reloads. `HomepageHelper.login()` and `login_from_url()` detect the stall, reload, re-enter the credentials and resubmit up to 3 times (`_submit_credentials`); the older `retry_web_login` fixture in `conftest.py` is a backstop. The root cause is **not** found: the network path tested healthy and 12/12 headless Chrome and 9/9 direct-load Safari sign-ins succeeded. Still intermittent in Safari (seen on `tst_enter_custom_quest_from_URL_signed_in`); the retry's effectiveness isn't proven.
- **Safari has no headless mode and no `driver.get_log()`.** Both are Apple platform limitations, not something misconfigured. Use `--browser=chrome` or `--browser=firefox` if you need either.
- **`rvsite`'s dev server behaves oddly after many restarts in one session.** If tests that used to pass start failing at the same early step (e.g. the homepage's "Find Quest" button never becoming clickable) with no code change, try clearing Vite's cache: `rm -rf <rvsite>/node_modules/.vite`.
- **An Android emulator's `localhost` is itself, not your Mac.** `android_chrome_driver` still navigates to `http://localhost:5174`/`:3000` like every other web driver — it works around Android's loopback by running `adb reverse` on setup instead of teaching test code a separate `10.0.2.2`-style URL. Drive the emulator manually outside this fixture and you'll need to do the same.

### Web fixtures live in randezvous-qa

Everything runs against `randezvous-qa`: the iOS app (QA scheme), the web servers (`npm start` → Vite `--mode qa` on 5174 + backend on 3000) and every Firebase Admin call. Web fixtures (quests under org `test-org`, the test accounts and their usernames) are defined once in `RandezVousUITests/helpers/web/quest_test_data.py` and created by `python scripts/firebase/seed_qa_web_fixtures.py` — re-run it after editing that file or whenever QA data is reset. A test account needs a `username` or rvsite parks it on "Create Your Username" and it never leaves `/login`.

Web-suite caveats: `tst_join_domain_quest_not_signed_in` checks that a signed-out visitor gets a Sign In modal on `/find-quest` and no quest content; the domain happy and unhappy paths sign in as fabricated Google-provider QA users (see `helpers/web/google_identity_helper.py`); and the iOS Safari "fallback" and "deep link" tests are mutually exclusive (one needs the RV app uninstalled), so one always skips.

- **Desktop Safari takes over your screen.** Safari has no headless mode, the fixture maximizes its window, and Safari automation brings its window to the front on every command, so you can't work in other apps while web tests run. Use `--browser chrome --headless` for day-to-day runs (no window, lighter, no leak risk) and keep Safari for deliberate runs.
- **`driver.quit()` leaves `Safari --automation` running.** A stale one makes the next session fail with "The Safari instance is already paired with a different session". The desktop fixture ends its own session's process after `quit()` (printing "Safari automation processes left after teardown: N", which should be 0), and web sessions sweep leaked processes at start and end. Killing a run mid-test can still orphan one; the next run's sweep cleans it up. Your own Safari is never touched.
- **An idle Android emulator hogs the Mac.** Left running it used ~77% CPU and most free RAM, which slowed everything else (and made browser tests time out). Shut it down (`adb emu kill`) when you aren't running Android tests, or start it with `-no-window`.
- **Bare `pytest` collects nothing.** The committed `pytest.ini` says `testpaths = tests` but the folder is `Tests`; always pass an explicit path (`pytest Tests/web/...`).
