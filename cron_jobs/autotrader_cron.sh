#!/bin/bash
# AutoTrader Cron Job - Runs every 5 minutes during market hours

# Set environment variables
export PATH="/usr/local/bin:/usr/bin:/bin"
cd /Users/admin/Developer/AutoTrader

# Activate virtual environment
source .venv/bin/activate

# Run the trading signal generator
python simple_signals.py >> logs/cron_trading.log 2>&1

# Log the run
echo "$(date): AutoTrader cron job executed" >> logs/cron_execution.log
