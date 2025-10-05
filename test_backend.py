#!/usr/bin/env python3
"""
Test script to verify backend functionality
"""

import requests
import json
import os
from pathlib import Path

def test_backend():
    base_url = "http://localhost:8001"
    
    print("Testing Optiv Masking API Backend...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False
    
    # Test 2: Process a sample file
    print("\n2. Testing file processing...")
    
    # Find a sample file
    sample_files_dir = Path("Files")
    if not sample_files_dir.exists():
        print("✗ No Files directory found")
        return False
    
    sample_files = list(sample_files_dir.glob("*"))
    if not sample_files:
        print("✗ No sample files found")
        return False
    
    sample_file = sample_files[0]
    print(f"  Using sample file: {sample_file.name}")
    
    try:
        with open(sample_file, 'rb') as f:
            files = {'file': (sample_file.name, f, 'application/octet-stream')}
            data = {'reversible': 'true'}
            
            # Note: This will fail without proper auth, but we can test the endpoint structure
            response = requests.post(f"{base_url}/process", files=files, data=data)
            
            if response.status_code == 200:
                print("✓ File processing successful")
                result = response.json()
                print(f"  Masking ID: {result.get('masking_id')}")
                print(f"  Reversible: {result.get('reversible')}")
            elif response.status_code == 401:
                print("✓ File processing endpoint accessible (auth required as expected)")
                print("  This is expected behavior - auth is required")
            else:
                print(f"✗ File processing failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
    except Exception as e:
        print(f"✗ File processing failed: {e}")
        return False
    
    # Test 3: List maskings (will also require auth)
    print("\n3. Testing list maskings endpoint...")
    try:
        response = requests.get(f"{base_url}/maskings")
        if response.status_code == 401:
            print("✓ List maskings endpoint accessible (auth required as expected)")
        else:
            print(f"✗ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"✗ List maskings failed: {e}")
    
    print("\n" + "=" * 50)
    print("Backend test completed!")
    print("Note: Authentication is required for full functionality.")
    print("The dev bypass should be enabled in the server startup script.")
    
    return True

if __name__ == "__main__":
    test_backend()
