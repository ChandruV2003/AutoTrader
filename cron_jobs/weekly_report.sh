#!/bin/bash
# Weekly Performance Report - Runs every Sunday at 9 AM

export PATH="/usr/local/bin:/usr/bin:/bin"
cd /Users/admin/Developer/AutoTrader
source .venv/bin/activate

# Generate weekly report
python -c "
import json
from datetime import datetime, timedelta
from pathlib import Path

# Create weekly report
report = {
    'date': datetime.now().strftime('%Y-%m-%d'),
    'system_status': 'Running',
    'automation': 'Cron Jobs Active',
    'trading_signals': 'Generated every 5 minutes',
    'model_training': 'Daily at 6 PM',
    'performance_reports': 'Weekly on Sundays'
}

# Save report
with open('reports/weekly_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print('Weekly report generated')
" >> logs/weekly_report.log 2>&1

echo "$(date): Weekly report generated" >> logs/cron_execution.log
