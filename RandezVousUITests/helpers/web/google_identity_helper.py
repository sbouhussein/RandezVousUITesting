"""Signs a browser in as the fabricated Google-provider test user, without Google's OAuth.

Driving a real Google sign-in through Selenium isn't viable (Google blocks webdriver browsers), and
rvsite's `google_hd` quest policy (backend/routes/quests.js) only accepts a user whose Firebase Auth
record has a `google.com` provider entry on an allowed domain. seed_qa_web_fixtures.py fabricates such
a user in randezvous-qa; this helper signs in as them:

  1. mint a custom token for the user's UID (Admin SDK),
  2. in the page, exchange it for an ID token (Identity Toolkit) and POST it to /api/auth/session-login
     through the app's own apiClient, which sets the same httpOnly session cookie a real login does.

rvsite's useAuth derives "signed in" from that cookie (via /api/auth/status), so a reload afterwards
puts the app in the signed-in state. In dev the backend skips App Check, so no token is needed.

This proves the backend's domain check and the frontend's success rendering. It does NOT prove real
Google consent-screen behavior (hosted-domain restriction at Google's login page); that can't be
automated."""
import time

import firebase_admin
from firebase_admin import auth as fb_auth

from helpers.web.base_helper import BaseHelper
from helpers.web.quest_test_data import GOOGLE_DOMAIN_UID

QA_PROJECT = "randezvous-qa"

# Runs in the page. Reuses the app's own firebaseConfig (for the web API key) and apiClient (base URL,
# credentials, headers) so the session-login call is exactly what the real login flow sends.
_SIGN_IN_SCRIPT = """
const customToken = arguments[0];
const done = arguments[arguments.length - 1];
(async () => {
  try {
    const { auth } = await import('/src/config/firebaseConfig.js');
    const { request } = await import('/src/api/apiClient.js');
    const r = await fetch(
      'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=' + auth.config.apiKey,
      { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: customToken, returnSecureToken: true }) });
    const j = await r.json();
    if (!r.ok) throw new Error('custom-token exchange failed: ' + ((j.error && j.error.message) || r.status));
    const res = await request('/api/auth/session-login', { method: 'POST', body: { idToken: j.idToken } });
    done({ ok: true, uid: (res && res.user && res.user.uid) || null });
  } catch (e) {
    done({ ok: false, error: String((e && e.message) || e) });
  }
})();
"""


class GoogleIdentityHelper(BaseHelper):
    def sign_in(self, uid=GOOGLE_DOMAIN_UID):
        """Signs the current browser session in as `uid` and reloads. The driver must already be on the
        app's origin (any page of it). Raises RuntimeError if the bridge fails."""
        project = firebase_admin.get_app().project_id
        if project != QA_PROJECT:
            raise RuntimeError(f"Refusing to mint a custom token: Admin app is on '{project}', not '{QA_PROJECT}'.")

        custom_token = fb_auth.create_custom_token(uid).decode()
        self.driver.set_script_timeout(30)
        result = self.driver.execute_async_script(_SIGN_IN_SCRIPT, custom_token)
        if not result or not result.get("ok"):
            raise RuntimeError(f"Google-identity sign-in bridge failed: {result}")
        print(f"Signed in as fabricated Google user (session uid: {result.get('uid')})")
        self.driver.refresh()
        time.sleep(0.5)  # let the post-reload auth-status request start before callers look at the page
        return result
