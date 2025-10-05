#!/usr/bin/env python3
"""
Test different file types with the backend
"""

import requests
import os
from pathlib import Path

def test_file_types():
    print("Testing Different File Types...")
    print("=" * 50)
    
    files_dir = Path("Files")
    if not files_dir.exists():
        print("✗ Files directory not found")
        return
    
    # Test different file types
    file_types = {
        'PDF': list(files_dir.glob("*.pdf")),
        'XLSX': list(files_dir.glob("*.xlsx")),
        'PPTX': list(files_dir.glob("*.pptx")),
        'Images': list(files_dir.glob("*.png")) + list(files_dir.glob("*.jpg")) + list(files_dir.glob("*.jpeg"))
    }
    
    for file_type, files in file_types.items():
        print(f"\n{file_type} Files:")
        if not files:
            print(f"  No {file_type} files found")
            continue
            
        test_file = files[0]
        print(f"  Testing: {test_file.name}")
        
        try:
            with open(test_file, 'rb') as f:
                files_data = {'file': (test_file.name, f, 'application/octet-stream')}
                data = {'reversible': 'true'}
                
                response = requests.post("http://localhost:8001/process", files=files_data, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✓ Success - Masking ID: {result.get('masking_id')}")
                    print(f"    Masked data keys: {list(result.get('masked', {}).keys())}")
                else:
                    print(f"  ✗ Failed - Status: {response.status_code}")
                    print(f"    Error: {response.text}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("File type testing completed!")

if __name__ == "__main__":
    test_file_types()
