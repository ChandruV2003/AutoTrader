# Simple ML-Enhanced Trading Algorithm
from AlgorithmImports import *
import joblib
import numpy as np
from pathlib import Path

class SimpleMLTrading(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2015, 1, 1)
        self.SetCash(10_000)
        
        # Add SPY equity
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        
        # Technical indicators
        self.fast_sma = self.SMA(self.symbol, 20, Resolution.Daily)
        self.slow_sma = self.SMA(self.symbol, 50, Resolution.Daily)
        self.rsi = self.RSI(self.symbol, 14, MovingAverageType.Wilders)
        
        # Price history for feature calculation
        self.price_history = RollingWindow[TradeBar](100)
        
        # ML model loading
        self.model = None
        self.load_ml_model()
        
        self.SetWarmUp(50)
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        
    def load_ml_model(self):
        """Load the latest trained ML model"""
        try:
            possible_paths = [
                Path("research/models"),
                Path("../research/models"),
                Path("../../research/models"),
                Path("/Users/admin/Developer/AutoTrader/research/models")
            ]
            
            models_dir = None
            for path in possible_paths:
                if path.exists():
                    models_dir = path
                    break
                    
            if models_dir:
                model_files = list(models_dir.glob("lgb_spy_*.pkl"))
                if model_files:
                    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
                    self.model = joblib.load(latest_model)
                    self.Debug(f"Loaded ML model: {latest_model.name}")
                else:
                    self.Debug("No ML models found, using technical indicators only")
            else:
                self.Debug("Models directory not found, using technical indicators only")
        except Exception as e:
            self.Debug(f"Error loading ML model: {e}")
            self.model = None

    def calculate_simple_features(self, current_price: float) -> dict:
        """Calculate simple ML features"""
        if not self.price_history.IsReady:
            return None
            
        # Get recent prices
        recent_prices = []
        for i in range(self.price_history.Count):
            bar = self.price_history[i]
            if bar is not None and bar.Close is not None:
                recent_prices.append(bar.Close)
        
        if len(recent_prices) < 30:
            return None
        
        # Calculate basic features
        ret_5d = (current_price - recent_prices[-6]) / recent_prices[-6] if len(recent_prices) >= 6 else 0
        
        # Calculate volatility
        if len(recent_prices) >= 31:
            returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                      for i in range(1, len(recent_prices))]
            vol_30d = np.std(returns[-30:]) if len(returns) >= 30 else 0
        else:
            vol_30d = 0
            
        # Calculate momentum
        mom_20d = (current_price - recent_prices[-21]) / recent_prices[-21] if len(recent_prices) >= 21 else 0
        mom_120d = (current_price - recent_prices[-121]) / recent_prices[-121] if len(recent_prices) >= 121 else 0
        
        # Simple ATR approximation
        if len(recent_prices) >= 15:
            high_low_ranges = []
            for i in range(max(0, len(recent_prices)-15), len(recent_prices)):
                if i > 0:
                    high_low_ranges.append(abs(recent_prices[i] - recent_prices[i-1]))
            atr_14d = np.mean(high_low_ranges) if high_low_ranges else 0
        else:
            atr_14d = 0
        
        # Simple skewness
        if len(recent_prices) >= 31:
            returns = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                      for i in range(1, len(recent_prices))]
            if len(returns) >= 30 and np.std(returns[-30:]) > 0:
                mean_return = np.mean(returns[-30:])
                std_return = np.std(returns[-30:])
                skew_30d = np.mean([(r - mean_return)**3 for r in returns[-30:]]) / (std_return**3)
            else:
                skew_30d = 0
        else:
            skew_30d = 0
            
        return {
            'ret_5d': ret_5d,
            'vol_30d': vol_30d,
            'mom_20d': mom_20d,
            'mom_120d': mom_120d,
            'atr_14d': atr_14d,
            'skew_30d': skew_30d
        }

    def get_ml_prediction(self, features: dict) -> float:
        """Get ML model prediction"""
        if self.model is None:
            return 0.5  # Neutral if no model
            
        try:
            feature_array = np.array([[
                features['ret_5d'],
                features['vol_30d'], 
                features['mom_20d'],
                features['mom_120d'],
                features['atr_14d'],
                features['skew_30d']
            ]])
            
            prediction = self.model.predict(feature_array)[0]
            return prediction
        except Exception as e:
            self.Debug(f"ML prediction error: {e}")
            return 0.5

    def OnData(self, data: Slice):
        if self.IsWarmingUp or not data.ContainsKey(self.symbol):
            return
            
        # Get current bar
        current_bar = data[self.symbol]
        if current_bar is None or current_bar.Close is None:
            return
            
        # Add to price history
        self.price_history.Add(current_bar)
        
        if not self.price_history.IsReady:
            return
            
        # Calculate features
        features = self.calculate_simple_features(current_bar.Close)
        if features is None:
            return
            
        # Get ML prediction
        ml_signal = self.get_ml_prediction(features)
        
        # Technical signals
        sma_bullish = self.fast_sma.Current.Value > self.slow_sma.Current.Value
        rsi_oversold = self.rsi.Current.Value < 30
        rsi_overbought = self.rsi.Current.Value > 70
        
        # Trading logic
        should_buy = (ml_signal > 0.6 and sma_bullish) or (ml_signal > 0.55 and sma_bullish and rsi_oversold)
        should_sell = (ml_signal < 0.4) or (ml_signal < 0.45 and rsi_overbought)
        
        # Execute trades
        if should_buy and not self.Portfolio.Invested:
            self.SetHoldings(self.symbol, 1.0)
            self.Debug(f"BUY: ML={ml_signal:.3f}, SMA={sma_bullish}, RSI={self.rsi.Current.Value:.1f}")
            
        elif should_sell and self.Portfolio.Invested:
            self.Liquidate(self.symbol)
            self.Debug(f"SELL: ML={ml_signal:.3f}, RSI={self.rsi.Current.Value:.1f}")
