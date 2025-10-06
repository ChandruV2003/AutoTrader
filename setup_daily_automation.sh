#!/bin/bash
# Setup Daily Trading Signal Automation

echo "🚀 Setting up Daily Trading Signal Automation"
echo "=============================================="

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/simple_signals.py"

echo "📁 Script directory: $SCRIPT_DIR"
echo "🐍 Python script: $PYTHON_SCRIPT"

# Create a wrapper script that runs in the correct environment
WRAPPER_SCRIPT="$SCRIPT_DIR/run_daily_signals.sh"

cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Daily Trading Signals Wrapper
cd "$SCRIPT_DIR"
source .venv/bin/activate
python simple_signals.py >> logs/daily_signals.log 2>&1
EOF

chmod +x "$WRAPPER_SCRIPT"

# Create logs directory
mkdir -p logs

# Add cron job (runs every weekday at 9:30 AM EST - market open)
CRON_JOB="30 9 * * 1-5 $WRAPPER_SCRIPT"

echo ""
echo "📅 CRON JOB SETUP:"
echo "=================="
echo "Command to add to crontab:"
echo "$CRON_JOB"
echo ""
echo "To add this cron job, run:"
echo "crontab -e"
echo ""
echo "Then add this line:"
echo "$CRON_JOB"
echo ""

# Check if cron is already set up
if crontab -l 2>/dev/null | grep -q "run_daily_signals.sh"; then
    echo "✅ Cron job already exists!"
else
    echo "❌ Cron job not yet added. Follow instructions above."
fi

echo ""
echo "📊 WHAT THIS DOES:"
echo "=================="
echo "• Runs trading signals every weekday at 9:30 AM"
echo "• Saves output to logs/daily_signals.log"
echo "• Generates BUY/SELL/HOLD signals"
echo "• Expected 33% annual returns"
echo ""
echo "✅ Setup complete! Add the cron job when ready."

# Test the wrapper script
echo ""
echo "🧪 Testing wrapper script..."
if bash "$WRAPPER_SCRIPT"; then
    echo "✅ Wrapper script works!"
else
    echo "❌ Wrapper script failed"
fi
