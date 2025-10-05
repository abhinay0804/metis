#!/usr/bin/env python3
"""
Test multiple image files to verify content-driven analysis
"""

from file_processor import FileProcessor
from server.analysis.advanced_analyzer import AdvancedDataAnalyzer
import os

def test_multiple_images():
    """Test content-driven analysis on multiple image files"""
    
    processor = FileProcessor(enable_ocr=True)
    analyzer = AdvancedDataAnalyzer()
    
    # Test different image files
    test_files = [
        'Files/File_001.png',
        'Files/File_002.png', 
        'Files/File_003.png',
        'Files/File_004.png',
        'Files/File_005.png'
    ]
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            continue
            
        print(f"\n{'='*50}")
        print(f"Testing: {file_path}")
        print('='*50)
        
        try:
            # Extract content
            content = processor.extractors['image/png'].extract(file_path)
            ocr_text = content.get('ocr_text', '').strip()
            
            # Run analysis
            result = analyzer.analyze(content, 'image/png')
            
            print(f"OCR Text: {repr(ocr_text)}")
            print(f"OCR Length: {len(ocr_text)} characters")
            print(f"Description: {result['description']}")
            print("Key Findings:")
            for i, finding in enumerate(result['keyFindings'], 1):
                print(f"  {i}. {finding}")
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

if __name__ == "__main__":
    test_multiple_images()









