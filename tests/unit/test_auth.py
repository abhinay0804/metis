#!/usr/bin/env python3
"""
Test script to check authentication bypass
"""

import os
import requests

def test_auth_bypass():
    print("Testing Authentication Bypass...")
    print("=" * 50)
    
    # Check if dev bypass is enabled
    print("1. Checking dev bypass environment...")
    bypass = os.environ.get('ALLOW_DEV_BYPASS')
    print(f"  ALLOW_DEV_BYPASS: {bypass}")
    
    # Test the auth endpoint directly
    print("\n2. Testing auth endpoint...")
    try:
        # Test without authorization header
        response = requests.post("http://localhost:8001/process", 
                               files={'file': ('test.txt', b'test content', 'text/plain')},
                               data={'reversible': 'true'})
        print(f"  Response status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Auth bypass working")
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "=" * 50)
    print("Auth test completed!")

if __name__ == "__main__":
    test_auth_bypass()
