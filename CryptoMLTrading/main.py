# ML-Enhanced Crypto Trading Algorithm
from AlgorithmImports import *
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

class CryptoMLTrading(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetCash(10_000)
        
        # Add crypto symbols (BTC and ETH)
        self.btc = self.AddCrypto("BTCUSD", Resolution.Hour).Symbol
        self.eth = self.AddCrypto("ETHUSD", Resolution.Hour).Symbol
        
        # Technical indicators for both crypto
        self.setup_indicators(self.btc)
        self.setup_indicators(self.eth)
        
        # ML model loading
        self.model = None
        self.load_ml_model()
        
        self.SetWarmUp(200)
        self.SetBrokerageModel(BrokerageName.BinanceBrokerage, AccountType.Cash)
        
        # Portfolio allocation (50% BTC, 50% ETH)
        self.btc_allocation = 0.5
        self.eth_allocation = 0.5
        
    def setup_indicators(self, symbol):
        """Setup technical indicators for a symbol"""
        # Create attribute names dynamically
        symbol_str = str(symbol).replace("USD", "").lower()
        
        setattr(self, f"{symbol_str}_fast_sma", self.SMA(symbol, 20, Resolution.Hour))
        setattr(self, f"{symbol_str}_slow_sma", self.SMA(symbol, 50, Resolution.Hour))
        setattr(self, f"{symbol_str}_rsi", self.RSI(symbol, 14, MovingAverageType.Wilders))
        setattr(self, f"{symbol_str}_macd", self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Hour))
        setattr(self, f"{symbol_str}_atr", self.ATR(symbol, 14, MovingAverageType.Simple))
        setattr(self, f"{symbol_str}_price_history", RollingWindow[TradeBar](200))
        
    def load_ml_model(self):
        """Load the latest trained ML model"""
        try:
            models_dir = Path("research/models")
            if models_dir.exists():
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

    def calculate_features(self, symbol, current_price: float) -> dict:
        """Calculate ML features from current market data"""
        symbol_str = str(symbol).replace("USD", "").lower()
        price_history = getattr(self, f"{symbol_str}_price_history")
        
        if not price_history.IsReady:
            return None
            
        # Get recent prices for calculations
        recent_prices = [bar.Close for bar in price_history]
        
        # Calculate returns
        ret_1d = (current_price - recent_prices[-2]) / recent_prices[-2] if len(recent_prices) >= 2 else 0
        ret_5d = (current_price - recent_prices[-6]) / recent_prices[-6] if len(recent_prices) >= 6 else 0
        
        # Calculate volatility (30-day rolling std of 1-day returns)
        if len(recent_prices) >= 31:
            returns_1d = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                         for i in range(1, len(recent_prices))]
            vol_30d = np.std(returns_1d[-30:]) if len(returns_1d) >= 30 else 0
        else:
            vol_30d = 0
            
        # Calculate momentum
        mom_20d = (current_price - recent_prices[-21]) / recent_prices[-21] if len(recent_prices) >= 21 else 0
        mom_120d = (current_price - recent_prices[-121]) / recent_prices[-121] if len(recent_prices) >= 121 else 0
        
        # ATR (using indicator value)
        atr_indicator = getattr(self, f"{symbol_str}_atr")
        atr_14d = atr_indicator.Current.Value if atr_indicator.IsReady else 0
        
        # Calculate skewness (30-day rolling)
        if len(recent_prices) >= 31:
            returns_1d = [(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                         for i in range(1, len(recent_prices))]
            skew_30d = np.mean([(r - np.mean(returns_1d[-30:]))**3 for r in returns_1d[-30:]]) / (np.std(returns_1d[-30:])**3) if len(returns_1d) >= 30 and np.std(returns_1d[-30:]) > 0 else 0
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
        """Get ML model prediction for buy/sell signal"""
        if self.model is None:
            return 0.5  # Neutral if no model
            
        try:
            # Convert features to array in correct order
            feature_array = np.array([[
                features['ret_5d'],
                features['vol_30d'], 
                features['mom_20d'],
                features['mom_120d'],
                features['atr_14d'],
                features['skew_30d']
            ]])
            
            # Get prediction probability
            prediction = self.model.predict(feature_array)[0]
            return prediction
        except Exception as e:
            self.Debug(f"ML prediction error: {e}")
            return 0.5

    def get_technical_signals(self, symbol):
        """Get technical analysis signals for a symbol"""
        symbol_str = str(symbol).replace("USD", "").lower()
        
        fast_sma = getattr(self, f"{symbol_str}_fast_sma")
        slow_sma = getattr(self, f"{symbol_str}_slow_sma")
        rsi = getattr(self, f"{symbol_str}_rsi")
        macd = getattr(self, f"{symbol_str}_macd")
        
        sma_bullish = fast_sma.Current.Value > slow_sma.Current.Value
        rsi_oversold = rsi.Current.Value < 30
        rsi_overbought = rsi.Current.Value > 70
        macd_bullish = macd.Current.Value > macd.Signal.Current.Value
        
        return {
            'sma_bullish': sma_bullish,
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought,
            'macd_bullish': macd_bullish,
            'rsi_value': rsi.Current.Value
        }

    def OnData(self, data: Slice):
        if self.IsWarmingUp:
            return
            
        # Process both BTC and ETH
        for symbol in [self.btc, self.eth]:
            if not data.ContainsKey(symbol):
                continue
                
            symbol_str = str(symbol).replace("USD", "").lower()
            
            # Add current bar to price history
            current_bar = data[symbol]
            price_history = getattr(self, f"{symbol_str}_price_history")
            price_history.Add(current_bar)
            
            if not price_history.IsReady:
                continue
                
            # Calculate ML features
            features = self.calculate_features(symbol, current_bar.Close)
            if features is None:
                continue
                
            # Get ML prediction
            ml_signal = self.get_ml_prediction(features)
            
            # Get technical signals
            tech_signals = self.get_technical_signals(symbol)
            
            # Combined signal logic for crypto (more aggressive than stocks)
            # Crypto is more volatile, so we use lower thresholds
            should_buy = (ml_signal > 0.55 and tech_signals['sma_bullish']) or \
                        (ml_signal > 0.52 and tech_signals['sma_bullish'] and tech_signals['macd_bullish'] and tech_signals['rsi_oversold'])
            should_sell = (ml_signal < 0.45) or \
                         (ml_signal < 0.48 and tech_signals['rsi_overbought'])
            
            # Execute trades
            if should_buy and not self.Portfolio[symbol].Invested:
                allocation = self.btc_allocation if symbol == self.btc else self.eth_allocation
                self.SetHoldings(symbol, allocation)
                self.Debug(f"BUY {symbol}: ML={ml_signal:.3f}, SMA={tech_signals['sma_bullish']}, RSI={tech_signals['rsi_value']:.1f}")
                
            elif should_sell and self.Portfolio[symbol].Invested:
                self.Liquidate(symbol)
                self.Debug(f"SELL {symbol}: ML={ml_signal:.3f}, RSI={tech_signals['rsi_value']:.1f}")
