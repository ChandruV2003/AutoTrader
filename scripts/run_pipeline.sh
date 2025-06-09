#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
LEAN="$(command -v lean)"

# make Lean happy even under cron / Colima
export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"
export TMPDIR="$HOME/.lean/tmp"
mkdir -p "$TMPDIR"

cd "$ROOT"

echo "[time] $(date "+%F %T")  —  training model"
"$PY" Research/scripts/train_lightgbm.py

echo "[time] $(date "+%F %T")  —  back-testing"
"$LEAN" backtest BaselineSMA --output pipeline_last.json

SUMMARY=$(find pipeline_last.json -maxdepth 1 -name '*-summary.json' | head -n 1)

NEW_AUC=$(cat latest_auc.txt 2>/dev/null || echo null)
OLD_AUC=-999

if [[ -f "$SUMMARY" ]]; then
    NEW=$(jq -r '.Statistics["Sharpe Ratio"] // .statistics["Sharpe Ratio"] // ."Sharpe Ratio"' "$SUMMARY")
NEW_AUC=$(cat latest_auc.txt 2>/dev/null || echo null)
    OLD=$(cat previous_sharpe.txt 2>/dev/null || echo -999)
    OLD_AUC=$(cat previous_auc.txt 2>/dev/null || echo -999)

    echo "[time] $(date "+%F %T")  —  Sharpe $NEW (prev $OLD) | AUC $NEW_AUC (prev $OLD_AUC)"

    if (( $(echo "$NEW > $OLD" | bc -l) )) && \
       (( $(echo "$NEW_AUC > $OLD_AUC + 0.01" | bc -l) )); then
        echo "$NEW"     > previous_sharpe.txt
        echo "$NEW_AUC" > previous_auc.txt
        git add Research/models previous_sharpe.txt previous_auc.txt
        git commit -m "Auto-promote model (Sharpe $NEW, AUC $NEW_AUC)"
        git push origin main
        echo "[time] $(date "+%F %T")  —  🚀 promoted improved model"
    fi
else
    echo "[time] $(date "+%F %T")  —  summary JSON not found — no promotion"
fi
