#!/usr/bin/env python3
"""
Test CORS from frontend perspective
"""

import requests

def test_cors():
    print("Testing CORS from frontend perspective...")
    print("=" * 50)
    
    # Test CORS preflight
    print("1. Testing CORS preflight...")
    try:
        headers = {
            'Origin': 'http://localhost:8080',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options("http://localhost:8001/process", headers=headers)
        print(f"  CORS preflight status: {response.status_code}")
        print(f"  CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"  CORS preflight error: {e}")
    
    # Test actual request with Origin header
    print("\n2. Testing actual request with Origin...")
    try:
        files = {'file': ('test.txt', b'test content', 'text/plain')}
        data = {'reversible': 'true'}
        headers = {'Origin': 'http://localhost:8080'}
        
        response = requests.post("http://localhost:8001/process", files=files, data=data, headers=headers)
        print(f"  Request status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Request successful")
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  Request error: {e}")
    
    print("\n" + "=" * 50)
    print("CORS test completed!")

if __name__ == "__main__":
    test_cors()
