#!/usr/bin/env python3
"""
🔧 Alpaca Account Setup Guide
============================

This script helps you set up a proper Alpaca account for automatic trading.
"""

import requests
import json
from datetime import datetime

def check_alpaca_api_key_format():
    """Check if the current API key format is correct"""
    
    current_key = "CKYLEELNW2NIB96RKL93"
    
    print("🔍 Checking API Key Format...")
    print(f"Current Key: {current_key}")
    print(f"Length: {len(current_key)} characters")
    
    # Alpaca API keys should be 24 characters and start with certain prefixes
    if len(current_key) != 24:
        print("❌ API key length is incorrect (should be 24 characters)")
        return False
    
    # Check if it looks like a valid Alpaca key
    if current_key.isalnum() and len(current_key) == 24:
        print("✅ API key format looks correct")
        return True
    else:
        print("❌ API key format appears invalid")
        return False

def test_alpaca_endpoints():
    """Test different Alpaca endpoints to identify the issue"""
    
    api_key = "CKYLEELNW2NIB96RKL93"
    secret_key = "65fiIPKkpyle0qxUoajCxp4RTnEyHEc1r2yHEnLB"
    
    endpoints = [
        "https://paper-api.alpaca.markets/v2/account",
        "https://api.alpaca.markets/v2/account",
        "https://paper-api.alpaca.markets/v2/positions",
        "https://paper-api.alpaca.markets/v2/orders"
    ]
    
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key
    }
    
    print("\n🔍 Testing Alpaca Endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"📡 {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                data = response.json()
                if 'account' in endpoint:
                    print(f"   💰 Account Status: {data.get('status', 'Unknown')}")
                    print(f"   💰 Buying Power: ${float(data.get('buying_power', 0)):,.2f}")
            elif response.status_code == 401:
                print("   🔑 Authentication failed")
            elif response.status_code == 403:
                print("   🚫 Access forbidden")
            else:
                print(f"   ⚠️ Unexpected response")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()

def generate_new_api_keys_guide():
    """Generate a guide for creating new API keys"""
    
    print("🔧 HOW TO CREATE NEW ALPACA API KEYS")
    print("=" * 50)
    print()
    print("1️⃣ Go to Alpaca Markets:")
    print("   https://app.alpaca.markets/")
    print()
    print("2️⃣ Sign in or create an account")
    print("   • Use your existing credentials")
    print("   • Or create a new account if needed")
    print()
    print("3️⃣ Navigate to API Keys:")
    print("   • Go to: Account → API Keys")
    print("   • Or: https://app.alpaca.markets/paper/dashboard/overview")
    print()
    print("4️⃣ Generate New Keys:")
    print("   • Click 'Generate New Key'")
    print("   • Choose 'Paper Trading' for testing")
    print("   • Copy the API Key ID and Secret Key")
    print()
    print("5️⃣ Update Configuration:")
    print("   • Replace keys in master_orchestrator.py")
    print("   • Or create new config file")
    print()
    print("6️⃣ Test Connection:")
    print("   • Run: python test_alpaca_connection.py")
    print()

def create_working_config_template():
    """Create a template for working API keys"""
    
    config_template = {
        "alpaca_paper_trading": {
            "api_key": "YOUR_NEW_API_KEY_HERE",
            "secret_key": "YOUR_NEW_SECRET_KEY_HERE",
            "base_url": "https://paper-api.alpaca.markets",
            "paper_trading": True,
            "instructions": [
                "1. Get new API keys from https://app.alpaca.markets/",
                "2. Replace YOUR_NEW_API_KEY_HERE with your actual API key",
                "3. Replace YOUR_NEW_SECRET_KEY_HERE with your actual secret key",
                "4. Save this file as config/alpaca_config.json",
                "5. Test with: python test_alpaca_connection.py"
            ]
        },
        "alternative_brokers": {
            "robinhood": {
                "note": "No official API - use manual trading or browser automation",
                "status": "manual_only"
            },
            "webull": {
                "note": "Has API but requires approval",
                "status": "requires_approval"
            },
            "interactive_brokers": {
                "note": "Professional API - requires account approval",
                "status": "professional"
            },
            "tradier": {
                "note": "Good API for retail traders",
                "status": "available"
            }
        }
    }
    
    # Create config directory
    import os
    os.makedirs("config", exist_ok=True)
    
    # Save template
    with open("config/alpaca_config_template.json", "w") as f:
        json.dump(config_template, f, indent=2)
    
    print("💾 Configuration template saved to: config/alpaca_config_template.json")

def test_alternative_brokers():
    """Test alternative broker APIs"""
    
    print("🔍 Testing Alternative Broker APIs...")
    
    # Test Tradier (free tier available)
    try:
        print("\n📡 Testing Tradier API...")
        # Tradier has a free tier for testing
        tradier_url = "https://api.tradier.com/v1/user/profile"
        # Note: Would need actual API key to test
        print("   ℹ️ Requires API key - check https://developer.tradier.com/")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n💡 Alternative Solutions:")
    print("   1. Fix Alpaca API keys (recommended)")
    print("   2. Use Tradier API (free tier available)")
    print("   3. Use browser automation with Robinhood/Webull")
    print("   4. Manual trading with signal generation")

def main():
    """Main function"""
    print("🔧 ALPACA API SETUP TROUBLESHOOTER")
    print("=" * 50)
    
    # Check current API key format
    key_valid = check_alpaca_api_key_format()
    
    # Test endpoints
    test_alpaca_endpoints()
    
    # Generate setup guide
    generate_new_api_keys_guide()
    
    # Create config template
    create_working_config_template()
    
    # Test alternatives
    test_alternative_brokers()
    
    print("\n🎯 RECOMMENDED NEXT STEPS:")
    print("=" * 30)
    
    if not key_valid:
        print("1. ❗ Create new Alpaca API keys (current ones appear invalid)")
        print("2. 🔧 Update configuration with new keys")
        print("3. 🧪 Test connection")
        print("4. 🚀 Run Master Orchestrator")
    else:
        print("1. 🔍 Check Alpaca account status")
        print("2. 🔧 Verify paper trading is enabled")
        print("3. 🧪 Test with different endpoints")
        print("4. 🚀 Run Master Orchestrator")
    
    print("\n💡 The Master Orchestrator will work with manual trading")
    print("   while you fix the API issues!")

if __name__ == "__main__":
    main()
