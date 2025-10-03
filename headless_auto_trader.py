#!/usr/bin/env python3
"""
Headless AutoTrader - Fully Automated Learning System
- Runs 24/7 without human intervention
- Learns from historical data and trading results
- Continuously improves performance
- Supports both stocks and crypto
"""

import pandas as pd
import numpy as np
import yfinance as yf
import requests
import json
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import schedule
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class HeadlessAutoTrader:
    def __init__(self):
        self.setup_logging()
        self.setup_database()
        self.setup_directories()
        
        # Trading parameters
        self.symbols = {
            'stocks': ['SPY', 'QQQ', 'IWM', 'VTI'],
            'crypto': ['BTC-USD', 'ETH-USD', 'ADA-USD', 'SOL-USD']
        }
        
        # Learning parameters
        self.learning_rate = 0.01
        self.exploration_rate = 0.1
        self.memory_size = 10000
        
        # Performance tracking
        self.performance_history = []
        self.trade_history = []
        
        self.logger.info("🚀 Headless AutoTrader initialized")
        self.logger.info(f"📊 Monitoring: {len(self.symbols['stocks'])} stocks, {len(self.symbols['crypto'])} crypto")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        Path("logs").mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/autotrader_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup SQLite database for storing data and learning"""
        self.db_path = "data/autotrader.db"
        Path("data").mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp DATETIME,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                market_type TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp DATETIME,
                signal TEXT,
                confidence REAL,
                price REAL,
                features TEXT,
                market_type TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                entry_time DATETIME,
                exit_time DATETIME,
                entry_price REAL,
                exit_price REAL,
                quantity INTEGER,
                pnl REAL,
                signal_confidence REAL,
                market_type TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                model_type TEXT,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                total_pnl REAL
            )
        ''')
        
        self.conn.commit()
        self.logger.info("📊 Database initialized")
    
    def setup_directories(self):
        """Setup directory structure"""
        directories = ['data', 'models', 'logs', 'backups', 'reports']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def collect_historical_data(self, symbol, market_type='stocks', days=365*5):
        """Collect and store historical market data"""
        try:
            self.logger.info(f"📈 Collecting historical data for {symbol} ({market_type})")
            
            # Get data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=f"{days}d")
            
            if data.empty:
                self.logger.warning(f"❌ No data for {symbol}")
                return False
            
            # Store in database
            cursor = self.conn.cursor()
            
            for timestamp, row in data.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO market_data 
                    (symbol, timestamp, open, high, low, close, volume, market_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, timestamp, row['Open'], row['High'], 
                    row['Low'], row['Close'], row['Volume'], market_type
                ))
            
            self.conn.commit()
            self.logger.info(f"✅ Stored {len(data)} records for {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error collecting data for {symbol}: {e}")
            return False
    
    def download_all_historical_data(self):
        """Download historical data for all symbols"""
        self.logger.info("📥 Starting historical data collection...")
        
        total_symbols = len(self.symbols['stocks']) + len(self.symbols['crypto'])
        completed = 0
        
        # Download stock data
        for symbol in self.symbols['stocks']:
            if self.collect_historical_data(symbol, 'stocks'):
                completed += 1
            time.sleep(1)  # Rate limiting
        
        # Download crypto data
        for symbol in self.symbols['crypto']:
            if self.collect_historical_data(symbol, 'crypto'):
                completed += 1
            time.sleep(1)  # Rate limiting
        
        self.logger.info(f"✅ Historical data collection complete: {completed}/{total_symbols} symbols")
    
    def calculate_features(self, data):
        """Calculate advanced features for ML model"""
        df = data.copy()
        
        # Price-based features
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        df['volatility'] = df['returns'].rolling(20).std()
        
        # Moving averages
        for period in [5, 10, 20, 50, 100, 200]:
            df[f'sma_{period}'] = df['close'].rolling(period).mean()
            df[f'price_sma_{period}_ratio'] = df['close'] / df[f'sma_{period}']
        
        # Technical indicators
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volume features
        df['volume_sma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Momentum features
        for period in [5, 10, 20]:
            df[f'momentum_{period}'] = df['close'] / df['close'].shift(period) - 1
        
        # Volatility features
        df['volatility_5d'] = df['returns'].rolling(5).std()
        df['volatility_20d'] = df['returns'].rolling(20).std()
        df['volatility_ratio'] = df['volatility_5d'] / df['volatility_20d']
        
        return df
    
    def create_training_data(self, symbol, market_type):
        """Create training data with features and labels"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM market_data 
                WHERE symbol = ? AND market_type = ?
                ORDER BY timestamp
            ''', (symbol, market_type))
            
            data = cursor.fetchall()
            if len(data) < 200:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'id', 'symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'market_type'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Calculate features
            df = self.calculate_features(df)
            
            # Create labels (future returns)
            df['future_return_1d'] = df['close'].shift(-1) / df['close'] - 1
            df['future_return_5d'] = df['close'].shift(-5) / df['close'] - 1
            
            # Binary labels for classification
            df['buy_signal'] = (df['future_return_5d'] > 0.02).astype(int)  # 2% gain in 5 days
            df['sell_signal'] = (df['future_return_5d'] < -0.02).astype(int)  # 2% loss in 5 days
            
            # Select features for training
            feature_columns = [
                'returns', 'volatility', 'rsi', 'macd', 'macd_signal', 'macd_histogram',
                'bb_width', 'bb_position', 'volume_ratio', 'volatility_ratio'
            ]
            
            # Add SMA ratios
            for period in [5, 10, 20, 50]:
                feature_columns.append(f'price_sma_{period}_ratio')
            
            # Add momentum features
            for period in [5, 10, 20]:
                feature_columns.append(f'momentum_{period}')
            
            # Remove rows with NaN values
            df_clean = df[feature_columns + ['buy_signal', 'sell_signal']].dropna()
            
            if len(df_clean) < 100:
                return None
            
            return df_clean
            
        except Exception as e:
            self.logger.error(f"❌ Error creating training data for {symbol}: {e}")
            return None
    
    def train_model(self, symbol, market_type):
        """Train ML model for a specific symbol"""
        try:
            self.logger.info(f"🤖 Training model for {symbol} ({market_type})")
            
            # Get training data
            data = self.create_training_data(symbol, market_type)
            if data is None:
                self.logger.warning(f"❌ Insufficient data for {symbol}")
                return None
            
            # Prepare features and labels
            feature_columns = [col for col in data.columns if col not in ['buy_signal', 'sell_signal']]
            X = data[feature_columns]
            y = data['buy_signal']  # Focus on buy signals
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save model
            model_path = f"models/{symbol}_{market_type}_model.pkl"
            joblib.dump(model, model_path)
            
            # Save performance metrics
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO model_performance 
                (timestamp, model_type, accuracy, total_trades, winning_trades, total_pnl)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (datetime.now(), f"{symbol}_{market_type}", accuracy, 0, 0, 0.0))
            self.conn.commit()
            
            self.logger.info(f"✅ Model trained for {symbol}: {accuracy:.3f} accuracy")
            return model
            
        except Exception as e:
            self.logger.error(f"❌ Error training model for {symbol}: {e}")
            return None
    
    def generate_signal(self, symbol, market_type):
        """Generate trading signal using trained model"""
        try:
            # Load model
            model_path = f"models/{symbol}_{market_type}_model.pkl"
            if not Path(model_path).exists():
                self.logger.warning(f"❌ No model found for {symbol}")
                return None
            
            model = joblib.load(model_path)
            
            # Get latest data
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM market_data 
                WHERE symbol = ? AND market_type = ?
                ORDER BY timestamp DESC LIMIT 200
            ''', (symbol, market_type))
            
            data = cursor.fetchall()
            if len(data) < 200:
                return None
            
            # Convert to DataFrame and calculate features
            df = pd.DataFrame(data, columns=[
                'id', 'symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'market_type'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp').sort_index()
            
            df = self.calculate_features(df)
            
            # Get latest features
            feature_columns = [col for col in df.columns if col not in ['buy_signal', 'sell_signal']]
            latest_features = df[feature_columns].iloc[-1:].fillna(0)
            
            # Generate prediction
            prediction = model.predict(latest_features)[0]
            confidence = model.predict_proba(latest_features)[0].max()
            
            signal = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'signal': 'BUY' if prediction == 1 else 'HOLD',
                'confidence': confidence,
                'price': df['close'].iloc[-1],
                'features': latest_features.to_dict('records')[0],
                'market_type': market_type
            }
            
            # Store signal
            cursor.execute('''
                INSERT INTO trading_signals 
                (symbol, timestamp, signal, confidence, price, features, market_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal['symbol'], signal['timestamp'], signal['signal'],
                signal['confidence'], signal['price'], 
                json.dumps(signal['features']), signal['market_type']
            ))
            self.conn.commit()
            
            return signal
            
        except Exception as e:
            self.logger.error(f"❌ Error generating signal for {symbol}: {e}")
            return None
    
    def update_market_data(self):
        """Update market data for all symbols"""
        self.logger.info("🔄 Updating market data...")
        
        for market_type, symbols in self.symbols.items():
            for symbol in symbols:
                try:
                    # Get latest data
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="2d")
                    
                    if not data.empty:
                        latest = data.iloc[-1]
                        
                        cursor = self.conn.cursor()
                        cursor.execute('''
                            INSERT OR REPLACE INTO market_data 
                            (symbol, timestamp, open, high, low, close, volume, market_type)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            symbol, latest.name, latest['Open'], latest['High'],
                            latest['Low'], latest['Close'], latest['Volume'], market_type
                        ))
                        self.conn.commit()
                        
                except Exception as e:
                    self.logger.error(f"❌ Error updating {symbol}: {e}")
                
                time.sleep(0.5)  # Rate limiting
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        self.logger.info("🔄 Starting trading cycle...")
        
        # Update market data
        self.update_market_data()
        
        # Generate signals for all symbols
        signals = []
        for market_type, symbols in self.symbols.items():
            for symbol in symbols:
                signal = self.generate_signal(symbol, market_type)
                if signal:
                    signals.append(signal)
        
        # Log signals
        for signal in signals:
            if signal['confidence'] > 0.7:  # High confidence signals
                self.logger.info(f"🎯 {signal['signal']} {signal['symbol']} "
                               f"(Confidence: {signal['confidence']:.3f}, "
                               f"Price: ${signal['price']:.2f})")
        
        self.logger.info(f"✅ Trading cycle complete: {len(signals)} signals generated")
    
    def retrain_models(self):
        """Retrain all models with latest data"""
        self.logger.info("🤖 Retraining all models...")
        
        for market_type, symbols in self.symbols.items():
            for symbol in symbols:
                self.train_model(symbol, market_type)
                time.sleep(1)  # Rate limiting
        
        self.logger.info("✅ Model retraining complete")
    
    def generate_performance_report(self):
        """Generate performance report"""
        try:
            cursor = self.conn.cursor()
            
            # Get recent performance
            cursor.execute('''
                SELECT * FROM model_performance 
                ORDER BY timestamp DESC LIMIT 10
            ''')
            performance = cursor.fetchall()
            
            # Get recent signals
            cursor.execute('''
                SELECT * FROM trading_signals 
                WHERE timestamp > datetime('now', '-7 days')
                ORDER BY timestamp DESC
            ''')
            recent_signals = cursor.fetchall()
            
            report = {
                'timestamp': datetime.now(),
                'total_models': len(performance),
                'recent_signals': len(recent_signals),
                'high_confidence_signals': len([s for s in recent_signals if s[4] > 0.7])
            }
            
            # Save report
            report_path = f"reports/performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"📊 Performance report generated: {report_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error generating report: {e}")
    
    def start_automated_trading(self):
        """Start the automated trading system"""
        self.logger.info("🚀 Starting Headless AutoTrader...")
        
        # Download historical data if not exists
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM market_data')
        data_count = cursor.fetchone()[0]
        
        if data_count < 1000:  # If we don't have much data
            self.logger.info("📥 Downloading historical data...")
            self.download_all_historical_data()
        
        # Train initial models
        self.logger.info("🤖 Training initial models...")
        self.retrain_models()
        
        # Schedule tasks
        schedule.every(5).minutes.do(self.run_trading_cycle)
        schedule.every().day.at("09:30").do(self.update_market_data)
        schedule.every().day.at("16:00").do(self.retrain_models)
        schedule.every().day.at("17:00").do(self.generate_performance_report)
        
        self.logger.info("⏰ Scheduled tasks:")
        self.logger.info("   - Trading cycle: Every 5 minutes")
        self.logger.info("   - Market data update: 9:30 AM daily")
        self.logger.info("   - Model retraining: 4:00 PM daily")
        self.logger.info("   - Performance report: 5:00 PM daily")
        
        # Run initial cycle
        self.run_trading_cycle()
        
        # Main loop
        self.logger.info("🔄 Starting main trading loop...")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("🛑 AutoTrader stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {e}")

def main():
    trader = HeadlessAutoTrader()
    trader.start_automated_trading()

if __name__ == "__main__":
    main()
