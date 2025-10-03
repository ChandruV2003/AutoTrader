#!/bin/bash
# Start live trading

echo "🚀 Starting AutoTrader Live Trading..."

# Check if already running
if pgrep -f "lean live" > /dev/null; then
    echo "❌ Trading is already running!"
    exit 1
fi

# Start live trading in background
cd /Users/admin/Developer/AutoTrader
nohup lean live WorkingTrading --brokerage alpaca > logs/live_trading.log 2>&1 &

echo "✅ Live trading started!"
echo "📊 Monitor with: ./scripts/monitor_system.sh"
echo "📝 Logs: tail -f logs/live_trading.log"
