#!/usr/bin/env python3
"""
Test Alpaca API endpoints to find the working one
"""

import requests

# Your NEW API keys
API_KEY = "CKTF9T2WWLLJRA146EHB"
SECRET_KEY = "kwmd0aPahXWAaMMgTSEO042UCmyn2hEQglrc9pYg"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

def test_endpoint(base_url, endpoint_name):
    print(f"\n🔍 Testing {endpoint_name}:")
    print(f"   URL: {base_url}/v2/account")
    
    try:
        response = requests.get(f"{base_url}/v2/account", headers=headers)
        print(f"   Response Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS! {endpoint_name} works!")
            return True
        else:
            print(f"   ❌ Failed with {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    print("🚀 Testing Alpaca API Endpoints")
    print("=" * 50)
    
    # Test different endpoints
    endpoints = [
        ("https://paper-api.alpaca.markets", "Paper Trading API"),
        ("https://broker-api.sandbox.alpaca.markets", "Broker Sandbox API"),
        ("https://api.alpaca.markets", "Live Trading API"),
        ("https://broker-api.alpaca.markets", "Live Broker API")
    ]
    
    working_endpoints = []
    
    for base_url, name in endpoints:
        if test_endpoint(base_url, name):
            working_endpoints.append((base_url, name))
    
    print(f"\n📊 RESULTS:")
    print("=" * 50)
    
    if working_endpoints:
        print(f"✅ Working endpoints ({len(working_endpoints)}):")
        for base_url, name in working_endpoints:
            print(f"   • {name}: {base_url}")
    else:
        print("❌ No working endpoints found")
        print("   This might mean:")
        print("   • API keys are incorrect")
        print("   • API keys need time to activate")
        print("   • Account needs to be activated")

if __name__ == "__main__":
    main()
