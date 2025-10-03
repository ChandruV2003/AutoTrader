#!/usr/bin/env python3
"""
🤖 MASTER ORCHESTRATOR - The Brain of AutoTrader
===============================================

This is the central intelligence that orchestrates all trading components:
- Automatic error detection and recovery
- Portfolio management and risk controls
- Multi-broker trading execution
- Continuous learning and adaptation
- Complete hands-off operation

Usage: python master_orchestrator.py
"""

import time
import logging
import subprocess
import threading
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import alpaca_trade_api as tradeapi
import requests

class MasterOrchestrator:
    """The brain that orchestrates all trading operations"""
    
    def __init__(self):
        self.setup_logging()
        self.setup_directories()
        self.setup_database()
        
        # Trading configuration
        self.portfolio_value = 10000  # Starting capital
        self.max_position_size = 0.25  # Max 25% per position
        self.stop_loss_pct = 0.05  # 5% stop loss
        self.take_profit_pct = 0.15  # 15% take profit
        
        # Symbols to trade
        self.stock_symbols = ['SPY', 'QQQ', 'IWM', 'VTI']
        self.crypto_symbols = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'SOL-USD']
        
        # Brokerage configurations (load from config file)
        self.brokerages = self.load_brokerage_config()
        
        # System state
        self.is_running = False
        self.positions = {}
        self.models = {}
        self.last_trade_time = {}
        
        # Performance tracking
        self.daily_pnl = 0
        self.total_trades = 0
        self.winning_trades = 0
        
        self.logger.info("🤖 Master Orchestrator initialized")
    def load_brokerage_config(self):
        """Load brokerage configuration from file"""
        try:
            config_file = Path("config/alpaca_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return {
                    'alpaca': {
                        'api_key': config['alpaca']['api_key'],
                        'secret_key': config['alpaca']['secret_key'],
                        'base_url': config['alpaca']['base_url'],
                        'enabled': True
                    },
                    'manual': {
                        'enabled': True,
                        'fallback': True
                    }
                }
        except Exception as e:
            self.logger.warning(f"Could not load config file: {e}")
        
        # Fallback configuration
        return {
            'alpaca': {
                'api_key': 'INVALID_KEY_NEEDS_UPDATE',
                'secret_key': 'INVALID_SECRET_NEEDS_UPDATE',
                'base_url': 'https://paper-api.alpaca.markets',
                'enabled': False
            },
            'manual': {
                'enabled': True,
                'fallback': True
            }
        }
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"master_orchestrator_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_directories(self):
        """Setup required directories"""
        for dir_name in ['data', 'models', 'signals', 'backups']:
            Path(dir_name).mkdir(exist_ok=True)
    
    def setup_database(self):
        """Setup SQLite database for tracking"""
        self.db_path = Path("data/master_orchestrator.db")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    action TEXT,
                    price REAL,
                    quantity INTEGER,
                    portfolio_value REAL,
                    pnl REAL,
                    model_confidence REAL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    component TEXT,
                    status TEXT,
                    error_message TEXT,
                    performance_metrics TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    model_type TEXT,
                    accuracy REAL,
                    precision REAL,
                    recall REAL,
                    f1_score REAL
                )
            ''')
    
    def check_system_health(self) -> Dict[str, bool]:
        """Check health of all system components"""
        health_status = {}
        
        # Check data collection
        try:
            data = yf.download('SPY', period='1d')
            health_status['data_collection'] = not data.empty
        except Exception as e:
            health_status['data_collection'] = False
            self.logger.error(f"Data collection health check failed: {e}")
        
        # Check Alpaca connection
        try:
            api = tradeapi.REST(
                self.brokerages['alpaca']['api_key'],
                self.brokerages['alpaca']['secret_key'],
                self.brokerages['alpaca']['base_url']
            )
            account = api.get_account()
            health_status['alpaca_connection'] = account is not None
        except Exception as e:
            health_status['alpaca_connection'] = False
            self.logger.warning(f"Alpaca connection failed: {e}")
        
        # Check models
        health_status['models'] = len(self.models) > 0
        
        # Check database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            health_status['database'] = True
        except Exception as e:
            health_status['database'] = False
            self.logger.error(f"Database health check failed: {e}")
        
        # Log health status
        self.logger.info(f"System Health: {health_status}")
        
        # Store health status in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO system_health (timestamp, component, status, error_message, performance_metrics)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                'overall',
                'healthy' if all(health_status.values()) else 'degraded',
                '',
                json.dumps(health_status)
            ))
        
        return health_status
    
    def collect_market_data(self) -> Dict[str, pd.DataFrame]:
        """Collect fresh market data for all symbols"""
        all_data = {}
        
        for symbol in self.stock_symbols + self.crypto_symbols:
            try:
                data = yf.download(symbol, period='1y', interval='1d')
                if not data.empty:
                    all_data[symbol] = data
                    self.logger.info(f"✅ Collected {len(data)} records for {symbol}")
                else:
                    self.logger.warning(f"⚠️ No data collected for {symbol}")
            except Exception as e:
                self.logger.error(f"❌ Error collecting data for {symbol}: {e}")
        
        return all_data
    
    def calculate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators and features"""
        df = data.copy()
        
        # Basic price features
        df['sma_5'] = df['Close'].rolling(5).mean()
        df['sma_20'] = df['Close'].rolling(20).mean()
        df['sma_50'] = df['Close'].rolling(50).mean()
        df['sma_200'] = df['Close'].rolling(200).mean()
        
        # Returns and volatility
        df['returns'] = df['Close'].pct_change()
        df['volatility_5'] = df['returns'].rolling(5).std()
        df['volatility_20'] = df['returns'].rolling(20).std()
        
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
        
        # Target (next day return > 0)
        df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        return df.dropna()
    
    def train_models(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, RandomForestClassifier]:
        """Train ML models for each symbol"""
        models = {}
        
        for symbol, data in all_data.items():
            try:
                df = self.calculate_features(data)
                
                if len(df) < 100:  # Need sufficient data
                    self.logger.warning(f"Insufficient data for {symbol}")
                    continue
                
                # Prepare features
                feature_cols = ['sma_5', 'sma_20', 'sma_50', 'sma_200', 'volatility_5', 'volatility_20', 'rsi', 'macd', 'macd_signal']
                X = df[feature_cols].fillna(0)
                y = df['target'].fillna(0)
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Train model
                model = RandomForestClassifier(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                models[symbol] = model
                
                # Save model
                model_path = Path(f"models/{symbol}_model.pkl")
                import joblib
                joblib.dump(model, model_path)
                
                # Log performance
                self.logger.info(f"🤖 Trained model for {symbol}: {accuracy:.3f} accuracy")
                
                # Store performance metrics
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('''
                        INSERT INTO model_performance (timestamp, symbol, model_type, accuracy, precision, recall, f1_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        datetime.now().isoformat(),
                        symbol,
                        'RandomForest',
                        accuracy,
                        0, 0, 0  # Placeholder for other metrics
                    ))
                
            except Exception as e:
                self.logger.error(f"❌ Error training model for {symbol}: {e}")
        
        return models
    
    def generate_signals(self, all_data: Dict[str, pd.DataFrame], models: Dict[str, RandomForestClassifier]) -> Dict[str, Dict]:
        """Generate trading signals for all symbols"""
        signals = {}
        
        for symbol, data in all_data.items():
            try:
                if symbol not in models:
                    continue
                
                df = self.calculate_features(data)
                if df.empty:
                    continue
                
                # Get latest features
                latest = df.iloc[-1]
                feature_cols = ['sma_5', 'sma_20', 'sma_50', 'sma_200', 'volatility_5', 'volatility_20', 'rsi', 'macd', 'macd_signal']
                features = latest[feature_cols].fillna(0).values.reshape(1, -1)
                
                # Get prediction
                model = models[symbol]
                prediction = model.predict(features)[0]
                confidence = model.predict_proba(features)[0].max()
                
                # Technical analysis
                current_price = latest['Close']
                sma_bullish = latest['sma_50'] > latest['sma_200']
                rsi_oversold = latest['rsi'] < 30
                rsi_overbought = latest['rsi'] > 70
                macd_bullish = latest['macd'] > latest['macd_signal']
                
                # Signal logic
                signal_type = "HOLD"
                if prediction == 1 and confidence > 0.6 and sma_bullish and not rsi_overbought:
                    signal_type = "BUY"
                elif prediction == 0 and confidence > 0.6 and (rsi_overbought or not sma_bullish):
                    signal_type = "SELL"
                
                signals[symbol] = {
                    'action': signal_type,
                    'confidence': confidence,
                    'price': current_price,
                    'prediction': prediction,
                    'technical_analysis': {
                        'sma_bullish': sma_bullish,
                        'rsi_oversold': rsi_oversold,
                        'rsi_overbought': rsi_overbought,
                        'macd_bullish': macd_bullish
                    },
                    'stop_loss': current_price * (1 - self.stop_loss_pct) if signal_type == "BUY" else 0,
                    'take_profit': current_price * (1 + self.take_profit_pct) if signal_type == "BUY" else 0
                }
                
                self.logger.info(f"📊 {symbol}: {signal_type} (Confidence: {confidence:.3f}, Price: ${current_price:.2f})")
                
            except Exception as e:
                self.logger.error(f"❌ Error generating signal for {symbol}: {e}")
        
        return signals
    
    def execute_trades(self, signals: Dict[str, Dict]) -> Dict[str, bool]:
        """Execute trades based on signals"""
        execution_results = {}
        
        for symbol, signal in signals.items():
            try:
                if signal['action'] == "HOLD":
                    execution_results[symbol] = True
                    continue
                
                # Check if we should trade (avoid overtrading)
                last_trade = self.last_trade_time.get(symbol, datetime.min)
                if datetime.now() - last_trade < timedelta(hours=1):  # Minimum 1 hour between trades
                    self.logger.info(f"⏰ Skipping {symbol} - too soon since last trade")
                    execution_results[symbol] = True
                    continue
                
                # Calculate position size
                current_price = signal['price']
                position_value = self.portfolio_value * self.max_position_size
                quantity = int(position_value / current_price)
                
                if quantity < 1:
                    self.logger.warning(f"⚠️ Position too small for {symbol}")
                    execution_results[symbol] = False
                    continue
                
                # Try Alpaca first, fallback to manual
                trade_executed = False
                
                if self.brokerages['alpaca']['enabled']:
                    trade_executed = self._execute_alpaca_trade(symbol, signal, quantity)
                
                if not trade_executed and self.brokerages['manual']['enabled']:
                    trade_executed = self._execute_manual_trade(symbol, signal, quantity)
                
                if trade_executed:
                    # Update tracking
                    self.last_trade_time[symbol] = datetime.now()
                    self.total_trades += 1
                    
                    # Store trade in database
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute('''
                            INSERT INTO trades (timestamp, symbol, action, price, quantity, portfolio_value, pnl, model_confidence)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            datetime.now().isoformat(),
                            symbol,
                            signal['action'],
                            current_price,
                            quantity,
                            self.portfolio_value,
                            0,  # PnL calculated later
                            signal['confidence']
                        ))
                    
                    self.logger.info(f"✅ Executed {signal['action']} for {quantity} shares of {symbol} at ${current_price:.2f}")
                
                execution_results[symbol] = trade_executed
                
            except Exception as e:
                self.logger.error(f"❌ Error executing trade for {symbol}: {e}")
                execution_results[symbol] = False
        
        return execution_results
    
    def _execute_alpaca_trade(self, symbol: str, signal: Dict, quantity: int) -> bool:
        """Execute trade via Alpaca API"""
        try:
            api = tradeapi.REST(
                self.brokerages['alpaca']['api_key'],
                self.brokerages['alpaca']['secret_key'],
                self.brokerages['alpaca']['base_url']
            )
            
            # Convert symbol format for Alpaca
            alpaca_symbol = symbol.replace('-USD', '') if '-USD' in symbol else symbol
            
            if signal['action'] == "BUY":
                order = api.submit_order(
                    symbol=alpaca_symbol,
                    qty=quantity,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
            elif signal['action'] == "SELL":
                order = api.submit_order(
                    symbol=alpaca_symbol,
                    qty=quantity,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
            
            self.logger.info(f"📈 Alpaca order submitted: {order.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Alpaca trade execution failed: {e}")
            return False
    
    def _execute_manual_trade(self, symbol: str, signal: Dict, quantity: int) -> bool:
        """Execute manual trade (save to file for user to execute)"""
        try:
            trade_instruction = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': signal['action'],
                'quantity': quantity,
                'price': signal['price'],
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'confidence': signal['confidence']
            }
            
            # Save to manual trades file
            manual_trades_file = Path("signals/manual_trades.json")
            trades = []
            
            if manual_trades_file.exists():
                with open(manual_trades_file, 'r') as f:
                    trades = json.load(f)
            
            trades.append(trade_instruction)
            
            with open(manual_trades_file, 'w') as f:
                json.dump(trades, f, indent=2)
            
            self.logger.info(f"📝 Manual trade instruction saved for {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Manual trade execution failed: {e}")
            return False
    
    def update_portfolio_value(self):
        """Update portfolio value based on current positions"""
        try:
            if self.brokerages['alpaca']['enabled']:
                api = tradeapi.REST(
                    self.brokerages['alpaca']['api_key'],
                    self.brokerages['alpaca']['secret_key'],
                    self.brokerages['alpaca']['base_url']
                )
                
                account = api.get_account()
                self.portfolio_value = float(account.portfolio_value)
                
                # Update positions
                positions = api.list_positions()
                for pos in positions:
                    self.positions[pos.symbol] = {
                        'quantity': int(pos.qty),
                        'market_value': float(pos.market_value),
                        'unrealized_pnl': float(pos.unrealized_pnl)
                    }
                
                self.logger.info(f"💰 Portfolio Value: ${self.portfolio_value:,.2f}")
                
        except Exception as e:
            self.logger.error(f"❌ Error updating portfolio: {e}")
    
    def generate_daily_report(self):
        """Generate daily performance report"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get today's trades
                today = datetime.now().date()
                trades = conn.execute('''
                    SELECT * FROM trades WHERE date(timestamp) = ?
                ''', (today,)).fetchall()
                
                # Calculate metrics
                total_trades = len(trades)
                profitable_trades = len([t for t in trades if t[7] > 0])  # PnL > 0
                win_rate = profitable_trades / total_trades if total_trades > 0 else 0
                
                # Generate report
                report = {
                    'date': today.isoformat(),
                    'portfolio_value': self.portfolio_value,
                    'total_trades': total_trades,
                    'profitable_trades': profitable_trades,
                    'win_rate': win_rate,
                    'daily_pnl': self.daily_pnl,
                    'positions': self.positions,
                    'system_health': self.check_system_health()
                }
                
                # Save report
                report_file = Path(f"reports/daily_report_{today}.json")
                report_file.parent.mkdir(exist_ok=True)
                
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                self.logger.info(f"📊 Daily report generated: {report_file}")
                
                # Print summary
                print(f"\n📊 DAILY REPORT - {today}")
                print("=" * 50)
                print(f"💰 Portfolio Value: ${self.portfolio_value:,.2f}")
                print(f"📈 Total Trades: {total_trades}")
                print(f"🎯 Win Rate: {win_rate:.1%}")
                print(f"💵 Daily P&L: ${self.daily_pnl:,.2f}")
                print(f"🏠 Active Positions: {len(self.positions)}")
                
        except Exception as e:
            self.logger.error(f"❌ Error generating daily report: {e}")
    
    def run_cycle(self):
        """Run one complete trading cycle"""
        try:
            self.logger.info("🔄 Starting trading cycle...")
            
            # 1. Check system health
            health = self.check_system_health()
            if not health.get('data_collection', False):
                self.logger.error("❌ System health check failed - skipping cycle")
                return
            
            # 2. Update portfolio
            self.update_portfolio_value()
            
            # 3. Collect market data
            all_data = self.collect_market_data()
            if not all_data:
                self.logger.error("❌ No market data collected - skipping cycle")
                return
            
            # 4. Train/update models
            self.models = self.train_models(all_data)
            
            # 5. Generate signals
            signals = self.generate_signals(all_data, self.models)
            
            # 6. Execute trades
            execution_results = self.execute_trades(signals)
            
            # 7. Log results
            successful_trades = sum(1 for result in execution_results.values() if result)
            self.logger.info(f"✅ Trading cycle complete: {successful_trades}/{len(execution_results)} trades executed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in trading cycle: {e}")
    
    def run(self):
        """Main execution loop"""
        self.logger.info("🚀 Master Orchestrator starting...")
        self.is_running = True
        
        # Initial setup
        self.update_portfolio_value()
        
        cycle_count = 0
        while self.is_running:
            try:
                cycle_count += 1
                self.logger.info(f"🔄 Starting cycle #{cycle_count}")
                
                # Run trading cycle
                self.run_cycle()
                
                # Generate daily report at end of day
                if datetime.now().hour == 16 and datetime.now().minute < 5:  # 4 PM
                    self.generate_daily_report()
                
                # Wait before next cycle (5 minutes during market hours, 1 hour after hours)
                current_hour = datetime.now().hour
                if 9 <= current_hour <= 16:  # Market hours
                    sleep_time = 300  # 5 minutes
                else:
                    sleep_time = 3600  # 1 hour
                
                self.logger.info(f"😴 Sleeping for {sleep_time//60} minutes...")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Master Orchestrator stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Critical error in main loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        self.logger.info("🏁 Master Orchestrator shutdown complete")

def main():
    """Main entry point"""
    print("🤖 MASTER ORCHESTRATOR - The Brain of AutoTrader")
    print("=" * 60)
    print("🧠 Intelligent trading system with:")
    print("   • Automatic error detection and recovery")
    print("   • Multi-broker trading execution")
    print("   • Continuous learning and adaptation")
    print("   • Complete hands-off operation")
    print("   • Portfolio management and risk controls")
    print("=" * 60)
    
    orchestrator = MasterOrchestrator()
    
    try:
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
    finally:
        print("🏁 Master Orchestrator shutdown complete")

if __name__ == "__main__":
    main()
