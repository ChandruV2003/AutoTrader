#!/bin/bash
# System monitoring script

echo "🔍 AutoTrader System Status - $(date)"
echo "=================================="

# Check if models are being updated
echo "📊 Latest Model Training:"
ls -la research/models/ | tail -5

# Check latest AUC scores
echo "🎯 Latest Performance:"
if [ -f latest_auc.txt ]; then
    echo "Stock AUC: $(cat latest_auc.txt)"
fi
if [ -f latest_crypto_auc.txt ]; then
    echo "Crypto AUC: $(cat latest_crypto_auc.txt)"
fi

# Check system resources
echo "💻 System Resources:"
echo "CPU Usage: $(top -l 1 | grep "CPU usage" | awk '{print $3}')"
echo "Memory Usage: $(top -l 1 | grep "PhysMem" | awk '{print $2}')"

# Check if trading is running
echo "📈 Trading Status:"
if pgrep -f "lean live" > /dev/null; then
    echo "✅ Live trading is running"
else
    echo "❌ Live trading is not running"
fi

echo "=================================="
