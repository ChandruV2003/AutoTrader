#!/bin/bash
# Fully Automatic Trader Startup Script

echo "🚀 Starting Fully Automatic Trader..."
echo "🤖 Executes trades automatically using browser automation"
echo "💰 100% automated background money maker"
echo "📊 No manual intervention required"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Install required packages for browser automation
echo "📦 Installing browser automation dependencies..."
pip install selenium pyautogui

# Create necessary directories
mkdir -p data models logs backups reports trade_screenshots

# Check if Chrome is installed
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️  Chrome browser not found. Installing Chrome..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install --cask google-chrome
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    fi
fi

# Download ChromeDriver
echo "📥 Downloading ChromeDriver..."
pip install webdriver-manager

# Start the fully automatic trader
echo "🔄 Starting fully automatic trading system..."
echo "📝 Logs will be saved to logs/ directory"
echo "💾 Data will be stored in data/ directory"
echo "🤖 Models will be saved in models/ directory"
echo "📸 Trade screenshots will be saved to trade_screenshots/ directory"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Make sure you're logged into Webull or Robinhood in your browser"
echo "   - The system will automatically execute trades based on signals"
echo "   - All trades will be logged and screenshots will be taken"
echo "   - This will execute real trades with real money!"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

python fully_automatic_trader.py
