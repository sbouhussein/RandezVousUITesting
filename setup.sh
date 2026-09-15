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
if [ ! -f "private/service-account-key.json" ]; then
    echo "⚠️  private/service-account-key.json not found."
    echo "   Get it from Firebase Console > Project Settings > Service Accounts > Generate new private key."
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

echo "==============================================="
echo "Setup complete!"
echo "To start running tests, turn on your environment by running:"
echo "source .venv/bin/activate"
echo "==============================================="
