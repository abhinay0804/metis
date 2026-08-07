#!/usr/bin/env python3
"""
Test script to verify frontend-backend connection
"""

import requests
import json

def test_frontend_backend_connection():
    print("Testing Frontend-Backend Connection...")
    print("=" * 50)
    
    # Test 1: Backend health check
    print("1. Testing backend health...")
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            print("✓ Backend is running and accessible")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend not accessible: {e}")
        return False
    
    # Test 2: Test CORS preflight
    print("\n2. Testing CORS preflight...")
    try:
        headers = {
            'Origin': 'http://localhost:8080',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type, Authorization'
        }
        response = requests.options("http://localhost:8001/process", headers=headers)
        print(f"  CORS preflight response: {response.status_code}")
        print(f"  CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"  CORS test error: {e}")
    
    # Test 3: Test actual API call with mock data
    print("\n3. Testing API call with mock data...")
    try:
        # Create a simple test file
        test_file_content = b"Test file content with email: test@example.com and phone: 555-123-4567"
        
        files = {'file': ('test.txt', test_file_content, 'text/plain')}
        data = {'reversible': 'true'}
        # No authorization header for dev bypass
        headers = {}
        
        response = requests.post("http://localhost:8001/process", files=files, data=data, headers=headers)
        
        if response.status_code == 200:
            print("✓ API call successful")
            result = response.json()
            print(f"  Masking ID: {result.get('masking_id')}")
            print(f"  Reversible: {result.get('reversible')}")
        else:
            print(f"✗ API call failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ API call error: {e}")
    
    print("\n" + "=" * 50)
    print("Connection test completed!")
    return True

if __name__ == "__main__":
    test_frontend_backend_connection()
