#!/usr/bin/env python3
"""
Test the enhanced analysis on File_001.png
"""

import os
from file_processor import FileProcessor
from server.analysis.advanced_analyzer import AdvancedDataAnalyzer

def test_file_001():
    """Test enhanced analysis on File_001.png"""
    
    print("Testing Enhanced Analysis on File_001.png")
    print("=" * 50)
    
    processor = FileProcessor(use_model_detector=True, enable_logo_redaction=True, enable_ocr=True)
    analyzer = AdvancedDataAnalyzer()
    
    file_path = 'Files/File_001.png'
    
    if not os.path.exists(file_path):
        print('File_001.png not found')
        return
    
    # Extract content
    file_type = processor.get_file_type(file_path)
    extractor = processor.extractors.get(file_type)
    content = extractor.extract(file_path)
    
    # Show OCR content
    ocr_text = content.get("ocr_text", "").strip()
    print(f"OCR Text: '{ocr_text}'")
    print(f"OCR Length: {len(ocr_text)} characters")
    
    # Run analysis
    result = analyzer.analyze(content, file_type)
    
    print("\nENHANCED ANALYSIS RESULTS:")
    print("-" * 30)
    print(f"Description: {result['description']}")
    print(f"Risk Level: {result['riskLevel']}")
    print(f"Data Quality: {result['dataQuality']}")
    print(f"Sensitive Fields: {result['sensitiveFields']}")
    
    print("\nKey Findings:")
    for i, finding in enumerate(result['keyFindings'], 1):
        print(f"  {i}. {finding}")
    
    categories = result.get('contentCategories', [])
    if categories:
        print(f"\nCategories: {', '.join(categories)}")

if __name__ == "__main__":
    test_file_001()









