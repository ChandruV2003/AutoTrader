#!/bin/bash
# Start the Browser Auto Trader

echo "🌐 Starting Browser Auto Trader..."
echo "🤖 Fully automatic trading using browser automation"
echo "📊 Works with Robinhood, Webull, and other brokers"
echo "🔄 Integrates with Master Orchestrator signals"
echo ""

# Ensure the virtual environment is activated
source .venv/bin/activate

# Install required packages if not already installed
pip install selenium webdriver-manager > /dev/null 2>&1

echo "🚀 Starting Browser Auto Trader in the background..."
echo "📝 Logs will be saved to logs/ directory"
echo "💾 Trade instructions will be saved to signals/ directory"
echo ""

# Run the Browser Auto Trader in the background
python browser_auto_trader.py &

# Get the process ID
PID=$!

echo "✅ Browser Auto Trader started with PID: $PID"
echo "📋 To stop it, run: kill $PID"
echo "📋 To check status, run: ps aux | grep browser_auto_trader"
echo "📋 To view logs, run: tail -f logs/browser_trader_$(date +%Y%m%d).log"
echo ""
echo "🎯 The system will:"
echo "   • Get trading signals from Master Orchestrator"
echo "   • Execute trades automatically via browser automation"
echo "   • Fall back to manual instructions if automation fails"
echo "   • Work with Robinhood, Webull, and other brokers"
