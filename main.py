"""
Main script to demonstrate the file processing and sensitive data masking system.
"""

import os
import json
from pathlib import Path
from file_processor import FileProcessor


def main():
    """Main function to demonstrate the system."""
    
    print("=== File Processing and Sensitive Data Masking System ===\n")
    
    # Initialize the file processor
    # Enable local NER detector for model-based redaction
    processor = FileProcessor(use_model_detector=True, enable_logo_redaction=True, enable_ocr=True)
    
    # Define sample files directory
    sample_files_dir = "Files"
    
    # Get all files in the sample directory
    if os.path.exists(sample_files_dir):
        sample_files = [os.path.join(sample_files_dir, f) for f in os.listdir(sample_files_dir)]
        print(f"Found {len(sample_files)} sample files to process:\n")
        
        for file_path in sample_files:
            print(f"  - {os.path.basename(file_path)}")
        
        print("\n" + "="*60)
        
        # Process each file
        results = []
        for file_path in sample_files:
            print(f"\nProcessing: {os.path.basename(file_path)}")
            print("-" * 40)
            
            try:
                # Process file with sensitive data masking
                result = processor.process_file(file_path, mask_sensitive=True)
                results.append(result)
                
                # Display basic info
                file_info = result["file_info"]
                extraction_meta = result["extraction_metadata"]
                
                print(f"File Type: {file_info['type']}")
                print(f"File Size: {file_info['size_bytes']} bytes")
                print(f"Extraction Success: {extraction_meta['success']}")
                print(f"Extractor Used: {extraction_meta['extractor_used']}")
                print(f"Masking Applied: {result.get('masking_applied', False)}")
                
                if not extraction_meta['success']:
                    print(f"Error: {extraction_meta['error']}")
                else:
                    # Show content summary
                    content = result["content"]
                    if file_info['type'] == 'application/pdf':
                        print(f"Pages: {content.get('page_count', 0)}")
                        print(f"Text sections: {len(content.get('text_content', []))}")
                        print(f"Tables: {len(content.get('tables', []))}")
                    elif 'application/vnd.openxmlformats-officedocument.presentationml.presentation' in file_info['type']:
                        print(f"Slides: {content.get('slide_count', 0)}")
                    elif 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in file_info['type']:
                        print(f"Sheets: {content.get('sheet_count', 0)}")
                    elif file_info['type'].startswith('image/'):
                        img_info = content.get('image_info', {})
                        print(f"Image Size: {img_info.get('width', 0)}x{img_info.get('height', 0)}")
                        print(f"Format: {img_info.get('format', 'Unknown')}")
                
            except Exception as e:
                print(f"Error processing file: {str(e)}")
        
        # Save results to JSON file
        output_file = "processing_results.json"
        processor.save_results(results, output_file)
        print(f"\n\nResults saved to: {output_file}")
        
        # Display summary
        print("\n" + "="*60)
        print("PROCESSING SUMMARY")
        print("="*60)
        
        successful = sum(1 for r in results if r["extraction_metadata"]["success"])
        total = len(results)
        
        print(f"Total files processed: {total}")
        print(f"Successfully processed: {successful}")
        print(f"Failed: {total - successful}")
        
        # Show file type breakdown
        file_types = {}
        for result in results:
            file_type = result["file_info"]["type"]
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        print(f"\nFile type breakdown:")
        for file_type, count in file_types.items():
            print(f"  {file_type}: {count} files")
    
    else:
        print(f"Sample files directory '{sample_files_dir}' not found.")
        print("Please ensure the Files directory exists with sample files.")


def test_sensitive_data_masking():
    """Test the sensitive data masking functionality."""
    
    print("\n" + "="*60)
    print("TESTING SENSITIVE DATA MASKING")
    print("="*60)
    
    from sensitive_data_masking import SensitiveDataMasker
    
    masker = SensitiveDataMasker()
    
    # Test data with various sensitive information
    test_data = {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "ssn": "123-45-6789",
            "dob": "01/15/1985"
        },
        "financial_info": {
            "credit_card": "4532-1234-5678-9012",
            "bank_account": "1234567890123456",
            "routing": "021000021"
        },
        "network_info": {
            "ip_address": "192.168.1.100",
            "url": "https://secure.example.com/login"
        },
        "documents": [
            "Passport: A1234567",
            "Driver License: D9876543"
        ]
    }
    
    print("Original data:")
    print(json.dumps(test_data, indent=2))
    
    # Mask sensitive data
    masked_data = masker.mask_sensitive_data(test_data)
    
    print("\nMasked data:")
    print(json.dumps(masked_data, indent=2))
    
    # Generate detection report
    report = masker.generate_masking_report(test_data)
    
    print("\nDetection report:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    # Run main processing
    main()
    
    # Test sensitive data masking
    test_sensitive_data_masking()
