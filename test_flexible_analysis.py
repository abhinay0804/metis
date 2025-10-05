#!/usr/bin/env python3
"""
Test the flexible analysis system on multiple files
"""

from file_processor import FileProcessor
from server.analysis.advanced_analyzer import AdvancedDataAnalyzer
import os

def test_flexible_analysis():
    """Test flexible analysis on different file types"""
    
    processor = FileProcessor(enable_ocr=True)
    analyzer = AdvancedDataAnalyzer()
    
    # Test different files
    test_files = [
        'Files/File_001.png',  # Access card reader
        'Files/File_005.png',  # Network diagram  
        'Files/File_008.xlsx', # Spreadsheet
        'Files/File_012.pdf',  # PDF document
        'Files/File_014.pptx'  # PowerPoint
    ]
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            continue
            
        print(f"\n{'='*60}")
        print(f"Testing: {file_path}")
        print('='*60)
        
        try:
            # Get file type and extract content
            file_type = processor.get_file_type(file_path)
            extractor = processor.extractors.get(file_type)
            
            if file_type == "application/pdf":
                content = extractor.extract(file_path, enable_ocr=True)
            else:
                content = extractor.extract(file_path)
            
            # Run analysis
            result = analyzer.analyze(content, file_type)
            
            print(f"File Type: {file_type}")
            print(f"Description: {result['description']}")
            print(f"Risk Level: {result['riskLevel']}")
            print(f"Data Quality: {result['dataQuality']}")
            print(f"Categories: {', '.join(result.get('contentCategories', []))}")
            
            print("\nKey Findings:")
            for i, finding in enumerate(result['keyFindings'], 1):
                print(f"  {i}. {finding}")
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

if __name__ == "__main__":
    test_flexible_analysis()
