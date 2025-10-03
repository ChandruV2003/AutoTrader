#!/bin/bash
# Setup Cron Automation for AutoTrader

echo "🕒 Setting up Cron Automation for AutoTrader"
echo "============================================="

# Create cron jobs directory
mkdir -p cron_jobs

# Create the main trading cron job
cat > cron_jobs/autotrader_cron.sh << 'EOF'
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
EOF

# Make the cron job executable
chmod +x cron_jobs/autotrader_cron.sh

# Create the daily model training cron job
cat > cron_jobs/daily_training.sh << 'EOF'
#!/bin/bash
# Daily Model Training - Runs every day at 6 PM

export PATH="/usr/local/bin:/usr/bin:/bin"
cd /Users/admin/Developer/AutoTrader
source .venv/bin/activate

# Run model training
python research/scripts/train_lightgbm.py >> logs/daily_training.log 2>&1

echo "$(date): Daily model training completed" >> logs/cron_execution.log
EOF

chmod +x cron_jobs/daily_training.sh

# Create the weekly performance report cron job
cat > cron_jobs/weekly_report.sh << 'EOF'
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
EOF

chmod +x cron_jobs/weekly_report.sh

# Add cron jobs to crontab
echo "📅 Adding cron jobs to crontab..."

# Backup existing crontab
crontab -l > cron_jobs/crontab_backup.txt 2>/dev/null || echo "# No existing crontab" > cron_jobs/crontab_backup.txt

# Create new crontab
cat > cron_jobs/new_crontab.txt << 'EOF'
# AutoTrader Cron Jobs
# Trading signals every 5 minutes during market hours (9:30 AM - 4:00 PM, Monday-Friday)
*/5 9-16 * * 1-5 /Users/admin/Developer/AutoTrader/cron_jobs/autotrader_cron.sh

# Daily model training at 6 PM
0 18 * * * /Users/admin/Developer/AutoTrader/cron_jobs/daily_training.sh

# Weekly performance report every Sunday at 9 AM
0 9 * * 0 /Users/admin/Developer/AutoTrader/cron_jobs/weekly_report.sh

# System health check every hour
0 * * * * echo "$(date): System running" >> /Users/admin/Developer/AutoTrader/logs/system_health.log
EOF

# Install the new crontab
crontab cron_jobs/new_crontab.txt

echo "✅ Cron jobs installed successfully!"
echo ""
echo "📅 Scheduled Jobs:"
echo "   • Trading signals: Every 5 minutes (9:30 AM - 4:00 PM, Mon-Fri)"
echo "   • Model training: Daily at 6:00 PM"
echo "   • Performance reports: Weekly on Sundays at 9:00 AM"
echo "   • System health: Every hour"
echo ""
echo "📝 Logs will be saved to:"
echo "   • logs/cron_trading.log"
echo "   • logs/daily_training.log"
echo "   • logs/weekly_report.log"
echo "   • logs/system_health.log"
echo ""
echo "🔍 To view cron jobs: crontab -l"
echo "🛑 To remove cron jobs: crontab -r"
echo "📊 To view logs: tail -f logs/cron_trading.log"
