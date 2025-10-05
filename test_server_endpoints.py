#!/usr/bin/env python3
"""
Test server endpoints with all file types
"""

import requests
import os
import time
from pathlib import Path
import json

def test_server_endpoints():
    """Test both /process and /analyze endpoints with all files"""
    
    print("🌐 TESTING SERVER ENDPOINTS")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not healthy")
            return
        print("✅ Server is healthy")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("Please start the server with: python run_server.py")
        return
    
    files_dir = Path("Files")
    if not files_dir.exists():
        print("❌ Files directory not found")
        return
    
    # Get all test files
    test_files = []
    for pattern in ["*.pdf", "*.xlsx", "*.pptx", "*.png", "*.jpg", "*.jpeg"]:
        test_files.extend(files_dir.glob(pattern))
    
    test_files.sort()
    print(f"📁 Found {len(test_files)} test files")
    
    # Test results
    results = {
        "masking_tests": {"passed": 0, "failed": 0, "errors": []},
        "analysis_tests": {"passed": 0, "failed": 0, "errors": []},
        "file_details": {}
    }
    
    for i, file_path in enumerate(test_files, 1):
        print(f"\n📄 [{i}/{len(test_files)}] Testing: {file_path.name}")
        print("-" * 40)
        
        file_result = {
            "masking": {"success": False, "error": None, "response": None},
            "analysis": {"success": False, "error": None, "response": None}
        }
        
        # Test 1: Masking endpoint
        print("   🎭 Testing /process endpoint...")
        try:
            with open(file_path, 'rb') as f:
                files_data = {'file': (file_path.name, f, 'application/octet-stream')}
                data = {'user_id': 'test-user'}  # Using dev bypass
                
                response = requests.post(
                    "http://localhost:8001/process", 
                    files=files_data, 
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"      ✅ SUCCESS - Masking ID: {result.get('masking_id', 'N/A')}")
                    print(f"      📊 Masked keys: {list(result.get('masked', {}).keys())}")
                    
                    file_result["masking"]["success"] = True
                    file_result["masking"]["response"] = result
                    results["masking_tests"]["passed"] += 1
                else:
                    error_msg = f"Status {response.status_code}: {response.text}"
                    print(f"      ❌ FAILED - {error_msg}")
                    file_result["masking"]["error"] = error_msg
                    results["masking_tests"]["failed"] += 1
                    results["masking_tests"]["errors"].append(f"{file_path.name}: {error_msg}")
        
        except Exception as e:
            error_msg = str(e)
            print(f"      ❌ ERROR - {error_msg}")
            file_result["masking"]["error"] = error_msg
            results["masking_tests"]["failed"] += 1
            results["masking_tests"]["errors"].append(f"{file_path.name}: {error_msg}")
        
        # Test 2: Analysis endpoint
        print("   🤖 Testing /analyze endpoint...")
        try:
            with open(file_path, 'rb') as f:
                files_data = {'file': (file_path.name, f, 'application/octet-stream')}
                data = {'user_id': 'test-user'}  # Using dev bypass
                
                response = requests.post(
                    "http://localhost:8001/analyze", 
                    files=files_data, 
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"      ✅ SUCCESS - Analysis ID: {result.get('analysis_id', 'N/A')}")
                    print(f"      📈 Risk: {result.get('riskLevel', 'N/A')}")
                    print(f"      📊 Quality: {result.get('dataQuality', 'N/A')}")
                    print(f"      🔒 Sensitive: {result.get('sensitiveFields', 'N/A')}")
                    
                    file_result["analysis"]["success"] = True
                    file_result["analysis"]["response"] = result
                    results["analysis_tests"]["passed"] += 1
                else:
                    error_msg = f"Status {response.status_code}: {response.text}"
                    print(f"      ❌ FAILED - {error_msg}")
                    file_result["analysis"]["error"] = error_msg
                    results["analysis_tests"]["failed"] += 1
                    results["analysis_tests"]["errors"].append(f"{file_path.name}: {error_msg}")
        
        except Exception as e:
            error_msg = str(e)
            print(f"      ❌ ERROR - {error_msg}")
            file_result["analysis"]["error"] = error_msg
            results["analysis_tests"]["failed"] += 1
            results["analysis_tests"]["errors"].append(f"{file_path.name}: {error_msg}")
        
        results["file_details"][file_path.name] = file_result
        
        # Small delay between files
        time.sleep(0.5)
    
    # Summary
    print(f"\n📊 ENDPOINT TEST SUMMARY")
    print("=" * 60)
    print(f"Masking Tests:")
    print(f"  ✅ Passed: {results['masking_tests']['passed']}")
    print(f"  ❌ Failed: {results['masking_tests']['failed']}")
    
    print(f"\nAnalysis Tests:")
    print(f"  ✅ Passed: {results['analysis_tests']['passed']}")
    print(f"  ❌ Failed: {results['analysis_tests']['failed']}")
    
    # Show errors
    if results["masking_tests"]["errors"]:
        print(f"\n❌ MASKING ERRORS:")
        for error in results["masking_tests"]["errors"]:
            print(f"   {error}")
    
    if results["analysis_tests"]["errors"]:
        print(f"\n❌ ANALYSIS ERRORS:")
        for error in results["analysis_tests"]["errors"]:
            print(f"   {error}")
    
    # Calculate success rates
    total_files = len(test_files)
    masking_rate = (results['masking_tests']['passed'] / total_files) * 100 if total_files > 0 else 0
    analysis_rate = (results['analysis_tests']['passed'] / total_files) * 100 if total_files > 0 else 0
    
    print(f"\n📈 SUCCESS RATES:")
    print(f"   Masking Endpoint: {masking_rate:.1f}%")
    print(f"   Analysis Endpoint: {analysis_rate:.1f}%")
    
    # Save results
    results_file = f"server_test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Test list endpoints
    print(f"\n🔍 Testing list endpoints...")
    try:
        # Test list maskings
        response = requests.get("http://localhost:8001/maskings", 
                              headers={'user_id': 'test-user'}, timeout=10)
        if response.status_code == 200:
            maskings = response.json()
            print(f"   ✅ List maskings: Found {len(maskings)} items")
        else:
            print(f"   ❌ List maskings failed: {response.status_code}")
        
        # Test list analyses
        response = requests.get("http://localhost:8001/analyses", 
                              headers={'user_id': 'test-user'}, timeout=10)
        if response.status_code == 200:
            analyses = response.json()
            print(f"   ✅ List analyses: Found {len(analyses)} items")
        else:
            print(f"   ❌ List analyses failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ List endpoints error: {e}")
    
    return results

if __name__ == "__main__":
    test_server_endpoints()
