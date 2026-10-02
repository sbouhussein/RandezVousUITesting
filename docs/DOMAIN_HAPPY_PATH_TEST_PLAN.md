# Plan: Domain-Restriction Happy Path (Correct-Domain Google User)

## Scope

One thing only: get real coverage of a signed-in, correct-Google-domain user
successfully joining a domain-restricted, non-team quest — the actual config
of the upcoming university event. Today this path has zero coverage; the
existing `suite_Quest_Onboarding_Access` tests only exercise the *failure*
modes (banned, wrong domain, signed out), never the success case, because
driving a real Google OAuth popup through Selenium isn't viable (Google
blocks automated/webdriver browsers).

## Blocker — must be resolved first, before any other step here

**All web automation in this repo currently runs against the real prod
Firebase project, not `randezvous-qa`.**

`conftest.py`'s `web_servers` fixture launches the app under test via
`npm run start:prod`, with its own comment confirming this is deliberate:
`start:prod`, despite the name, is rvsite's explicit opt-in to the real prod
Firebase config (see `rvsite/CLAUDE.md`: `npm start` = QA on 5174, `npm run
start:prod` = prod, explicit opt-in, not the default). `docs/CLAUDE_GUIDELINES.md`
and this repo's own `CLAUDE.md` describe `restart_node_server_for_web` as
running `npm start` — that description is stale; the code it documents
now runs `npm run start:prod`.

This plan requires fabricating a Firebase Auth user via
`firebase_admin.auth.import_users()` with a spoofed `google.com` provider
entry, and minting `createCustomToken()` sign-ins for it. **That must never
run against the prod project.** Until every web test in this repo points at
`randezvous-qa` — server, service-account key, and App Check debug token —
none of the work below should be built, let alone run.

### Blocker checklist

- [ ] Switch `web_servers` (conftest.py) to launch rvsite via `npm start`
      (QA, port 5174/3000) instead of `npm run start:prod`, and update every
      `BASE_URL`/port reference in `helpers/web/quest_test_data.py` and
      elsewhere that hardcodes `5173`/prod assumptions.
- [ ] Swap `private/service-account-key.json` for the `randezvous-qa`
      project's service account key (currently prod's, per the default
      pointed at by `firebase_init`).
- [ ] Confirm `FIREBASE_APP_CHECK_DEBUG_TOKEN` in `.env` is the QA-project
      debug token, not prod's.
- [ ] Re-run the full existing suite against QA and confirm it's still green
      — this also validates QA has the Auth providers and Firestore state
      (rules/indexes/seed data) the current tests depend on.
- [ ] Fix `CLAUDE.md` / `docs/CLAUDE_GUIDELINES.md` to describe the actual
      QA-pointed command, so this doesn't silently drift back to prod later.
- [ ] Confirm QA's seeded test org/quest data (`ORG_ID`, `RESTRICTED_QUEST_ID`,
      etc. in `quest_test_data.py`) actually exists in `randezvous-qa` — it
      was copied from prod's rules/indexes, not necessarily its documents.

Nothing past this point starts until every box above is checked.

## Why the fabrication technique is safe to use once on QA

`backend/routes/quests.js`'s domain check (`google_hd` access policy) reads
`admin.auth().getUser(uid).providerData` for a `google.com` entry on the
allowed domain — it never re-verifies a live OAuth session. A normal user
can't self-assert that field (only a real, Firebase-verified Google sign-in
populates it), but `import_users()` can set it directly. That call, and
`createCustomToken()`, both require the project's service-account key —
the same privileged credential the backend itself already depends on to
run at all. Scoped to QA, this fabricates a realistic account state without
needing real Google Workspace credentials or automating Google's OAuth
popup (which webdriver-controlled browsers can't get through anyway).

## Plan (after the blocker is cleared)

1. **Identity fixture** — new `helpers/web/google_identity_helper.py`:
   - `import_users()` a test user into `randezvous-qa` Auth with a
     `providerData` entry for `google.com`, email on the domain
     `RESTRICTED_QUEST_ID` allows (see `quest_test_data.py`).
   - Guard rail: assert the initialized `firebase_admin` app's project ID
     is `randezvous-qa` before doing anything — refuse to run otherwise.
   - Teardown: delete the fabricated user (`auth.delete_user`) so QA doesn't
     accumulate test accounts across runs.

2. **Custom-token sign-in bridge** — extend `helpers/web/homepage_helper.py`
   (or a new method) to, given a UID: mint a custom token via
   `admin.auth().create_custom_token(uid)`, `driver.execute_script(...)` to
   call `signInWithCustomToken()` + `getIdToken()` in-browser, then POST
   that ID token to `/api/auth/session-login` exactly as the app's real
   login flow does. This produces the same session cookie a real Google
   sign-in would, without touching Google's OAuth servers.

3. **Tests** — new suite entries alongside
   `tests/web/suite_Quest_Onboarding_Access/`:
   - `tst_onboarding_domain_restricted_happy_path_mobile` — correct-domain
     signed-in user hits `onboarding_url(RESTRICTED_QUEST_ID)` on
     `mobile_chrome_driver`, completes "Continue on web" (or the Android
     "Open in App" fallback href, which resolves straight to the quest
     page for an already-allowed user), lands on the quest page with no
     `accessError`/`RestrictedBanner`.
   - `tst_onboarding_domain_restricted_happy_path_desktop` — same, on
     `desktop_safari_driver`, via `DefaultActionCard`'s "Start Quest".

4. **What this still won't prove** — flagged explicitly in both test
   docstrings: this validates the backend's domain check and the frontend's
   rendering of the success state, but not real Google OAuth consent-screen
   behavior itself (hosted-domain restriction at Google's login page,
   token refresh edge cases). That gap is accepted as out of scope; it's
   not something Selenium can safely automate at all.
