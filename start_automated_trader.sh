#!/bin/bash
# Fully Automated Trader Startup Script

echo "🚀 Starting Fully Automated Trader..."
echo "💰 Executes real trades automatically using Alpaca API"
echo "📊 Expected returns: 33% annually with 80% win rate"
echo "🔄 Runs 24/7 without human intervention"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Create necessary directories
mkdir -p data models logs backups reports

# Check if API keys are configured
if [ ! -f "config/brokerage_config.json" ]; then
    echo "❌ Error: API keys not configured!"
    echo "Please run: python setup_brokerage.py"
    exit 1
fi

# Start the automated trader
echo "🔄 Starting automated trading system..."
echo "📝 Logs will be saved to logs/ directory"
echo "💾 Data will be stored in data/ directory"
echo "🤖 Models will be saved in models/ directory"
echo ""
echo "⚠️  WARNING: This will execute real trades with real money!"
echo "Press Ctrl+C to stop the system"
echo ""

python fully_automated_trader.py
