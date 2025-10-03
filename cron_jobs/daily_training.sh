#!/bin/bash
# Daily Model Training - Runs every day at 6 PM

export PATH="/usr/local/bin:/usr/bin:/bin"
cd /Users/admin/Developer/AutoTrader
source .venv/bin/activate

# Run model training
python research/scripts/train_lightgbm.py >> logs/daily_training.log 2>&1

echo "$(date): Daily model training completed" >> logs/cron_execution.log
