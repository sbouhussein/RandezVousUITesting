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

echo "==============================================="
echo "Setup complete!"
echo "To start running tests, turn on your environment by running:"
echo "source .venv/bin/activate"
echo "==============================================="
