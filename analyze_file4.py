#!/usr/bin/env python3
"""
Analyze File_004.png to understand its content
"""

import os
from file_processor import FileProcessor
from server.analysis.advanced_analyzer import AdvancedDataAnalyzer

def analyze_file4():
    """Analyze File_004.png content"""
    
    processor = FileProcessor()
    analyzer = AdvancedDataAnalyzer()
    file_path = 'Files/File_004.png'
    
    if not os.path.exists(file_path):
        print('File_004.png not found')
        return
    
    print('🔍 ANALYZING FILE_004.PNG')
    print('=' * 50)
    
    # Get file type and extract content
    file_type = processor.get_file_type(file_path)
    print(f'📄 File Type: {file_type}')
    
    extractor = processor.extractors.get(file_type)
    if not extractor:
        print('❌ No extractor available')
        return
    
    # Extract content
    content = extractor.extract(file_path)
    print(f'📋 Content Keys: {list(content.keys())}')
    
    # Show image info
    if 'image_info' in content:
        info = content['image_info']
        print(f'🖼️  Image Size: {info.get("width")}x{info.get("height")}')
        print(f'📐 Format: {info.get("format")}')
    
    # Show OCR text
    if 'ocr_text' in content:
        ocr = content['ocr_text'].strip()
        print(f'📝 OCR Text Length: {len(ocr)} characters')
        if ocr:
            print(f'📖 OCR Sample: {repr(ocr[:100])}')
        else:
            print('📖 OCR: No text detected')
    
    print('\n🤖 ADVANCED ANALYZER RESULTS')
    print('=' * 50)
    
    # Run advanced analysis
    result = analyzer.analyze(content, file_type)
    
    print(f'📝 Description: {result["description"]}')
    print(f'🎯 Risk Level: {result["riskLevel"]}')
    print(f'📈 Data Quality: {result["dataQuality"]}')
    print(f'🔒 Sensitive Fields: {result["sensitiveFields"]}')
    
    categories = result.get('contentCategories', [])
    if categories:
        print(f'📂 Categories: {", ".join(categories)}')
    
    print('🔑 Key Findings:')
    for i, finding in enumerate(result['keyFindings'], 1):
        print(f'   {i}. {finding}')

if __name__ == "__main__":
    analyze_file4()
