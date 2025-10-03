#!/bin/bash
# Stop live trading

echo "🛑 Stopping AutoTrader Live Trading..."

# Kill live trading processes
pkill -f "lean live"

echo "✅ Live trading stopped!"
