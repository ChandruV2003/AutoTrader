#!/usr/bin/env python3
"""
Test Alpaca API Connection
"""

import json
import requests

# Load API keys
with open('config/brokerage_config.json', 'r') as f:
    config = json.load(f)

api_key = config['alpaca']['api_key']
secret_key = config['alpaca']['secret_key']
base_url = config['alpaca']['base_url']

print(f"🔑 API Key: {api_key}")
print(f"🔑 Secret Key: {secret_key[:10]}...")
print(f"🌐 Base URL: {base_url}")

# Test connection
headers = {
    'APCA-API-KEY-ID': api_key,
    'APCA-API-SECRET-KEY': secret_key,
    'Content-Type': 'application/json'
}

print(f"\n🧪 Testing connection to: {base_url}/v2/account")

try:
    response = requests.get(f"{base_url}/v2/account", headers=headers)
    print(f"📊 Status Code: {response.status_code}")
    print(f"📄 Response: {response.text}")
    
    if response.status_code == 200:
        account = response.json()
        print(f"✅ SUCCESS! Connected to Alpaca")
        print(f"📊 Account ID: {account.get('id', 'N/A')}")
        print(f"💰 Portfolio Value: ${float(account.get('portfolio_value', 0)):,.2f}")
        print(f"💵 Cash: ${float(account.get('cash', 0)):,.2f}")
    else:
        print(f"❌ FAILED! Status: {response.status_code}")
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
