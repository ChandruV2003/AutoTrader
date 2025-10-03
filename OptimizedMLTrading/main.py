# Optimized ML-Enhanced Trading Algorithm for Maximum Profitability
from AlgorithmImports import *
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

class OptimizedMLTrading(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2015, 1, 1)  # More recent data for better performance
        self.SetCash(10_000)
        
        # Add multiple symbols for diversification
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.qqq = self.AddEquity("QQQ", Resolution.Daily).Symbol
        self.iwm = self.AddEquity("IWM", Resolution.Daily).Symbol
        
        # Technical indicators for each symbol
        self.setup_indicators(self.spy)
        self.setup_indicators(self.qqq)
        self.setup_indicators(self.iwm)
        
        # ML model loading
        self.model = None
        self.load_ml_model()
        
        # Risk management
        self.max_portfolio_risk = 0.95  # Use 95% of portfolio
        self.stop_loss_pct = 0.05  # 5% stop loss
        self.take_profit_pct = 0.15  # 15% take profit
        
        # Position sizing
        self.position_size = 0.33  # 33% per position (3 positions max)
        
        self.SetWarmUp(200)
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        
    def setup_indicators(self, symbol):
        """Setup technical indicators for a symbol"""
        symbol_str = str(symbol).replace(" ", "_").lower()
        
        setattr(self, f"{symbol_str}_fast_sma", self.SMA(symbol, 20, Resolution.Daily))
        setattr(self, f"{symbol_str}_slow_sma", self.SMA(symbol, 50, Resolution.Daily))
        setattr(self, f"{symbol_str}_rsi", self.RSI(symbol, 14, MovingAverageType.Wilders))
        setattr(self, f"{symbol_str}_macd", self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily))
        setattr(self, f"{symbol_str}_atr", self.ATR(symbol, 14, MovingAverageType.Simple))
        setattr(self, f"{symbol_str}_bb", self.BB(symbol, 20, 2, MovingAverageType.Simple, Resolution.Daily))
        setattr(self, f"{symbol_str}_price_history", RollingWindow[TradeBar](200))
        
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

    def calculate_features(self, symbol, current_price: float) -> dict:
        """Calculate ML features from current market data"""
        symbol_str = str(symbol).replace(" ", "_").lower()
        price_history = getattr(self, f"{symbol_str}_price_history")
        
        if not price_history.IsReady:
            return None
            
        # Get recent prices for calculations (filter out None values)
        recent_prices = [bar.Close for bar in price_history if bar is not None and bar.Close is not None]
        
        if len(recent_prices) < 30:
            return None
        
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
            if len(returns_1d) >= 30 and np.std(returns_1d[-30:]) > 0:
                skew_30d = np.mean([(r - np.mean(returns_1d[-30:]))**3 for r in returns_1d[-30:]]) / (np.std(returns_1d[-30:])**3)
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
        symbol_str = str(symbol).replace(" ", "_").lower()
        
        fast_sma = getattr(self, f"{symbol_str}_fast_sma")
        slow_sma = getattr(self, f"{symbol_str}_slow_sma")
        rsi = getattr(self, f"{symbol_str}_rsi")
        macd = getattr(self, f"{symbol_str}_macd")
        bb = getattr(self, f"{symbol_str}_bb")
        
        sma_bullish = fast_sma.Current.Value > slow_sma.Current.Value
        rsi_oversold = rsi.Current.Value < 30
        rsi_overbought = rsi.Current.Value > 70
        macd_bullish = macd.Current.Value > macd.Signal.Current.Value
        bb_oversold = bb.Current.Value < bb.LowerBand.Current.Value
        bb_overbought = bb.Current.Value > bb.UpperBand.Current.Value
        
        return {
            'sma_bullish': sma_bullish,
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought,
            'macd_bullish': macd_bullish,
            'bb_oversold': bb_oversold,
            'bb_overbought': bb_overbought,
            'rsi_value': rsi.Current.Value
        }

    def calculate_position_size(self, symbol, signal_strength: float) -> float:
        """Calculate position size based on signal strength and risk management"""
        if signal_strength < 0.6:
            return 0
            
        # Scale position size based on signal strength
        base_size = self.position_size
        strength_multiplier = min(signal_strength * 1.5, 1.0)  # Cap at 1.0
        
        return base_size * strength_multiplier

    def OnData(self, data: Slice):
        if self.IsWarmingUp:
            return
            
        # Process each symbol
        for symbol in [self.spy, self.qqq, self.iwm]:
            if not data.ContainsKey(symbol):
                continue
                
            symbol_str = str(symbol).replace(" ", "_").lower()
            
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
            
            # Enhanced signal logic for better profitability
            # More aggressive thresholds for better returns
            strong_buy = (ml_signal > 0.7 and tech_signals['sma_bullish'] and tech_signals['macd_bullish'])
            moderate_buy = (ml_signal > 0.6 and tech_signals['sma_bullish']) or \
                          (ml_signal > 0.55 and tech_signals['sma_bullish'] and tech_signals['rsi_oversold'])
            
            should_buy = strong_buy or moderate_buy
            should_sell = (ml_signal < 0.4) or \
                         (ml_signal < 0.45 and tech_signals['rsi_overbought']) or \
                         (ml_signal < 0.5 and tech_signals['bb_overbought'])
            
            # Calculate position size
            position_size = self.calculate_position_size(symbol, ml_signal)
            
            # Execute trades
            if should_buy and not self.Portfolio[symbol].Invested and position_size > 0:
                self.SetHoldings(symbol, position_size)
                self.Debug(f"BUY {symbol}: ML={ml_signal:.3f}, Size={position_size:.2f}, SMA={tech_signals['sma_bullish']}, RSI={tech_signals['rsi_value']:.1f}")
                
            elif should_sell and self.Portfolio[symbol].Invested:
                self.Liquidate(symbol)
                self.Debug(f"SELL {symbol}: ML={ml_signal:.3f}, RSI={tech_signals['rsi_value']:.1f}")
            
            # Risk management - stop loss and take profit
            if self.Portfolio[symbol].Invested:
                entry_price = self.Portfolio[symbol].AveragePrice
                current_price = current_bar.Close
                
                # Stop loss
                if current_price <= entry_price * (1 - self.stop_loss_pct):
                    self.Liquidate(symbol)
                    self.Debug(f"STOP LOSS {symbol}: Entry={entry_price:.2f}, Current={current_price:.2f}")
                
                # Take profit
                elif current_price >= entry_price * (1 + self.take_profit_pct):
                    self.Liquidate(symbol)
                    self.Debug(f"TAKE PROFIT {symbol}: Entry={entry_price:.2f}, Current={current_price:.2f}")
