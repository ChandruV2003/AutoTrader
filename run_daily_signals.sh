#!/bin/bash
# Daily Trading Signals Wrapper
cd "/Users/admin/Developer/AutoTrader"
source .venv/bin/activate
python simple_signals.py >> logs/daily_signals.log 2>&1
