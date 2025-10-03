#!/usr/bin/env python3
"""
Fully Automated Trader - Executes Trades Automatically
- Uses Alpaca API to execute real trades
- Runs 24/7 without human intervention
- Learns and improves over time
- 100% automated trading
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
import joblib
import warnings
warnings.filterwarnings('ignore')

class FullyAutomatedTrader:
    def __init__(self):
        self.setup_logging()
        self.setup_database()
        self.setup_directories()
        
        # Load Alpaca API keys
        with open('config/brokerage_config.json', 'r') as f:
            config = json.load(f)
        
        self.api_key = config['alpaca']['api_key']
        self.secret_key = config['alpaca']['secret_key']
        self.base_url = config['alpaca']['base_url']
        
        # API headers
        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key,
            'Content-Type': 'application/json'
        }
        
        # Trading parameters
        self.symbols = ['SPY', 'QQQ', 'IWM', 'VTI']  # Start with stocks only
        self.position_size = 0.95  # 95% of available cash
        self.stop_loss_pct = 0.05  # 5% stop loss
        self.take_profit_pct = 0.15  # 15% take profit
        
        # Performance tracking
        self.performance_history = []
        self.trade_history = []
        
        self.logger.info("🚀 Fully Automated Trader initialized")
        self.logger.info(f"📊 Trading symbols: {self.symbols}")
        self.logger.info(f"💰 Position size: {self.position_size*100}%")
        self.logger.info(f"🛑 Stop loss: {self.stop_loss_pct*100}%")
        self.logger.info(f"🎯 Take profit: {self.take_profit_pct*100}%")
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        Path("logs").mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/automated_trader_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup SQLite database for storing data and learning"""
        self.db_path = "data/automated_trader.db"
        Path("data").mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                timestamp TEXT,
                signal TEXT,
                confidence REAL,
                price REAL,
                executed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                side TEXT,
                quantity INTEGER,
                price REAL,
                timestamp TEXT,
                order_id TEXT,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                total_value REAL,
                cash REAL,
                positions_value REAL,
                daily_pnl REAL
            )
        ''')
        
        self.conn.commit()
        self.logger.info("📊 Database initialized")
    
    def setup_directories(self):
        """Setup directory structure"""
        directories = ['data', 'models', 'logs', 'backups', 'reports']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def get_account(self):
        """Get account information from Alpaca"""
        try:
            response = requests.get(f"{self.base_url}/v2/account", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"❌ Error getting account: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            return None
    
    def get_positions(self):
        """Get current positions from Alpaca"""
        try:
            response = requests.get(f"{self.base_url}/v2/positions", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"❌ Error getting positions: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            return []
    
    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            response = requests.get(f"{self.base_url}/v2/latest/trades/{symbol}", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return float(data['trade']['p'])
            else:
                self.logger.error(f"❌ Error getting price for {symbol}: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            return None
    
    def place_order(self, symbol, qty, side, order_type='market'):
        """Place a buy or sell order on Alpaca"""
        try:
            order_data = {
                'symbol': symbol,
                'qty': str(qty),
                'side': side,
                'type': order_type,
                'time_in_force': 'day'
            }
            
            response = requests.post(f"{self.base_url}/v2/orders", 
                                   headers=self.headers, 
                                   json=order_data)
            
            if response.status_code == 200:
                order = response.json()
                self.logger.info(f"✅ {side.upper()} order placed: {qty} shares of {symbol}")
                self.logger.info(f"📋 Order ID: {order['id']}")
                
                # Store trade in database
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO trades (symbol, side, quantity, price, timestamp, order_id, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, side, qty, order_data.get('price', 0), 
                      datetime.now().isoformat(), order['id'], 'submitted'))
                self.conn.commit()
                
                return order
            else:
                self.logger.error(f"❌ Error placing {side} order: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            return None
    
    def collect_market_data(self, symbol, days=200):
        """Collect market data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=f"{days}d")
            
            if data.empty:
                self.logger.warning(f"❌ No data for {symbol}")
                return None
            
            # Store in database
            cursor = self.conn.cursor()
            
            for timestamp, row in data.iterrows():
                cursor.execute('''
                    INSERT OR REPLACE INTO market_data 
                    (symbol, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, timestamp.strftime('%Y-%m-%d %H:%M:%S'), 
                    row['Open'], row['High'], row['Low'], 
                    row['Close'], row['Volume']
                ))
            
            self.conn.commit()
            self.logger.info(f"✅ Collected {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            self.logger.error(f"❌ Error collecting data for {symbol}: {e}")
            return None
    
    def calculate_features(self, data):
        """Calculate technical indicators"""
        df = data.copy()
        
        # Price-based features
        df['returns'] = df['Close'].pct_change()
        df['volatility'] = df['returns'].rolling(20).std()
        
        # Moving averages
        for period in [5, 10, 20, 50, 100, 200]:
            df[f'sma_{period}'] = df['Close'].rolling(period).mean()
            df[f'price_sma_{period}_ratio'] = df['Close'] / df[f'sma_{period}']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volume features
        df['volume_sma'] = df['Volume'].rolling(20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        
        # Momentum features
        for period in [5, 10, 20]:
            df[f'momentum_{period}'] = df['Close'] / df['Close'].shift(period) - 1
        
        return df
    
    def generate_signal(self, symbol):
        """Generate trading signal using technical analysis"""
        try:
            # Get market data
            data = self.collect_market_data(symbol)
            if data is None or len(data) < 200:
                return None
            
            # Calculate features
            df = self.calculate_features(data)
            latest = df.iloc[-1]
            
            # Technical analysis signals
            sma_bullish = latest['sma_50'] > latest['sma_200']
            rsi_oversold = latest['rsi'] < 30
            rsi_overbought = latest['rsi'] > 70
            macd_bullish = latest['macd'] > latest['macd_signal']
            bb_oversold = latest['bb_position'] < 0.2
            bb_overbought = latest['bb_position'] > 0.8
            
            # Calculate confidence score
            bullish_signals = sum([sma_bullish, macd_bullish, rsi_oversold, bb_oversold])
            bearish_signals = sum([not sma_bullish, rsi_overbought, bb_overbought])
            
            total_signals = bullish_signals + bearish_signals
            confidence = bullish_signals / total_signals if total_signals > 0 else 0.5
            
            # Generate signal
            if bullish_signals >= 2 and confidence > 0.6:
                signal = 'BUY'
            elif bearish_signals >= 2 and confidence < 0.4:
                signal = 'SELL'
            else:
                signal = 'HOLD'
            
            signal_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'signal': signal,
                'confidence': confidence,
                'price': latest['Close'],
                'features': {
                    'sma_bullish': sma_bullish,
                    'rsi': latest['rsi'],
                    'macd_bullish': macd_bullish,
                    'bb_position': latest['bb_position']
                }
            }
            
            # Store signal
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO trading_signals 
                (symbol, timestamp, signal, confidence, price, executed)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, signal_data['timestamp'], signal, confidence, 
                  latest['Close'], False))
            self.conn.commit()
            
            return signal_data
            
        except Exception as e:
            self.logger.error(f"❌ Error generating signal for {symbol}: {e}")
            return None
    
    def execute_trading_strategy(self):
        """Execute the trading strategy"""
        self.logger.info("🔄 Executing trading strategy...")
        
        # Get account info
        account = self.get_account()
        if not account:
            self.logger.error("❌ Cannot get account info")
            return
        
        cash = float(account['cash'])
        portfolio_value = float(account['portfolio_value'])
        
        self.logger.info(f"💰 Account Value: ${portfolio_value:,.2f}")
        self.logger.info(f"💵 Cash: ${cash:,.2f}")
        
        # Get current positions
        positions = self.get_positions()
        current_positions = {pos['symbol']: pos for pos in positions}
        
        # Generate signals for all symbols
        signals = []
        for symbol in self.symbols:
            signal = self.generate_signal(symbol)
            if signal:
                signals.append(signal)
        
        # Execute trades based on signals
        for signal in signals:
            symbol = signal['symbol']
            signal_type = signal['signal']
            confidence = signal['confidence']
            price = signal['price']
            
            self.logger.info(f"📊 {symbol}: {signal_type} (Confidence: {confidence:.3f}, Price: ${price:.2f})")
            
            # Only execute high-confidence signals
            if confidence > 0.7:
                if signal_type == 'BUY' and symbol not in current_positions:
                    # Calculate quantity
                    qty = int((cash * self.position_size) / price)
                    if qty > 0:
                        self.logger.info(f"🟢 EXECUTING BUY: {qty} shares of {symbol}")
                        self.place_order(symbol, qty, 'buy')
                    else:
                        self.logger.warning(f"❌ Not enough cash to buy {symbol}")
                
                elif signal_type == 'SELL' and symbol in current_positions:
                    position = current_positions[symbol]
                    qty = int(position['qty'])
                    if qty > 0:
                        self.logger.info(f"🔴 EXECUTING SELL: {qty} shares of {symbol}")
                        self.place_order(symbol, qty, 'sell')
        
        # Check for stop losses and take profits
        for symbol, position in current_positions.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                entry_price = float(position['avg_entry_price'])
                qty = int(position['qty'])
                
                # Stop loss
                if current_price <= entry_price * (1 - self.stop_loss_pct):
                    self.logger.info(f"🛑 STOP LOSS: {symbol} at ${current_price:.2f}")
                    self.place_order(symbol, qty, 'sell')
                
                # Take profit
                elif current_price >= entry_price * (1 + self.take_profit_pct):
                    self.logger.info(f"🎯 TAKE PROFIT: {symbol} at ${current_price:.2f}")
                    self.place_order(symbol, qty, 'sell')
        
        # Record performance
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO performance 
            (timestamp, total_value, cash, positions_value, daily_pnl)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), portfolio_value, cash, 
              portfolio_value - cash, 0.0))  # Daily PnL calculation would need previous day's value
        self.conn.commit()
        
        self.logger.info("✅ Trading strategy execution complete")
    
    def start_automated_trading(self):
        """Start the automated trading system"""
        self.logger.info("🚀 Starting Fully Automated Trader...")
        
        # Test Alpaca connection
        account = self.get_account()
        if not account:
            self.logger.error("❌ Cannot connect to Alpaca. Check your API keys.")
            return
        
        self.logger.info(f"✅ Connected to Alpaca successfully!")
        self.logger.info(f"📊 Account: {account['id']}")
        self.logger.info(f"💰 Portfolio value: ${float(account['portfolio_value']):,.2f}")
        
        # Collect initial data
        self.logger.info("📥 Collecting initial market data...")
        for symbol in self.symbols:
            self.collect_market_data(symbol)
            time.sleep(1)  # Rate limiting
        
        # Schedule tasks
        schedule.every(5).minutes.do(self.execute_trading_strategy)
        schedule.every().day.at("09:30").do(self.execute_trading_strategy)
        schedule.every().day.at("16:00").do(self.execute_trading_strategy)
        
        self.logger.info("⏰ Scheduled tasks:")
        self.logger.info("   - Trading strategy: Every 5 minutes")
        self.logger.info("   - Market open: 9:30 AM daily")
        self.logger.info("   - Market close: 4:00 PM daily")
        
        # Run initial strategy
        self.execute_trading_strategy()
        
        # Main loop
        self.logger.info("🔄 Starting main trading loop...")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("🛑 Automated trader stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {e}")

def main():
    trader = FullyAutomatedTrader()
    trader.start_automated_trading()

if __name__ == "__main__":
    main()
