#!/usr/bin/env python3
"""
Crypto-focused LightGBM model:
  • features: 5-day return + 30-day volatility + momentum + ATR + skewness
  • label   : 1 if price in 5 sessions is higher, else 0
  • data    : BTC and ETH price data
"""

import datetime as dt
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import yfinance as yf


def fetch_crypto_data(tickers: list = ["BTC-USD", "ETH-USD"],
                     start: str = "2020-01-01") -> pd.DataFrame:
    """Fetch crypto data and combine into single dataset"""
    all_data = []
    
    for ticker in tickers:
        df = yf.download(ticker, start=start, interval="1d", auto_adjust=True)
        df.rename(columns=str.lower, inplace=True)
        
        # Flatten possible MultiIndex
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        
        # Add ticker identifier
        df['ticker'] = ticker.replace('-USD', '')
        
        all_data.append(df)
    
    # Combine all crypto data
    combined_df = pd.concat(all_data, ignore_index=False)
    return combined_df


def build_crypto_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build features for crypto trading"""
    df = df.copy()
    
    # Group by ticker to calculate features per crypto
    result_dfs = []
    
    for ticker in df['ticker'].unique():
        ticker_df = df[df['ticker'] == ticker].copy()
        
        # Basic returns & volatility
        ticker_df["ret_1d"] = ticker_df["close"].pct_change()
        ticker_df["ret_5d"] = ticker_df["close"].pct_change(5)
        ticker_df["vol_30d"] = ticker_df["ret_1d"].rolling(30).std()
        
        # Engineered features
        ticker_df["mom_20d"] = ticker_df["close"].pct_change(20)
        ticker_df["mom_120d"] = ticker_df["close"].pct_change(120)
        ticker_df["atr_14d"] = (ticker_df["high"] - ticker_df["low"]).rolling(14).mean()
        ticker_df["skew_30d"] = ticker_df["ret_1d"].rolling(30).skew()
        
        # Crypto-specific features
        ticker_df["volume_ma_20"] = ticker_df["volume"].rolling(20).mean()
        ticker_df["volume_ratio"] = ticker_df["volume"] / ticker_df["volume_ma_20"]
        
        # Binary label
        ticker_df["target"] = (ticker_df["close"].shift(-5) > ticker_df["close"]).astype(int)
        
        # Drop rows with missing values
        ticker_df.dropna(subset=["ret_5d", "vol_30d", "mom_20d", "mom_120d", "atr_14d", "skew_30d", "target"], inplace=True)
        
        result_dfs.append(ticker_df)
    
    # Combine all tickers back together
    final_df = pd.concat(result_dfs, ignore_index=False)
    return final_df


def train_crypto_model(df: pd.DataFrame) -> lgb.Booster:
    """Train LightGBM model on crypto data"""
    # Use the same features as stock model but add volume features
    feature_cols = ["ret_5d", "vol_30d", "mom_20d", "mom_120d", "atr_14d", "skew_30d"]
    
    X = df[feature_cols].values
    y = df["target"].values
    
    dtrain = lgb.Dataset(X, label=y, feature_name=feature_cols)
    
    return lgb.train(
        dict(objective="binary",
             learning_rate=0.05,
             num_leaves=31,
             metric=["binary_logloss", "auc"],
             verbose=-1),
        dtrain, num_boost_round=400
    )


def main() -> None:
    """Main training pipeline for crypto models"""
    print("Fetching crypto data...")
    df = fetch_crypto_data()
    
    print("Building features...")
    df_features = build_crypto_features(df)
    
    print("Training model...")
    model = train_crypto_model(df_features)

    # Save model
    out = Path(__file__).resolve().parent.parent / "models"
    out.mkdir(parents=True, exist_ok=True)
    fname = out / f"lgb_crypto_{dt.date.today():%Y-%m-%d}.pkl"
    joblib.dump(model, fname)
    print(f"✔ saved → {fname}")
    
    # Calculate and save AUC score
    feature_cols = ["ret_5d", "vol_30d", "mom_20d", "mom_120d", "atr_14d", "skew_30d"]
    X = df_features[feature_cols].values
    y = df_features["target"].values
    predictions = model.predict(X)
    
    from sklearn.metrics import roc_auc_score
    auc_score = roc_auc_score(y, predictions)
    
    # Save AUC score for pipeline script
    auc_file = Path(__file__).resolve().parent.parent.parent / "latest_crypto_auc.txt"
    with open(auc_file, 'w') as f:
        f.write(str(auc_score))
    
    print(f"✔ Crypto AUC Score: {auc_score:.6f}")
    print(f"✔ AUC saved → {auc_file}")


if __name__ == "__main__":
    main()
