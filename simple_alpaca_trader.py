#!/usr/bin/env python3
"""
Simple Alpaca Trader - Direct API Trading
100% FREE - No QuantConnect fees, no cloud costs
"""

import json
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

class SimpleAlpacaTrader:
    def __init__(self):
        # Load API keys from config
        with open('config/brokerage_config.json', 'r') as f:
            config = json.load(f)
        
        self.api_key = config['alpaca']['api_key']
        self.secret_key = config['alpaca']['secret_key']
        self.base_url = config['alpaca']['base_url']
        
        # Headers for API requests
        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key,
            'Content-Type': 'application/json'
        }
        
        # Trading parameters
        self.symbol = 'SPY'
        self.position_size = 0.95  # 95% of available cash
        self.stop_loss_pct = 0.05  # 5% stop loss
        self.take_profit_pct = 0.15  # 15% take profit
        
        print(f"🚀 Simple Alpaca Trader initialized")
        print(f"📊 Trading: {self.symbol}")
        print(f"💰 Position size: {self.position_size*100}%")
        print(f"🛑 Stop loss: {self.stop_loss_pct*100}%")
        print(f"🎯 Take profit: {self.take_profit_pct*100}%")
    
    def get_account(self):
        """Get account information"""
        try:
            response = requests.get(f"{self.base_url}/v2/account", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error getting account: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_positions(self):
        """Get current positions"""
        try:
            response = requests.get(f"{self.base_url}/v2/positions", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error getting positions: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            response = requests.get(f"{self.base_url}/v2/latest/trades/{symbol}", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return float(data['trade']['p'])
            else:
                print(f"❌ Error getting price for {symbol}: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def place_order(self, symbol, qty, side, order_type='market'):
        """Place a buy or sell order"""
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
                print(f"✅ {side.upper()} order placed: {qty} shares of {symbol}")
                return order
            else:
                print(f"❌ Error placing {side} order: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def calculate_technical_signals(self, symbol):
        """Calculate simple technical indicators"""
        try:
            # Get recent bars (last 200 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=300)
            
            response = requests.get(
                f"{self.base_url}/v2/stocks/{symbol}/bars",
                headers=self.headers,
                params={
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d'),
                    'timeframe': '1Day',
                    'limit': 200
                }
            )
            
            if response.status_code != 200:
                print(f"❌ Error getting bars: {response.status_code}")
                return None
            
            data = response.json()
            if 'bars' not in data or not data['bars']:
                print(f"❌ No bars data for {symbol}")
                return None
            
            # Convert to DataFrame
            bars = []
            for bar in data['bars']:
                bars.append({
                    'timestamp': bar['t'],
                    'open': float(bar['o']),
                    'high': float(bar['h']),
                    'low': float(bar['l']),
                    'close': float(bar['c']),
                    'volume': int(bar['v'])
                })
            
            df = pd.DataFrame(bars)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Calculate indicators
            df['sma_50'] = df['close'].rolling(50).mean()
            df['sma_200'] = df['close'].rolling(200).mean()
            
            # RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Get latest values
            latest = df.iloc[-1]
            
            signals = {
                'current_price': latest['close'],
                'sma_50': latest['sma_50'],
                'sma_200': latest['sma_200'],
                'rsi': latest['rsi'],
                'sma_bullish': latest['sma_50'] > latest['sma_200'],
                'rsi_oversold': latest['rsi'] < 30,
                'rsi_overbought': latest['rsi'] > 70
            }
            
            return signals
            
        except Exception as e:
            print(f"❌ Error calculating signals: {e}")
            return None
    
    def should_buy(self, signals):
        """Determine if we should buy"""
        if not signals:
            return False
        
        # Simple buy logic: SMA bullish and RSI not overbought
        return signals['sma_bullish'] and not signals['rsi_overbought']
    
    def should_sell(self, signals, entry_price):
        """Determine if we should sell"""
        if not signals:
            return False
        
        current_price = signals['current_price']
        
        # Stop loss
        if current_price <= entry_price * (1 - self.stop_loss_pct):
            return True, "STOP_LOSS"
        
        # Take profit
        if current_price >= entry_price * (1 + self.take_profit_pct):
            return True, "TAKE_PROFIT"
        
        # Technical sell: SMA bearish or RSI overbought
        if not signals['sma_bullish'] or signals['rsi_overbought']:
            return True, "TECHNICAL"
        
        return False, None
    
    def run_trading_cycle(self):
        """Run one trading cycle"""
        print(f"\n🔄 Trading cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get account info
        account = self.get_account()
        if not account:
            return
        
        print(f"💰 Account value: ${float(account['portfolio_value']):,.2f}")
        print(f"💵 Cash: ${float(account['cash']):,.2f}")
        
        # Get current positions
        positions = self.get_positions()
        current_position = None
        
        for pos in positions:
            if pos['symbol'] == self.symbol:
                current_position = pos
                break
        
        # Calculate technical signals
        signals = self.calculate_technical_signals(self.symbol)
        if not signals:
            print("❌ Could not get technical signals")
            return
        
        print(f"📊 {self.symbol} Price: ${signals['current_price']:.2f}")
        print(f"📈 SMA 50: ${signals['sma_50']:.2f}")
        print(f"📉 SMA 200: ${signals['sma_200']:.2f}")
        print(f"🎯 RSI: {signals['rsi']:.1f}")
        print(f"📊 SMA Bullish: {signals['sma_bullish']}")
        
        # Trading logic
        if current_position:
            # We have a position, check if we should sell
            entry_price = float(current_position['avg_entry_price'])
            qty = int(current_position['qty'])
            
            should_sell, reason = self.should_sell(signals, entry_price)
            
            if should_sell:
                print(f"🔴 SELL signal: {reason}")
                self.place_order(self.symbol, qty, 'sell')
            else:
                print(f"⏳ Holding position (Entry: ${entry_price:.2f})")
        else:
            # No position, check if we should buy
            if self.should_buy(signals):
                print(f"🟢 BUY signal detected!")
                
                # Calculate quantity
                cash = float(account['cash'])
                price = signals['current_price']
                qty = int((cash * self.position_size) / price)
                
                if qty > 0:
                    self.place_order(self.symbol, qty, 'buy')
                else:
                    print(f"❌ Not enough cash to buy")
            else:
                print(f"⏳ No buy signal")
    
    def run_continuous(self, interval_minutes=60):
        """Run trading continuously"""
        print(f"🚀 Starting continuous trading (checking every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_trading_cycle()
                print(f"⏰ Waiting {interval_minutes} minutes until next check...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\n🛑 Trading stopped by user")

def main():
    trader = SimpleAlpacaTrader()
    
    # Test connection
    account = trader.get_account()
    if account:
        print(f"✅ Connected to Alpaca successfully!")
        print(f"📊 Account: {account['id']}")
        print(f"💰 Portfolio value: ${float(account['portfolio_value']):,.2f}")
        
        # Run one trading cycle
        trader.run_trading_cycle()
        
        # Ask if user wants to run continuously
        response = input("\n🤔 Run continuously? (y/n): ").lower()
        if response == 'y':
            trader.run_continuous(interval_minutes=60)  # Check every hour
    else:
        print("❌ Failed to connect to Alpaca")

if __name__ == "__main__":
    main()
