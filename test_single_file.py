#!/usr/bin/env python3
"""
Test single file analysis
"""

import requests
import time

def test_single_file():
    """Test analysis on a single file"""
    
    # Wait for server to be ready
    time.sleep(3)
    
    filename = 'File_004.png'
    print(f'Testing {filename} with restarted server...')
    
    try:
        with open(f'Files/{filename}', 'rb') as f:
            files = {'file': (filename, f, 'application/octet-stream')}
            data = {'user_id': 'test-user'}
            response = requests.post('http://localhost:8001/analyze', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print('SUCCESS! New analysis result:')
            print(f'Description: {result.get("description", "N/A")}')
            print(f'Risk: {result.get("riskLevel", "N/A")}')
            print(f'Quality: {result.get("dataQuality", "N/A")}')
            print(f'Sensitive Fields: {result.get("sensitiveFields", "N/A")}')
            
            findings = result.get('keyFindings', [])
            if findings:
                print('Key Findings:')
                for finding in findings[:3]:
                    print(f'  - {finding}')
        else:
            print(f'Failed: {response.status_code}')
            print(f'Error: {response.text}')
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test_single_file()
