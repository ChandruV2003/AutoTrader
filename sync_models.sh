#!/bin/bash
# Auto-sync ML models and performance metrics between computers
# Run this every 6 hours on the training computer (M1 MacBook)

cd "$(dirname "$0")" || exit 1

echo "🔄 $(date): AutoTrader Model Sync Starting..."

# Pull latest changes first
git pull origin main --rebase

# Add trained models
git add research/models/*.pkl 2>/dev/null
git add latest_auc.txt 2>/dev/null
git add logs/training.log 2>/dev/null

# Check if there are changes
if git diff --staged --quiet; then
    echo "✅ No new models to sync"
    exit 0
fi

# Get current AUC score
AUC_SCORE=$(cat latest_auc.txt 2>/dev/null | head -1)
DATE=$(date +"%Y-%m-%d %H:%M")

# Commit and push
git commit -m "🤖 Auto-sync: Models $DATE (AUC: $AUC_SCORE)"
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully synced models to Git"
    echo "   AUC Score: $AUC_SCORE"
    echo "   Time: $DATE"
else
    echo "❌ Failed to push models to Git"
    exit 1
fi

