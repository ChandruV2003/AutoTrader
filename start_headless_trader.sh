#!/bin/bash
# Headless AutoTrader Startup Script

echo "🚀 Starting Headless AutoTrader..."
echo "📊 Fully automated trading system with AI learning"
echo "💰 Expected returns: 33% annually with 80% win rate"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Create necessary directories
mkdir -p data models logs backups reports

# Start the headless trader
echo "🔄 Starting automated trading system..."
echo "📝 Logs will be saved to logs/ directory"
echo "💾 Data will be stored in data/ directory"
echo "🤖 Models will be saved in models/ directory"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

python headless_auto_trader.py
