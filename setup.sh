#!/usr/bin/env bash

echo "Starting environment setup..."

# 1. Ensure the virtual environment is created
echo "Creating virtual environment (.venv)..."
python3 -m venv .venv

# 2. Activate the environment
source .venv/bin/activate

# 3. Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# 4. Install required packages
echo "Installing test dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install pytest pytest-html selenium google-auth google-api-core firebase-admin appium-python-client python-dotenv piexif Pillow "urllib3<2"
fi

# 5. Create .env from the template if it doesn't exist yet
if [ ! -f ".env" ]; then
    echo "No .env found -- copying .env.example to .env."
    cp .env.example .env
    echo "Fill in .env before running tests (Firebase App Check token, WEB_APP_PATH for web tests, etc.)."
else
    echo ".env already exists -- leaving it alone."
fi

# 6. Warn about the Firebase service account key (can't be automated -- see README)
if [ ! -f "private/service-account-key-qa.json" ]; then
    echo "⚠️  private/service-account-key-qa.json not found."
    echo "   Get it from the randezvous-qa project: Firebase Console > Project Settings > Service Accounts > Generate new private key."
    echo "   (This suite only ever talks to randezvous-qa -- never save the prod key here.)"
fi

# 7. Check Node/npm are on PATH (needed to run rvsite's dev servers for web tests)
if ! command -v npm >/dev/null 2>&1; then
    echo "⚠️  npm not found on PATH -- web tests need Node.js installed to run rvsite's dev servers."
fi

# 8. Check the configured rvsite checkout actually exists (web tests only)
web_app_path=$(grep -m1 '^WEB_APP_PATH=' .env 2>/dev/null | cut -d= -f2- | tr -d '"')
web_app_path="${web_app_path:-../../RandezVousSite/rvsite}"
if [ ! -d "$web_app_path" ]; then
    echo "⚠️  rvsite checkout not found at '$web_app_path' (WEB_APP_PATH in .env) -- web tests need it there."
fi

# 9. Install rvsite's npm dependencies if they're missing (web tests start its dev servers)
if [ -d "$web_app_path" ] && command -v npm >/dev/null 2>&1; then
    for dir in "$web_app_path" "$web_app_path/backend"; do
        if [ -f "$dir/package.json" ] && [ ! -d "$dir/node_modules" ]; then
            echo "Installing npm dependencies in $dir..."
            (cd "$dir" && npm install) || echo "⚠️  npm install failed in $dir."
        fi
    done
fi

# 10. Android emulator tooling (SDK, adb, Google Play system image, AVD) for android_chrome_driver tests.
#     Several GB -- skip with: SKIP_ANDROID=1 ./setup.sh
if [ "${SKIP_ANDROID:-0}" = "1" ]; then
    echo "SKIP_ANDROID=1 -- skipping Android emulator setup."
else
    bash scripts/setup_android.sh || echo "⚠️  Android setup didn't finish -- Android tests won't run until it does (see messages above)."
fi

# 11. Remind about the Appium drivers (one-time, installed globally by Appium rather than into .venv)
if command -v appium >/dev/null 2>&1; then
    installed_drivers=$(appium driver list --installed 2>&1)
    echo "$installed_drivers" | grep -q "xcuitest" || echo "⚠️  Appium XCUITest driver missing -- run: appium driver install xcuitest"
    echo "$installed_drivers" | grep -q "uiautomator2" || echo "⚠️  Appium UiAutomator2 driver missing (Android tests) -- run: appium driver install uiautomator2"
else
    echo "⚠️  appium not found on PATH -- install it (npm install -g appium), then the xcuitest and uiautomator2 drivers."
fi

# 12. Web tests need their fixtures (quests + test accounts) in randezvous-qa. Seeding is per QA project, not
#     per clone, so just point at it when the key is present rather than writing to QA on every setup.
if [ -f "private/service-account-key-qa.json" ]; then
    echo "ℹ️  First time against this QA project (or after a data reset)? Seed the web fixtures:"
    echo "   python scripts/firebase/seed_qa_web_fixtures.py"
fi

echo "==============================================="
echo "Setup complete!"
echo "To start running tests, turn on your environment by running:"
echo "source .venv/bin/activate"
echo "==============================================="
