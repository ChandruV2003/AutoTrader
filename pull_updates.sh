#!/bin/bash
# Pull latest updates from Git (code, models, configs)
# Run this hourly on the trading server (Mac Mini)

cd "$(dirname "$0")" || exit 1

echo "⬇️  $(date): Pulling latest AutoTrader updates..."

# Stash any local changes (shouldn't happen on trading server)
git stash

# Pull latest
git pull origin main --rebase

if [ $? -eq 0 ]; then
    echo "✅ Successfully pulled latest updates"
    
    # Check for new models
    LATEST_MODEL=$(ls -t research/models/*.pkl 2>/dev/null | head -1)
    if [ -n "$LATEST_MODEL" ]; then
        echo "   Latest model: $(basename $LATEST_MODEL)"
    fi
    
    # Check AUC score
    if [ -f "latest_auc.txt" ]; then
        AUC=$(cat latest_auc.txt | head -1)
        echo "   Model accuracy: $AUC ($(echo "$AUC * 100" | bc -l | cut -c1-5)%)"
    fi
else
    echo "❌ Failed to pull updates from Git"
    exit 1
fi

# Pop stash if there was one
git stash pop 2>/dev/null

echo "✅ Pull complete at $(date)"

