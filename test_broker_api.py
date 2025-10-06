#!/usr/bin/env python3
"""
Test Alpaca Broker API specifically
"""

import requests

# Your NEW API keys
API_KEY = "CKTF9T2WWLLJRA146EHB"
SECRET_KEY = "kwmd0aPahXWAaMMgTSEO042UCmyn2hEQglrc9pYg"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

def test_broker_endpoints():
    print("🚀 Testing Alpaca Broker API Endpoints")
    print("=" * 50)
    
    base_url = "https://broker-api.sandbox.alpaca.markets"
    
    # Test different endpoints
    endpoints = [
        "/v1/accounts",
        "/v2/accounts", 
        "/v1/account",
        "/v2/account",
        "/v1/portfolio",
        "/v2/portfolio",
        "/v1/positions",
        "/v2/positions"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing {endpoint}:")
        print(f"   URL: {base_url}{endpoint}")
        
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            print(f"   Response Code: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS! {endpoint} works!")
                return endpoint
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized - API keys might be wrong")
            elif response.status_code == 404:
                print(f"   ❌ Not found - endpoint doesn't exist")
            else:
                print(f"   ❌ Failed with {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def main():
    working_endpoint = test_broker_endpoints()
    
    if working_endpoint:
        print(f"\n🎉 SUCCESS! Found working endpoint: {working_endpoint}")
    else:
        print(f"\n❌ No working endpoints found")
        print("   Possible issues:")
        print("   • API keys are for different service")
        print("   • Keys need time to activate")
        print("   • Account not properly set up")

if __name__ == "__main__":
    main()
