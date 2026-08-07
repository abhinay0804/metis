#!/usr/bin/env python3
"""
Test complete flow from frontend perspective
"""

import requests
import json
import os
from pathlib import Path

def test_complete_flow():
    print("Testing Complete Flow...")
    print("=" * 50)
    
    # Test 1: Backend health
    print("1. Testing backend health...")
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            print("✓ Backend is running")
        else:
            print(f"✗ Backend health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend not accessible: {e}")
        return False
    
    # Test 2: Test file processing with a real file
    print("\n2. Testing file processing...")
    try:
        # Use a real file from the Files directory
        files_dir = Path("Files")
        if not files_dir.exists():
            print("✗ Files directory not found")
            return False
        
        # Find a PDF file
        pdf_files = list(files_dir.glob("*.pdf"))
        if not pdf_files:
            print("✗ No PDF files found")
            return False
        
        test_file = pdf_files[0]
        print(f"  Using file: {test_file.name}")
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/pdf')}
            data = {'reversible': 'true'}
            
            response = requests.post("http://localhost:8001/process", files=files, data=data)
            
            if response.status_code == 200:
                print("✓ File processing successful")
                result = response.json()
                print(f"  Masking ID: {result.get('masking_id')}")
                print(f"  Reversible: {result.get('reversible')}")
                print(f"  Masked data keys: {list(result.get('masked', {}).keys())}")
            else:
                print(f"✗ File processing failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
    except Exception as e:
        print(f"✗ File processing error: {e}")
        return False
    
    # Test 3: Test list maskings
    print("\n3. Testing list maskings...")
    try:
        response = requests.get("http://localhost:8001/maskings")
        if response.status_code == 200:
            print("✓ List maskings successful")
            maskings = response.json()
            print(f"  Found {len(maskings)} maskings")
        else:
            print(f"✗ List maskings failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ List maskings error: {e}")
    
    print("\n" + "=" * 50)
    print("Complete flow test finished!")
    return True

if __name__ == "__main__":
    test_complete_flow()
