```bash
#!/bin/bash
echo "Starting System Setup..."

echo "1/4: Installing NVM..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

echo "2/4: Installing Node.js v24..."
nvm install 24

echo "3/4: Installing Appium Server..."
npm install -g appium@latest

echo "4/4: Installing Python Dependencies..."
pip install -r requirements.txt

echo "Setup Complete!"