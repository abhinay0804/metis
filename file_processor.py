"""
File Processor for extracting content from various file types and masking sensitive data.
Supports PDF, PowerPoint, Excel, and Image files.
"""

import os
import json
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path

# Try to import magic, fallback to mimetypes if not available
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    import mimetypes
    HAS_MAGIC = False

# Import specific extractors
from extractors.pdf_extractor import PDFExtractor
from extractors.ppt_extractor import PPTExtractor
from extractors.excel_extractor import ExcelExtractor
from extractors.image_extractor import ImageExtractor
from extractors.docx_extractor import DOCXExtractor
from extractors.txt_extractor import TXTExtractor
from extractors.csv_extractor import CSVExtractor
from sensitive_data_masking import SensitiveDataMasker


class FileProcessor:
    """
    Main file processor that handles different file types and extracts content to JSON format.
    """
    
    def __init__(self, use_model_detector: bool = False, ner_model: str = None, enable_logo_redaction: bool = True, enable_ocr: bool = True):
        self.extractors = {
            'application/pdf': PDFExtractor(),
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': PPTExtractor(),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ExcelExtractor(),
            'application/vnd.ms-excel': ExcelExtractor(),
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DOCXExtractor(),
            'image/jpeg': ImageExtractor(enable_logo_redaction=enable_logo_redaction, enable_ocr=enable_ocr),
            'image/png': ImageExtractor(enable_logo_redaction=enable_logo_redaction, enable_ocr=enable_ocr),
            'image/jpg': ImageExtractor(enable_logo_redaction=enable_logo_redaction, enable_ocr=enable_ocr),
            'text/plain': TXTExtractor(),
            'text/csv': CSVExtractor(),
        }
        self.masker = SensitiveDataMasker(use_model_detector=use_model_detector, ner_model=ner_model)
    
    def get_file_type(self, file_path: str) -> str:
        """Get MIME type of the file."""
        if HAS_MAGIC:
            try:
                mime = magic.from_file(file_path, mime=True)
                return mime
            except Exception as e:
                print(f"Error detecting file type with magic: {e}")
        
        # Fallback to extension-based detection
        ext = Path(file_path).suffix.lower()
        ext_mapping = {
            '.pdf': 'application/pdf',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain',
            '.csv': 'text/csv'
        }
        return ext_mapping.get(ext, 'unknown')
    
    def process_file(self, file_path: str, mask_sensitive: bool = True) -> Dict[str, Any]:
        """
        Process a file and extract content to JSON format.
        
        Args:
            file_path: Path to the file to process
            mask_sensitive: Whether to mask sensitive data
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_type = self.get_file_type(file_path)
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path)
        
        # Initialize result structure
        result = {
            "file_info": {
                "name": file_name,
                "path": file_path,
                "type": file_type,
                "size_bytes": file_size
            },
            "content": {},
            "extraction_metadata": {
                "success": False,
                "error": None,
                "extractor_used": None
            }
        }
        
        try:
            # Get appropriate extractor
            extractor = self.extractors.get(file_type)
            if not extractor:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Extract content
            content = extractor.extract(file_path)
            result["content"] = content
            result["extraction_metadata"]["success"] = True
            result["extraction_metadata"]["extractor_used"] = extractor.__class__.__name__
            
            # Mask sensitive data if requested
            if mask_sensitive:
                masked_content = self.masker.mask_sensitive_data(content)
                result["content"] = masked_content
                result["masking_applied"] = True
            else:
                result["masking_applied"] = False
                
        except Exception as e:
            result["extraction_metadata"]["error"] = str(e)
            result["extraction_metadata"]["success"] = False
        
        return result
    
    def process_multiple_files(self, file_paths: List[str], mask_sensitive: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple files and return list of results.
        
        Args:
            file_paths: List of file paths to process
            mask_sensitive: Whether to mask sensitive data
            
        Returns:
            List of dictionaries containing extracted content and metadata
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.process_file(file_path, mask_sensitive)
                results.append(result)
            except Exception as e:
                error_result = {
                    "file_info": {
                        "name": Path(file_path).name,
                        "path": file_path,
                        "type": "unknown",
                        "size_bytes": 0
                    },
                    "content": {},
                    "extraction_metadata": {
                        "success": False,
                        "error": str(e),
                        "extractor_used": None
                    },
                    "masking_applied": False
                }
                results.append(error_result)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str):
        """
        Save processing results to a JSON file.
        
        Args:
            results: List of processing results
            output_path: Path to save the JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Example usage
    processor = FileProcessor()
    
    # Process a single file
    # result = processor.process_file("path/to/file.pdf")
    # print(json.dumps(result, indent=2))
    
    # Process multiple files
    # results = processor.process_multiple_files(["file1.pdf", "file2.pptx"])
    # processor.save_results(results, "extraction_results.json")
