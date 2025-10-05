#!/usr/bin/env python3
"""
Test fresh analysis on multiple files to show unique results
"""

import requests
import time
import json

def test_fresh_analysis():
    """Test analysis on multiple different file types"""
    
    # Test different file types
    test_files = [
        ('File_001.png', 'Image file'),
        ('File_004.png', 'Image file (different content)'), 
        ('File_008.xlsx', 'Excel spreadsheet'),
        ('File_012.pdf', 'PDF document'),
        ('File_014.pptx', 'PowerPoint presentation')
    ]
    
    print('🔬 TESTING FRESH ANALYSIS - UNIQUE RESULTS')
    print('=' * 60)
    
    results = []
    
    # Analyze each file
    for filename, description in test_files:
        print(f'\n📄 Analyzing {filename} ({description})')
        print('-' * 40)
        
        try:
            with open(f'Files/{filename}', 'rb') as f:
                files = {'file': (filename, f, 'application/octet-stream')}
                data = {'user_id': 'test-user'}
                response = requests.post('http://localhost:8001/analyze', files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                analysis_id = result['analysis_id']
                
                # Store result for comparison
                results.append({
                    'filename': filename,
                    'analysis_id': analysis_id,
                    'description': result.get('description', 'N/A'),
                    'risk_level': result.get('riskLevel', 'N/A'),
                    'quality': result.get('dataQuality', 'N/A'),
                    'sensitive_fields': result.get('sensitiveFields', 'N/A'),
                    'key_findings': result.get('keyFindings', [])[:2]  # First 2 findings
                })
                
                print(f'✅ Success - Analysis ID: {analysis_id}')
                print(f'📝 Description: {result.get("description", "N/A")}')
                print(f'🎯 Risk: {result.get("riskLevel", "N/A")} | Quality: {result.get("dataQuality", "N/A")} | Sensitive: {result.get("sensitiveFields", "N/A")}')
                
            else:
                print(f'❌ Failed: HTTP {response.status_code}')
                
        except Exception as e:
            print(f'❌ Error: {str(e)}')
    
    # Show comparison table
    print('\n\n📊 RESULTS COMPARISON - PROVING UNIQUENESS')
    print('=' * 80)
    
    for i, result in enumerate(results, 1):
        print(f'\n{i}. {result["filename"]}:')
        print(f'   📝 Description: {result["description"][:80]}...')
        print(f'   🎯 Risk: {result["risk_level"]} | Quality: {result["quality"]} | Sensitive: {result["sensitive_fields"]}')
        if result["key_findings"]:
            print(f'   🔑 Key Finding: {result["key_findings"][0]}')
    
    # Verify uniqueness
    descriptions = [r["description"] for r in results]
    unique_descriptions = set(descriptions)
    
    print(f'\n🎯 UNIQUENESS VERIFICATION:')
    print(f'   Total files analyzed: {len(results)}')
    print(f'   Unique descriptions: {len(unique_descriptions)}')
    
    if len(unique_descriptions) == len(results):
        print('   ✅ SUCCESS: All files have UNIQUE analysis results!')
    else:
        print('   ⚠️  WARNING: Some files have duplicate results')
        
    return results

if __name__ == "__main__":
    test_fresh_analysis()
