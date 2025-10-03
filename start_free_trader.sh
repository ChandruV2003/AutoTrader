#!/bin/bash
# Free Automated Trader Startup Script

echo "🚀 Starting Free Automated Trader..."
echo "💰 100% FREE - No API keys required!"
echo "📊 Generates trading signals automatically"
echo "💼 Tracks virtual portfolio performance"
echo "📋 Creates trade instructions for manual execution"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Create necessary directories
mkdir -p data models logs backups reports trade_instructions

# Start the free automated trader
echo "🔄 Starting automated trading system..."
echo "📝 Logs will be saved to logs/ directory"
echo "💾 Data will be stored in data/ directory"
echo "🤖 Models will be saved in models/ directory"
echo "📋 Trade instructions will be saved to trade_instructions/ directory"
echo ""
echo "💡 This system will:"
echo "   1. Generate trading signals every 5 minutes"
echo "   2. Create trade instruction files for manual execution"
echo "   3. Track virtual portfolio performance"
echo "   4. Learn and improve over time"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

python free_automated_trader.py
