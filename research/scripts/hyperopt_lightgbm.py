#!/usr/bin/env python3
"""
Optuna tuner for the daily-bar LightGBM model.

Run:  python Research/scripts/hyperopt_lightgbm.py --trials 75
"""

import argparse, datetime as dt, joblib, optuna
from pathlib import Path
import lightgbm as lgb

from train_lightgbm import fetch_data, build_features


# ── helpers ────────────────────────────────────────────────────────────────
def _split() -> tuple[lgb.Dataset, lgb.Dataset]:
    df = build_features(fetch_data())
    cut = int(len(df) * 0.7)
    X, y = df[["ret_5d", "vol_30d", "mom_20d", "mom_120d", "atr_14d", "skew_30d"]].values, df["target"].values
    return (
        lgb.Dataset(X[:cut],  label=y[:cut]),
        lgb.Dataset(X[cut:], label=y[cut:]),
    )


def _objective(trial: optuna.trial.Trial) -> float:
    dtrain, dvalid = _split()
    params = {
        "objective":     "binary",
        "metric":        "auc",
        "learning_rate": trial.suggest_float("lr", 0.01, 0.2, log=True),
        "num_leaves":    trial.suggest_int("nl", 15, 127),
        "min_child_samples": trial.suggest_int("mcs", 5, 50),
        "verbose":       -1,
    }
    booster = lgb.train(
        params,
        dtrain,
        num_boost_round=500,
        valid_sets=[dvalid],
        callbacks=[lgb.early_stopping(50, verbose=False)],
    )
    return booster.best_score["valid_0"]["auc"]


def main(trials: int) -> None:
    study = optuna.create_study(direction="maximize")
    study.optimize(_objective, n_trials=trials)
    print("Best params:", study.best_params)
    print("Best  AUC  :", study.best_value)

    # retrain on full set with best params
    df = build_features(fetch_data())
    FEATURES=["ret_5d","vol_30d","mom_20d","mom_120d","atr_14d","skew_30d"]
    dtrain = lgb.Dataset(df[["ret_5d", "vol_30d", "mom_20d", "mom_120d", "atr_14d", "skew_30d"]].values, label=df["target"].values)
    best = study.best_params | {"objective": "binary", "metric": "auc", "verbose": -1}
    booster = lgb.train(best, dtrain, num_boost_round=600)

    out = Path(__file__).resolve().parent.parent / "models"
    out.mkdir(exist_ok=True)
    fname = out / f"lgb_spy_optuna_{dt.date.today():%Y-%m-%d}.pkl"
    joblib.dump(booster, fname)
    Path("latest_auc.txt").write_text(str(study.best_value))
    print("Model saved →", fname)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--trials", type=int, default=50)
    main(p.parse_args().trials)
