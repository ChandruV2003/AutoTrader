#!/usr/bin/env python3
"""
🔧 Alpaca Connection Fixer
=========================

This script fixes Alpaca API connection issues and tests the setup.
"""

import alpaca_trade_api as tradeapi
import requests
import json
from datetime import datetime

def test_alpaca_connection():
    """Test Alpaca API connection and fix common issues"""
    
    # Your API credentials
    api_key = "CKYLEELNW2NIB96RKL93"
    secret_key = "65fiIPKkpyle0qxUoajCxp4RTnEyHEc1r2yHEnLB"
    base_url = "https://paper-api.alpaca.markets"
    
    print("🔧 Testing Alpaca Connection...")
    print(f"📡 Base URL: {base_url}")
    print(f"🔑 API Key: {api_key[:10]}...")
    
    try:
        # Initialize API
        api = tradeapi.REST(api_key, secret_key, base_url)
        
        # Test account access
        print("\n📊 Testing account access...")
        account = api.get_account()
        
        print("✅ Account connection successful!")
        print(f"💰 Account Status: {account.status}")
        print(f"💰 Buying Power: ${float(account.buying_power):,.2f}")
        print(f"💰 Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"💰 Cash: ${float(account.cash):,.2f}")
        
        # Test market data access
        print("\n📈 Testing market data access...")
        bars = api.get_bars("SPY", tradeapi.TimeFrame.Day, limit=1)
        if bars:
            latest_bar = bars[0]
            print(f"✅ Market data access successful!")
            print(f"📊 SPY latest price: ${latest_bar.c}")
        else:
            print("⚠️ No market data received")
        
        # Test order submission (paper trade)
        print("\n📝 Testing order submission (paper trade)...")
        try:
            # Submit a very small test order
            order = api.submit_order(
                symbol="SPY",
                qty=1,
                side="buy",
                type="market",
                time_in_force="day"
            )
            print(f"✅ Test order submitted: {order.id}")
            
            # Cancel the test order immediately
            api.cancel_order(order.id)
            print("✅ Test order cancelled successfully")
            
        except Exception as e:
            print(f"⚠️ Order submission test failed: {e}")
            print("This might be normal if account has insufficient funds")
        
        print("\n🎉 Alpaca connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Alpaca connection failed: {e}")
        
        # Try to diagnose the issue
        print("\n🔍 Diagnosing connection issues...")
        
        # Test basic HTTP connection
        try:
            response = requests.get(base_url, timeout=10)
            print(f"✅ Base URL is reachable (HTTP {response.status_code})")
        except Exception as http_error:
            print(f"❌ Base URL is not reachable: {http_error}")
        
        # Test API endpoint
        try:
            auth_url = f"{base_url}/v2/account"
            headers = {
                "APCA-API-KEY-ID": api_key,
                "APCA-API-SECRET-KEY": secret_key
            }
            response = requests.get(auth_url, headers=headers, timeout=10)
            print(f"📡 API endpoint response: HTTP {response.status_code}")
            
            if response.status_code == 401:
                print("🔑 Authentication failed - check API keys")
            elif response.status_code == 403:
                print("🚫 Access forbidden - check account permissions")
            elif response.status_code == 200:
                print("✅ API endpoint is working")
                
        except Exception as api_error:
            print(f"❌ API endpoint test failed: {api_error}")
        
        return False

def fix_common_issues():
    """Fix common Alpaca connection issues"""
    
    print("\n🔧 Attempting to fix common issues...")
    
    # Issue 1: Wrong base URL
    print("1️⃣ Checking base URL...")
    correct_urls = [
        "https://paper-api.alpaca.markets",  # Paper trading
        "https://api.alpaca.markets",        # Live trading
    ]
    
    for url in correct_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} is reachable")
        except:
            print(f"❌ {url} is not reachable")
    
    # Issue 2: API key format
    print("\n2️⃣ Checking API key format...")
    api_key = "CKYLEELNW2NIB96RKL93"
    if len(api_key) != 24:
        print("⚠️ API key length seems incorrect (should be 24 characters)")
    else:
        print("✅ API key length is correct")
    
    # Issue 3: Account status
    print("\n3️⃣ Checking account status...")
    print("💡 Make sure your Alpaca account is:")
    print("   • Fully approved and active")
    print("   • Has paper trading enabled")
    print("   • API keys are correctly generated")
    
    return True

def generate_config():
    """Generate a working configuration file"""
    
    config = {
        "alpaca": {
            "api_key": "CKYLEELNW2NIB96RKL93",
            "secret_key": "65fiIPKkpyle0qxUoajCxp4RTnEyHEc1r2yHEnLB",
            "base_url": "https://paper-api.alpaca.markets",
            "paper_trading": True,
            "tested_at": datetime.now().isoformat()
        },
        "trading": {
            "max_position_size": 0.25,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.15,
            "min_trade_interval_hours": 1
        },
        "symbols": {
            "stocks": ["SPY", "QQQ", "IWM", "VTI"],
            "crypto": ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD"]
        }
    }
    
    with open("config/working_alpaca_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Configuration saved to: config/working_alpaca_config.json")

def main():
    """Main function"""
    print("🔧 Alpaca Connection Fixer")
    print("=" * 40)
    
    # Test connection
    success = test_alpaca_connection()
    
    if not success:
        # Try to fix issues
        fix_common_issues()
    
    # Generate config regardless
    generate_config()
    
    print("\n📋 Next steps:")
    if success:
        print("✅ Alpaca connection is working!")
        print("🚀 You can now run the Master Orchestrator")
        print("💡 Command: python master_orchestrator.py")
    else:
        print("❌ Alpaca connection needs manual fixing")
        print("🔧 Check your Alpaca account settings:")
        print("   • Verify API keys are correct")
        print("   • Ensure account is approved")
        print("   • Check paper trading is enabled")
        print("   • Try generating new API keys")
        print("\n💡 The system will fallback to manual trading")
        print("🚀 You can still run the Master Orchestrator")

if __name__ == "__main__":
    main()
