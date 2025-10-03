#!/bin/bash
# Start the Ultimate Free Trader

echo "💰 Starting Ultimate Free Trader..."
echo "🆓 100% FREE trading system with zero costs"
echo "📊 Works with free brokers (Robinhood, Webull)"
echo "🤖 Browser automation for automatic execution"
echo "🧠 Master Orchestrator for intelligent signals"
echo ""

# Ensure the virtual environment is activated
source .venv/bin/activate

# Install required packages if not already installed
echo "📦 Installing required packages..."
pip install selenium webdriver-manager requests scikit-learn joblib > /dev/null 2>&1

# Check if Chrome is installed
if ! command -v google-chrome &> /dev/null && ! command -v chrome &> /dev/null; then
    echo "⚠️ Chrome browser not found. Installing..."
    echo "💡 Run: brew install --cask google-chrome"
fi

# Check if ChromeDriver is installed
if ! command -v chromedriver &> /dev/null; then
    echo "⚠️ ChromeDriver not found. Installing..."
    echo "💡 Run: brew install chromedriver"
fi

# Create necessary directories
mkdir -p logs data models signals reports browser_screenshots

echo "🚀 Starting Ultimate Free Trader in the background..."
echo "📝 Logs will be saved to logs/ directory"
echo "💾 Data will be stored in data/ directory"
echo "🤖 Models will be saved in models/ directory"
echo "📊 Reports will be saved to reports/ directory"
echo "📸 Screenshots will be saved to browser_screenshots/ directory"
echo ""

# Run the Ultimate Free Trader in the background
python ultimate_free_trader.py &

# Get the process ID
PID=$!

echo "✅ Ultimate Free Trader started with PID: $PID"
echo "📋 To stop it, run: kill $PID"
echo "📋 To check status, run: ps aux | grep ultimate_free_trader"
echo "📋 To view logs, run: tail -f logs/ultimate_free_trader_$(date +%Y%m%d).log"
echo ""
echo "🎯 The system will:"
echo "   • Start the Master Orchestrator (the brain)"
echo "   • Set up browser automation"
echo "   • Generate trading signals continuously"
echo "   • Execute trades automatically via browser"
echo "   • Fall back to manual instructions if needed"
echo "   • Work with free brokers (Robinhood, Webull)"
echo "   • Cost you ZERO dollars!"
echo ""
echo "💡 To set up broker login (optional):"
echo "   1. The system will save trade instructions"
echo "   2. You can execute them manually"
echo "   3. Or set up browser automation for full automation"
echo ""
echo "🆓 Your FREE money-making machine is now running!"
