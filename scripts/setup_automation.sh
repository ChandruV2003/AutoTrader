#!/bin/bash
# AutoTrader Automation Setup Script

echo "🚀 Setting up AutoTrader automation..."

# Create cron jobs for automated trading
echo "📅 Setting up daily automation..."

# Daily model training and backtesting
(crontab -l 2>/dev/null; echo "0 6 * * * cd /Users/admin/Developer/AutoTrader && /Users/admin/Developer/AutoTrader/.venv/bin/python research/scripts/train_lightgbm.py >> logs/training.log 2>&1") | crontab -

# Daily crypto model training
(crontab -l 2>/dev/null; echo "0 7 * * * cd /Users/admin/Developer/AutoTrader && /Users/admin/Developer/AutoTrader/.venv/bin/python research/scripts/train_crypto_lightgbm.py >> logs/crypto_training.log 2>&1") | crontab -

# Daily backtesting and model promotion
(crontab -l 2>/dev/null; echo "0 8 * * * cd /Users/admin/Developer/AutoTrader && ./scripts/run_pipeline.sh >> logs/pipeline.log 2>&1") | crontab -

# Live trading (only if you want it to run automatically)
# (crontab -l 2>/dev/null; echo "0 9 * * 1-5 cd /Users/admin/Developer/AutoTrader && lean live WorkingTrading --brokerage alpaca >> logs/live_trading.log 2>&1") | crontab -

# Create logs directory
mkdir -p logs

# Create monitoring script
cat > scripts/monitor_system.sh << 'EOF'
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
EOF

chmod +x scripts/monitor_system.sh

# Create startup script
cat > scripts/start_trading.sh << 'EOF'
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
EOF

chmod +x scripts/start_trading.sh

# Create stop script
cat > scripts/stop_trading.sh << 'EOF'
#!/bin/bash
# Stop live trading

echo "🛑 Stopping AutoTrader Live Trading..."

# Kill live trading processes
pkill -f "lean live"

echo "✅ Live trading stopped!"
EOF

chmod +x scripts/stop_trading.sh

echo "✅ Automation setup complete!"
echo ""
echo "📋 What was set up:"
echo "  • Daily model training (6 AM)"
echo "  • Daily crypto training (7 AM)" 
echo "  • Daily backtesting (8 AM)"
echo "  • System monitoring script"
echo "  • Start/stop trading scripts"
echo ""
echo "🎮 Commands to use:"
echo "  • Start trading: ./scripts/start_trading.sh"
echo "  • Stop trading: ./scripts/stop_trading.sh"
echo "  • Monitor system: ./scripts/monitor_system.sh"
echo "  • View cron jobs: crontab -l"
echo ""
echo "⚠️  IMPORTANT: Test with paper trading first!"
echo "   Run: lean live WorkingTrading --brokerage paper"
