#!/usr/bin/env python3
"""
Test Alpaca order placement endpoints
"""

import requests

# Your NEW API keys
API_KEY = "CKTF9T2WWLLJRA146EHB"
SECRET_KEY = "kwmd0aPahXWAaMMgTSEO042UCmyn2hEQglrc9pYg"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY,
    "Content-Type": "application/json"
}

def test_order_endpoints():
    print("🚀 Testing Alpaca Order Endpoints")
    print("=" * 50)
    
    base_url = "https://broker-api.sandbox.alpaca.markets"
    
    # Test different order endpoints
    endpoints = [
        "/v1/orders",
        "/v2/orders",
        "/v1/trading/orders",
        "/v2/trading/orders"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing {endpoint}:")
        print(f"   URL: {base_url}{endpoint}")
        
        try:
            # Try GET request first to see if endpoint exists
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            print(f"   GET Response Code: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
            
            if response.status_code in [200, 201, 404]:
                print(f"   ✅ Endpoint exists!")
                
                # If GET works, try a simple POST test
                test_order = {
                    "symbol": "SPY",
                    "qty": 1,
                    "side": "buy",
                    "type": "market",
                    "time_in_force": "day"
                }
                
                post_response = requests.post(f"{base_url}{endpoint}", 
                                            json=test_order, 
                                            headers=headers)
                print(f"   POST Response Code: {post_response.status_code}")
                print(f"   POST Response: {post_response.text[:100]}...")
                
                if post_response.status_code in [200, 201]:
                    print(f"   🎉 SUCCESS! Orders can be placed at {endpoint}")
                    return endpoint
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return None

def main():
    working_endpoint = test_order_endpoints()
    
    if working_endpoint:
        print(f"\n🎉 SUCCESS! Found working order endpoint: {working_endpoint}")
    else:
        print(f"\n❌ No working order endpoints found")

if __name__ == "__main__":
    main()
