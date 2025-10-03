#!/usr/bin/env python3
"""
Daily-bar LightGBM model:
  • features: 5-day return + 30-day volatility
  • label   : 1 if price in 5 sessions is higher, else 0
"""

import datetime as dt
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import yfinance as yf


def fetch_data(ticker: str = "SPY",
               start: str = "1993-01-29") -> pd.DataFrame:
    df = yf.download(ticker, start=start, interval="1d", auto_adjust=True)
    df.rename(columns=str.lower, inplace=True)

    # ── flatten possible MultiIndex → "close", "high", … ──
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    price_col = "close" if "close" in df.columns else "adj close"
    if price_col not in df.columns:
        raise KeyError("Could not find a price column")
    df = df.copy()                                  # avoid SettingWithCopy
    # ── basic returns & volatility ───────────────────────────────────────
    df["ret_1d"]   = df[price_col].pct_change()
    df["ret_5d"]   = df[price_col].pct_change(5)
    df["vol_30d"]  = df["ret_1d"].rolling(30).std()
    # ── engineered features ─────────────────────────────────────────────
    df["mom_20d"]  = df[price_col].pct_change(20)
    df["mom_120d"] = df[price_col].pct_change(120)
    df["atr_14d"]  = (df["high"] - df["low"]).rolling(14).mean()
    df["skew_30d"] = df["ret_1d"].rolling(30).skew()
    # ── binary label ────────────────────────────────────────────────────
    df["target"]   = (df[price_col].shift(-5) > df[price_col]).astype(int)
    df.dropna(subset=["ret_5d", "vol_30d", "mom_20d", "mom_120d", "atr_14d", "skew_30d", "target"], inplace=True)
    return df


def train(df: pd.DataFrame) -> lgb.Booster:
    X = df[["ret_5d","vol_30d","mom_20d","mom_120d","atr_14d","skew_30d"]].values
    y = df["target"].values
    FEATURES=["ret_5d","vol_30d","mom_20d","mom_120d","atr_14d","skew_30d"]
    dtrain = lgb.Dataset(X, label=y, feature_name=FEATURES)
    return lgb.train(
        dict(objective="binary",
             learning_rate=0.05,
             num_leaves=31,
             metric=["binary_logloss", "auc"],
             verbose=-1),
        dtrain, num_boost_round=400
    )


def main() -> None:
    df    = build_features(fetch_data())
    model = train(df)

    out = Path(__file__).resolve().parent.parent / "models"
    out.mkdir(parents=True, exist_ok=True)
    fname = out / f"lgb_spy_{dt.date.today():%Y-%m-%d}.pkl"
    joblib.dump(model, fname)
    print(f"✔ saved → {fname}")


if __name__ == "__main__":
    main()
