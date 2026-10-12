# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Automated UI test suite for the RandezVous product, built with Appium + Selenium + pytest. Covers:
- **iOS app** (`tests/ios/`) — driven via Appium/XCUITest against a local iOS Simulator.
- **Web app** (`tests/web/`) — driven via Selenium against a local Desktop Safari (or Chrome via `--browser chrome`), pointed at a React app the test suite spins up itself in rvsite's **QA mode** (`npm start`: backend on port 3000 + Vite `--mode qa` on port **5174**, both against `randezvous-qa`; located at `WEB_APP_PATH` — a repo checked out alongside this one's parent directory, default `../../RandezVousSite/rvsite`). Also covers mobile-browser variants of that same app via `mobile_chrome_driver` (desktop Chrome, spoofed UA) and `android_chrome_driver` (real Chrome on an Android emulator).

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
- Seed the web fixtures once per QA project: `python scripts/firebase/seed_qa_web_fixtures.py` (idempotent; creates the `web-*` quests under org `test-org` plus the test accounts — see "Web fixtures" below).
- Firebase service account key for the **`randezvous-qa`** project → save to `private/service-account-key-qa.json` (gitignored, not committed; `firebase_init` in `conftest.py` hard-fails at session start if this file is missing). This suite never uses prod's key.
- iOS app must be built from `RandevousMain` with the "RandezVous QA" scheme (embeds `GoogleService-Info-QA.plist`), and `FIREBASE_APP_CHECK_DEBUG_TOKEN` must be registered in Console → `randezvous-qa` → App Check, or `joinQuest` fails with "unauthenticated".
- `.env` values `DEVICE_NAME` / `PLATFORM_VERSION` / `UDID` must match the actual Simulator (Xcode → Window → Devices and Simulators)

Android (`android_chrome_driver`): `./setup.sh` runs `scripts/setup_android.sh`, which installs the SDK, `adb`, a Google Play system image (real Chrome, not AOSP) and the AVD named by `ANDROID_DEVICE_NAME` (several GB; `SKIP_ANDROID=1 ./setup.sh` skips it). Still manual:
- Appium UiAutomator2 driver: `appium driver install uiautomator2` (`setup.sh` warns if it's missing)
- Boot the AVD before running Android tests (`~/Library/Android/sdk/emulator/emulator -avd Pixel_8_API_34 -no-snapshot -no-audio`) — `android_chrome_driver` targets whatever `adb devices` reports (or `ANDROID_UDID` in `.env` if more than one device is attached). `conftest.py` finds `adb` and defaults `ANDROID_HOME` under `~/Library/Android/sdk`, so no shell-profile edits are needed.
- Don't `lsof -ti:5173 | xargs kill` while the emulator is up — its `adb reverse` tunnels show up as connections on those ports and you'd kill the emulator. The fixture's `kill-port` only hits listeners, so it's safe.
- The first web run after a fresh `npm install` can fail while Vite re-optimizes dependencies; re-run once.

## Common commands

```bash
# Run everything
pytest RandezVousUITests

# Run one test (path convention: Tests/<platform>/suite_<area>/tst_<name>/test.py -- note the capital T;
# pytest.ini's `testpaths = tests` doesn't match the real `Tests/` folder, so always pass an explicit path)
pytest RandezVousUITests/Tests/ios/suite_Quest_Activity/tst_Complete_Quest_From_Login/test.py --udid <simulator-udid>

# Run by test name (with a path, e.g. `pytest RandezVousUITests/Tests -k "complete_quest_from_login"`)

# Web tests without a window taking over your screen (desktop Safari can't run headless)
pytest RandezVousUITests/Tests/web --browser chrome --headless

# iOS headless (no visible simulator window)
pytest RandezVousUITests/Tests/ios/suite_Quest_Activity/tst_Complete_Quest_From_Login/test.py --udid <simulator-udid> --headless

# Verbose + stop on first failure + show prints
pytest -s -v --maxfail=1
```

`pytest.ini` (in `RandezVousUITests/`) sets `testpaths = tests`, discovers files named exactly `test.py`, and always runs with `-v -s --capture=tee-sys`. `pythonpath = .` means imports in tests/helpers are rooted at `RandezVousUITests/` (e.g. `from helpers.ios.login_page_helper import LoginPageHelper`).

Every test run auto-generates an HTML dashboard in `RandezVousUITests/reports/Execution_Report_<timestamp>.html` (aggregated logs, failure line/screenshot per test) — this is a `pytest_sessionfinish` hook in `conftest.py`, not `pytest-html`.

## Architecture

### conftest.py — shared fixtures (session root: `RandezVousUITests/`)

- **`appium_server`** (session scope): kills anything already on `APPIUM_PORT`, launches `appium` as a subprocess (with `--allow-insecure uiautomator2:chromedriver_autodownload`, needed for `android_chrome_driver`'s `chromedriverAutodownload` capability to actually work), logs to `RandezVousUITests/Tests/logs/appium_server.log`.
- **`firebase_init`** (session scope, autouse): initializes `firebase_admin` from `private/service-account-key-qa.json` (the `randezvous-qa` project; there is no `--env` switch and prod is never used). Fails the whole session immediately if the key is missing.
- **`rv_driver`**: fresh Appium session against the RandezVous iOS app (`RV_BUNDLE_ID`), full reset each test. Default fixture for iOS tests.
- **`rv_driver_no_reset`**: same but `noReset=True` — use when a test needs to preserve app state from a prior session.
- **`safari_driver`**: Appium session against mobile Safari (`SAFARI_BUNDLE_ID`) — for iOS deep-link flows that start in a browser.
- **`desktop_safari_driver`**: native macOS Desktop Safari (or Chrome/Firefox via `--browser`), navigates to `http://localhost:5174`, clears local/session storage, waits for React to hydrate (a visible header "Login" link or email input — the root route is the marketing landing page). Used by all web tests. Teardown (in a `try/finally`, so it also runs when setup fails) closes every window, quits the driver, and — for Safari — ends that session's own `Safari --automation` process, which `driver.quit()` otherwise leaves running and which blocks the next session ("already paired with a different session"); it prints "Safari automation processes left after teardown: N" (should be 0). Safari takes over the screen for the whole run; use `--browser chrome --headless` to avoid that.
- **`mobile_chrome_driver`**: desktop Chrome pinned to an Android user-agent string — cheap way to make `rvsite`'s `detectPlatform()` treat the session as a phone browser without needing a real device; can only observe the fallback *href*, not real intent-link navigation.
- **`android_chrome_driver`**: real mobile Chrome on an Android emulator/device via Appium's UiAutomator2 driver — the Android counterpart to `safari_driver`, and what actually exercises Android's intent-link resolution (`mobile_chrome_driver` can't). Resolves the target device from `ANDROID_UDID` or, if unset, whatever single device `adb devices` reports. Runs `adb reverse` for ports 5174/3000 on setup (removed on teardown) so the emulator's own `localhost` reaches the host's dev servers. RV's TWA (`com.randezvous.RandezVous`, `RV_ANDROID_PACKAGE`) is already live on Google Play — see `rvsite/public/.well-known/assetlinks.json` — so this same setup could later drive it directly via `appPackage`/`appActivity` instead of the browser.
- **`restart_node_server_for_web`** (function scope, autouse, only for tests under a `/web/` path): kills anything on ports 3000/5173/5174, runs `npm start` in `WEB_APP_PATH` (rvsite's QA target: backend + Vite `--mode qa` together; never `start:prod`), polls both ports until ready, tears down after the test. This means **web tests require the `RandezVousSite/rvsite` repo to be checked out and runnable** at `WEB_APP_PATH`.
- **`setup_teardown`** (autouse): reads the `@pytest.mark.cleanup(type=..., value=..., score=...)` marker and calls `cleanup_user_data()` from `helpers/ios/firebase_cleanup_helper.py` to wipe Firestore test fields (`username`, `questHist`, optionally `score`) by username or email, directly against Firebase. Most tests that log in as a real seeded test account carry this marker.
- Both driver fixtures pass `FIREBASE_APP_CHECK_DEBUG_TOKEN` (if set) as a process arg so Firebase App Check accepts requests from the automation build.

### Page Object Model — `helpers/`

Split by platform: `helpers/ios/`, `helpers/android/`, and `helpers/web/`. `helpers/ios/` and `helpers/web/` each have their own `base_helper.py` defining `BaseHelper` (wraps `WebDriverWait`, exposes `is_visible()` / `click()`). The web `click()` additionally scrolls the element into view and falls back to a JS click if a native click is intercepted (common with sticky headers/overlays). `helpers/android/` currently just has `device_helper.py` — Android tests otherwise reuse `helpers/web/`'s page objects against `android_chrome_driver`, since it's still driving a browser. Both platforms' `DeviceHelper` (install-state / foreground checks) subclass `helpers/common/device_helper_base.py`'s `DeviceHelperBase`, keyed by whichever app identifier the platform uses (bundle ID on iOS, package name on Android).

`HomepageHelper.login()` / `login_from_url()` go through `_submit_credentials`, which retries a stalled Firebase sign-in (page stays on `/login`, form filled, no error — or `auth/network-request-failed`) by reloading the login page and resubmitting up to 3 times. Root cause of the stall is unresolved and it is still intermittent in desktop Safari; see the README's Known Quirks.

Convention per helper class:
- Locators are **class-level attributes**, not set in `__init__`, so they're inspectable without instantiating.
- `__init__` only sets `driver` / `wait`.
- Methods are **actions only** — no `assert` inside helpers; assertions belong in the test file.
- iOS: prefer `AppiumBy.IOS_CLASS_CHAIN` for elements without a unique Accessibility ID; `AppiumBy.XPATH` is last resort. When `.click()` is unreliable on overlapping XCUITest elements, use `driver.execute_script('mobile: tap', {'element': el.id, 'x': .., 'y': ..})`.

### Tests — `tests/{ios,web}/suite_<feature_area>/tst_<what_it_tests>/test.py`

`tests/web/android/` groups the quest-onboarding suite (`suite_Quest_Onboarding_Access`) — the tests merged in with the Android emulator work. Only one of them uses the emulator (`android_chrome_driver`); the rest run in desktop Chrome/Safari or iOS Safari, so Android tests can be selected or skipped by path (`pytest RandezVousUITests/Tests/web/android`). It stays under `web/` because the web-server fixture keys off that path segment.

One test function per file, named `test_<what_it_tests>`, taking a driver fixture as its argument. No setup/teardown logic in the test itself (lives in `conftest.py`). Conditional navigation (e.g. `if welcome.verify_welcome_modal_is_displayed(): ...`) is acceptable for screens that only appear on first launch or after specific state changes.

### scripts/firebase/

Standalone Firebase Admin scripts (not part of the pytest suite) for direct data manipulation — e.g. `delete_account.py`, `firebase_admin_client.py`. Use these for one-off data resets outside of test runs.

## Web fixtures (randezvous-qa)

Everything — iOS, web, the web servers, Admin SDK calls — runs against `randezvous-qa`. The iOS suite uses quest `test-automation-quest`. The web suite uses fixtures defined in **one place**, `helpers/web/quest_test_data.py` (ports, org `test-org`, quest IDs, test accounts, usernames); tests import the constants instead of hardcoding IDs or URLs. `scripts/firebase/seed_qa_web_fixtures.py` (re-runnable) creates them: the `web-*` quests (Firestore doc + activities JSON in Cloud Storage + `quest_index` + org `privateQids`), cloned from `test-automation-quest`, and the email/password accounts. Test accounts need a `username` or rvsite parks them on "Create Your Username" and they never leave `/login` — the seed sets it. Activity names are `"<Type> Activity"` because the web helpers locate on rvsite's rendered headings and aria-labels. Change an ID in `quest_test_data.py`, then re-run the seed.

The domain-restricted **happy path** (`tst_join_domain_quest_with_correct_domain`) signs in as a *fabricated Google-provider* account, `google_domain_user@randezvous.com` (uid `qa-web-google-domain-user`, created by the seed with `auth.import_users()`), via `helpers/web/google_identity_helper.py`: it mints a custom token, exchanges it in the page, and POSTs the ID token to `/api/auth/session-login` through the app's own `apiClient` (rvsite derives "signed in" from that session cookie; the dev backend skips App Check). rvsite's `google_hd` policy only accepts a `google.com` provider entry on an allowed domain, so the email/password `test_user@randezvous.com` account can't pass it. A second fabricated account, `google_wrong_domain_user@gmail.com` (uid `qa-web-google-wrong-domain-user`, `google.com` provider on @gmail.com), drives the **unhappy path** (`tst_join_domain_quest_blocked_for_wrong_google_domain`): a Google user on the wrong domain is refused with the "requires a @randezvous.com account. You are signed in with @gmail.com" message and a Switch-accounts button, never reaches the quest, and gets no `questGrants` doc — the wrong-*domain* branch, distinct from the email/password wrong-*provider* branch. These cover the backend domain check and the rendering, not real Google consent-screen behavior.

Known web-suite caveats: `tst_complete_expired_quest` skips itself because rvsite `main` no longer has the dev-only quest `timing` endpoint it needs; `tst_join_domain_quest_not_signed_in` is an unfinished stub (named `tst_`, so pytest never collects it); `tst_onboarding_ios_safari_fallback_*` and `..._deep_link_opens_app_*` are mutually exclusive (one needs the RV app uninstalled), so one always skips on a simulator that has it installed.

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

Never read or commit: `.env`, `private/` (contains `service-account-key-qa.json`). `.claude/` is also gitignored locally.
