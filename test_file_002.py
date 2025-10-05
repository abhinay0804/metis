#!/usr/bin/env python3
"""
Test File_002.png analysis
"""

from file_processor import FileProcessor
from server.analysis.advanced_analyzer import AdvancedDataAnalyzer

def test_file_002():
    p = FileProcessor(enable_ocr=True)
    a = AdvancedDataAnalyzer()
    
    content = p.extractors['image/png'].extract('Files/File_002.png')
    info = content['image_info']
    
    ratio = info['width'] / info['height']
    print(f'Dimensions: {info["width"]}x{info["height"]}')
    print(f'Aspect Ratio: {ratio:.3f}')
    
    # Determine category
    if 1.7 <= ratio <= 1.8:
        category = "System Interface Screenshot"
    elif 1.3 <= ratio <= 1.4:
        category = "Security Monitor Display"
    elif ratio > 2:
        category = "Network Infrastructure Layout"
    elif 0.7 <= ratio <= 1.3:
        category = "Access Control Panel"
    else:
        category = "Security System Interface"
    
    print(f'Category: {category}')
    
    # Run full analysis
    result = a.analyze(content, 'image/png')
    print(f'\nDescription: {result["description"]}')
    print('Key Findings:')
    for i, f in enumerate(result['keyFindings'], 1):
        print(f'  {i}. {f}')

if __name__ == "__main__":
    test_file_002()









