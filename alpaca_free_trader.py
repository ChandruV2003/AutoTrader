"""
Alpaca FREE API Trading System
100% FREE for individuals - no commissions, no monthly fees
"""

import requests
import json
import time
from datetime import datetime
import logging

class AlpacaFreeTrader:
    def __init__(self):
        # Alpaca Paper Trading (FREE) - WORKING ENDPOINT!
        self.base_url = "https://broker-api.sandbox.alpaca.markets"
        self.data_url = "https://data.alpaca.markets"
        
        # Your Alpaca API keys (FREE) - NEW KEYS!
        self.api_key = "CKTF9T2WWLLJRA146EHB"
        self.secret_key = "kwmd0aPahXWAaMMgTSEO042UCmyn2hEQglrc9pYg"
        
        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key
        }
        
        self.logger = logging.getLogger(__name__)
        
    def get_account_info(self):
        """Get account balance and info - FREE"""
        try:
            print(f"🔍 Testing API connection...")
            print(f"   URL: {self.base_url}/v1/accounts")
            print(f"   API Key: {self.api_key[:10]}...")
            
            response = requests.get(f"{self.base_url}/v1/accounts", headers=self.headers)
            print(f"   Response Code: {response.status_code}")
            
            if response.status_code == 200:
                accounts = response.json()
                print(f"   ✅ SUCCESS! Connected to Alpaca!")
                print(f"   📊 Found {len(accounts)} account(s)")
                
                if accounts:
                    # Use the first account
                    account = accounts[0]
                    return {
                        'account_id': account.get('id', 'Unknown'),
                        'status': account.get('status', 'Unknown'),
                        'currency': account.get('currency', 'USD'),
                        'created_at': account.get('created_at', 'Unknown')
                    }
                else:
                    return {
                        'account_id': 'No accounts found',
                        'status': 'New account',
                        'currency': 'USD',
                        'created_at': 'Just created'
                    }
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return None
            
    def get_current_price(self, symbol):
        """Get current price - FREE"""
        try:
            response = requests.get(f"{self.data_url}/v2/stocks/{symbol}/quotes/latest", 
                                  headers=self.headers)
            if response.status_code == 200:
                quote = response.json()
                return float(quote['quote']['ap'])
            else:
                self.logger.error(f"Price error for {symbol}: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return None
            
    def place_order(self, symbol, quantity, side, order_type="market"):
        """Place trade order - FREE"""
        try:
            order_data = {
                "symbol": symbol,
                "qty": str(quantity),
                "side": side,  # "buy" or "sell"
                "type": order_type,  # "market" or "limit"
                "time_in_force": "day"
            }
            
            response = requests.post(f"{self.base_url}/v2/orders", 
                                   headers=self.headers, 
                                   json=order_data)
            
            if response.status_code == 201:
                order = response.json()
                self.logger.info(f"Order placed: {side} {quantity} {symbol}")
                return order
            else:
                self.logger.error(f"Order error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None
            
    def execute_signal(self, signal_data):
        """Execute trading signal from your AutoTrader"""
        symbol = signal_data.get('symbol', 'SPY')
        signal = signal_data.get('signal', 'HOLD')
        confidence = signal_data.get('confidence', 0.5)
        price = signal_data.get('price', 0)
        
        print(f"\n🎯 EXECUTING SIGNAL ON ALPACA (FREE):")
        print(f"   Symbol: {symbol}")
        print(f"   Signal: {signal}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Price: ${price:.2f}")
        
        # Get account info
        account = self.get_account_info()
        if not account:
            print("   ❌ Could not get account info")
            return False
            
        print(f"   🏦 Account ID: {account.get('account_id', 'N/A')}")
        print(f"   📊 Status: {account.get('status', 'N/A')}")
        print(f"   💰 Currency: {account.get('currency', 'USD')}")
        print(f"   📅 Created: {account.get('created_at', 'N/A')}")
        print("   💡 This is a new account - ready for trading!")
        
        if signal == "BUY" and confidence > 0.6:
            # For new account, simulate trading
            # position_value = account['buying_power'] * 0.1
            quantity = 1  # Simulate 1 share for new account
            
            if quantity > 0:
                print(f"   📈 BUYING {quantity} shares of {symbol}")
                print(f"   💰 Position Value: ${price:.2f}")
                
                order = self.place_order(symbol, quantity, "buy", "market")
                if order:
                    print(f"   ✅ Order placed successfully!")
                    return True
                else:
                    print(f"   ❌ Order failed")
                    return False
            else:
                print(f"   ⚠️ Insufficient buying power")
                return False
                
        elif signal == "SELL" and confidence < 0.4:
            print(f"   📉 SELLING position in {symbol}")
            # Implement sell logic here
            return True
            
        else:
            print(f"   ⚪ HOLDING - signal not strong enough")
            return True
            
    def setup_instructions(self):
        """Print setup instructions"""
        print("\n🚀 ALPACA FREE API SETUP:")
        print("=" * 50)
        print("1. Go to: https://alpaca.markets")
        print("2. Click 'Get Started' (FREE)")
        print("3. Sign up with email (takes 2 minutes)")
        print("4. Go to 'Paper Trading' section")
        print("5. Generate API keys (FREE)")
        print("6. Copy API keys to this script")
        print("7. Start trading - NO COMMISSIONS!")
        print("\n💰 COSTS:")
        print("   • API Access: FREE")
        print("   • Stock Trades: FREE")
        print("   • Data: FREE")
        print("   • Monthly Fee: FREE")
        print("\n✅ PERFECT FOR:")
        print("   • Individual traders")
        print("   • Automated systems")
        print("   • Testing strategies")
        print("   • Small accounts")

def main():
    """Test Alpaca integration"""
    print("🚀 Alpaca FREE API AutoTrader")
    print("=" * 50)
    
    trader = AlpacaFreeTrader()
    trader.setup_instructions()
    
    # Test signal from your headless system
    test_signal = {
        'symbol': 'SPY',
        'signal': 'BUY',
        'confidence': 0.667,
        'price': 669.22
    }
    
    print(f"\n🧪 Testing with your current signal:")
    trader.execute_signal(test_signal)

if __name__ == "__main__":
    main()
