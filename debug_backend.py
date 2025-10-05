#!/usr/bin/env python3
"""
Debug script to test backend components individually
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_backend_components():
    print("Testing Backend Components...")
    print("=" * 50)
    
    # Test 1: Import components
    print("1. Testing imports...")
    try:
        from file_processor import FileProcessor
        from sensitive_data_masking import SensitiveDataMasker
        print("✓ Core components imported successfully")
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 2: Initialize components
    print("\n2. Testing component initialization...")
    try:
        processor = FileProcessor(use_model_detector=True, enable_logo_redaction=True, enable_ocr=True)
        masker = SensitiveDataMasker(use_model_detector=True)
        print("✓ Components initialized successfully")
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return False
    
    # Test 3: Test file processing with a simple text file
    print("\n3. Testing file processing...")
    try:
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test file with email: test@example.com and phone: 555-123-4567")
            temp_file = f.name
        
        # Test file type detection
        file_type = processor.get_file_type(temp_file)
        print(f"  File type detected: {file_type}")
        
        # Test extraction
        extractor = processor.extractors.get(file_type)
        if extractor:
            print("  Extractor found")
            original_content = extractor.extract(temp_file)
            print(f"  Content extracted: {type(original_content)}")
            
            # Test masking
            masked_content = masker.mask_sensitive_data(original_content)
            print(f"  Content masked: {type(masked_content)}")
            print("✓ File processing successful")
        else:
            print("✗ No extractor found for file type")
        
        # Clean up
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"✗ File processing error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Test storage components
    print("\n4. Testing storage components...")
    try:
        from server.storage import LocalMaskedStore, EncryptedLocalStore
        
        masked_store = LocalMaskedStore(base_dir=os.path.join(os.getcwd(), "data"))
        enc_store = EncryptedLocalStore(base_dir=os.path.join(os.getcwd(), "data"))
        
        print("✓ Storage components initialized")
    except Exception as e:
        print(f"✗ Storage error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Component test completed!")
    return True

if __name__ == "__main__":
    test_backend_components()
