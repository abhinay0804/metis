# File Processing and Sensitive Data Masking System

A comprehensive system for extracting content from various file types and masking sensitive information.

## Features

- **Multi-format Support**: Handles PDF, PowerPoint, Excel, and Image files
- **Content Extraction**: Extracts text, tables, metadata, and images
- **Sensitive Data Detection**: Automatically detects various types of sensitive information
- **Data Masking**: Masks sensitive data while preserving structure
- **JSON Output**: Standardized JSON format for all extracted content

## Supported File Types

| File Type | Library Used | Extracted Content |
|-----------|--------------|-------------------|
| PDF | pdfplumber | Text, tables, images, metadata |
| PowerPoint (.pptx) | python-pptx | Slides, text, tables, shapes |
| Excel (.xlsx, .xls) | openpyxl | Worksheets, data, formulas |
| Images (JPG, PNG, etc.) | PIL | Base64 encoded data, metadata |

## Sensitive Data Types Detected

- Email addresses
- Phone numbers
- Social Security Numbers (SSN)
- Credit card numbers
- IP addresses
- URLs
- Dates of birth
- Bank account numbers
- Passport numbers
- Driver license numbers

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. For Windows users, you may need to install python-magic-bin:
```bash
pip install python-magic-bin
```

## Usage

### Basic Usage

```python
from file_processor import FileProcessor

processor = FileProcessor()

result = processor.process_file("document.pdf", mask_sensitive=True)

results = processor.process_multiple_files(["file1.pdf", "file2.pptx"])

processor.save_results(results, "output.json")
```

### Running the Demo

```bash
python main.py
```

This will process all files in the `Files` directory and demonstrate the sensitive data masking functionality.

## Project Structure

```
├── file_processor.py          # Main file processor
├── sensitive_data_masking.py  # Sensitive data detection and masking
├── extractors/                # File type specific extractors
│   ├── __init__.py
│   ├── pdf_extractor.py
│   ├── ppt_extractor.py
│   ├── excel_extractor.py
│   └── image_extractor.py
├── main.py                    # Demo script
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Output Format

The system outputs a standardized JSON structure:

```json
{
  "file_info": {
    "name": "document.pdf",
    "path": "/path/to/document.pdf",
    "type": "application/pdf",
    "size_bytes": 1024000
  },
  "content": {
    "text_content": [...],
    "tables": [...],
    "metadata": {...}
  },
  "extraction_metadata": {
    "success": true,
    "error": null,
    "extractor_used": "PDFExtractor"
  },
  "masking_applied": true
}
```

## Masking Examples

| Original | Masked |
|----------|--------|
| john.doe@example.com | j***e@example.com |
| (555) 123-4567 | ***-***-4567 |
| 123-45-6789 | ***-**-6789 |
| 4532-1234-5678-9012 | ****-****-****-9012 |
| 192.168.1.1 | ***.***.***.*** |

## Customization

### Adding New File Types

1. Create a new extractor in the `extractors/` directory
2. Implement the `extract(file_path)` method
3. Add the MIME type mapping in `FileProcessor.__init__()`

### Adding New Sensitive Data Patterns

1. Add regex pattern to `SensitiveDataMasker.patterns`
2. Implement masking function in `SensitiveDataMasker.masking_strategies`
3. Update the `mask_sensitive_data()` method if needed

## Error Handling

The system includes comprehensive error handling:
- File not found errors
- Unsupported file types
- Extraction failures
- Invalid file formats

All errors are captured in the output metadata for debugging.

## Future Enhancements

- OCR support for scanned documents
- Advanced image analysis
- Custom sensitive data patterns
- Batch processing optimization
- API endpoint for web integration
