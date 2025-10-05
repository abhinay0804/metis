# MASKING IMPLEMENTATION DOCUMENTATION

## Overview
The masking system is a comprehensive solution for detecting and redacting sensitive information from various file types. It provides both pattern-based and model-based detection capabilities, with support for multiple file formats and advanced redaction techniques.

## Core Components

### 1. SensitiveDataMasker (`sensitive_data_masking.py`)

#### **Primary Class: SensitiveDataMasker**
- **Purpose**: Main class for detecting and masking sensitive data
- **Location**: `sensitive_data_masking.py`
- **Key Features**:
  - Pattern-based detection using regex
  - Optional NER (Named Entity Recognition) model integration
  - Key-based redaction for sensitive field names
  - Comprehensive masking report generation

#### **Detection Patterns**
```python
patterns = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
    'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
    'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
    'date_of_birth': r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12][0-9]|3[01])[-/](19|20)\d{2}\b',
    'bank_account': r'\b\d{8,17}\b',
    'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
    'driver_license': r'\b[A-Z]\d{7,8}\b'
}
```

#### **Sensitive Keys for Field-Based Redaction**
```python
sensitive_keys = {
    'name', 'full_name', 'first_name', 'last_name',
    'email', 'email_address',
    'phone', 'phone_number', 'mobile', 'contact',
    'ssn', 'social_security_number',
    'credit_card', 'card', 'card_number',
    'ip', 'ip_address',
    'url', 'link', 'website',
    'dob', 'date_of_birth', 'birthdate',
    'bank_account', 'account_number', 'iban',
    'passport', 'passport_number',
    'driver_license', 'license', 'license_number',
    'address', 'street', 'city', 'state', 'zipcode', 'postal_code',
    'username', 'user', 'userid', 'user_id',
    'password', 'passcode', 'pin', 'token', 'secret'
}
```

#### **Key Methods**

1. **`detect_sensitive_data(text: str) -> Dict[str, List[str]]`**
   - Detects sensitive data patterns in text
   - Returns dictionary with detected types and values
   - Removes duplicates from matches

2. **`mask_text(text: str) -> str`**
   - Masks sensitive data in plain text
   - Applies pattern-based redaction
   - Optional NER-based redaction if model is enabled

3. **`mask_sensitive_data(content: Union[Dict, List, str]) -> Union[Dict, List, str]`**
   - Recursively processes complex data structures
   - Handles dictionaries, lists, and strings
   - Applies key-based redaction for sensitive field names

4. **`generate_masking_report(original_content) -> Dict[str, Any]`**
   - Generates comprehensive report of detected sensitive data
   - Provides statistics and sample detections
   - Useful for audit and compliance purposes

### 2. FileProcessor (`file_processor.py`)

#### **Primary Class: FileProcessor**
- **Purpose**: Main orchestrator for file processing and masking
- **Location**: `file_processor.py`
- **Key Features**:
  - Multi-format file support
  - Integrated masking capabilities
  - Batch processing support
  - Error handling and metadata tracking

#### **Supported File Types**
```python
extractors = {
    'application/pdf': PDFExtractor(),
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': PPTExtractor(),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ExcelExtractor(),
    'application/vnd.ms-excel': ExcelExtractor(),
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DOCXExtractor(),
    'image/jpeg': ImageExtractor(enable_logo_redaction=True, enable_ocr=True),
    'image/png': ImageExtractor(enable_logo_redaction=True, enable_ocr=True),
    'image/jpg': ImageExtractor(enable_logo_redaction=True, enable_ocr=True),
    'text/plain': TXTExtractor(),
    'text/csv': CSVExtractor(),
}
```

#### **Key Methods**

1. **`process_file(file_path: str, mask_sensitive: bool = True) -> Dict[str, Any]`**
   - Processes single file with optional masking
   - Returns structured JSON with content and metadata
   - Handles extraction errors gracefully

2. **`process_multiple_files(file_paths: List[str], mask_sensitive: bool = True) -> List[Dict[str, Any]]`**
   - Batch processing for multiple files
   - Individual error handling per file
   - Returns list of processing results

3. **`get_file_type(file_path: str) -> str`**
   - MIME type detection using python-magic
   - Fallback to extension-based detection
   - Supports all major file formats

### 3. File Extractors (`extractors/`)

#### **PDF Extractor (`pdf_extractor.py`)**
- **Library**: pdfplumber
- **Features**:
  - Text extraction from PDF pages
  - Table extraction and parsing
  - Image extraction and base64 encoding
  - OCR support for scanned documents
  - Metadata extraction

#### **Image Extractor (`image_extractor.py`)**
- **Libraries**: PIL, OpenCV, pytesseract
- **Features**:
  - Base64 encoding of images
  - OCR text extraction
  - Logo detection and redaction
  - Image metadata extraction
  - Sensitive text redaction in OCR results

#### **Excel Extractor (`excel_extractor.py`)**
- **Library**: openpyxl
- **Features**:
  - Worksheet data extraction
  - Formula and value parsing
  - Cell formatting information
  - Multiple sheet support

#### **PowerPoint Extractor (`ppt_extractor.py`)**
- **Library**: python-pptx
- **Features**:
  - Slide content extraction
  - Text and shape parsing
  - Table extraction from slides
  - Image extraction

#### **Word Extractor (`docx_extractor.py`)**
- **Library**: python-docx
- **Features**:
  - Paragraph text extraction
  - Table extraction
  - Document structure parsing
  - Metadata extraction

### 4. Advanced Redaction Features

#### **Logo Redaction (`detectors/logo_redactor.py`)**
- **Purpose**: Detect and redact corporate logos
- **Method**: Template matching using OpenCV
- **Features**:
  - Template-based logo detection
  - Configurable redaction areas
  - Support for multiple logo formats

#### **NER Detector (`detectors/ner_detector.py`)**
- **Purpose**: Named Entity Recognition for advanced redaction
- **Model**: BERT-based NER model (dslim/bert-base-NER)
- **Features**:
  - Person name detection
  - Organization detection
  - Location detection
  - Custom entity redaction

### 5. API Integration (`server/app.py`)

#### **Masking Endpoint**
```python
@app.post("/process", response_model=ProcessResponse)
async def process_file(
    file: UploadFile = File(...),
    user: User = Depends(verify_id_token),
):
```

**Process Flow**:
1. File upload and temporary storage
2. File type detection
3. Content extraction (bypassing masking)
4. Sensitive data masking
5. Storage in Firestore/local storage
6. Return masked content and masking ID

#### **Storage Integration**
- **Firestore**: Primary cloud storage for masked data
- **Local Storage**: Fallback for development/testing
- **Metadata Tracking**: File info, timestamps, user association

### 6. Masking Strategies

#### **Pattern-Based Redaction**
- **Method**: Regex pattern matching
- **Replacement**: `[REDACT]` placeholder
- **Coverage**: 10+ sensitive data types
- **Performance**: Fast, reliable

#### **Key-Based Redaction**
- **Method**: Field name analysis
- **Target**: Sensitive field names (case-insensitive)
- **Replacement**: `[REDACT]` for entire field values
- **Use Case**: Structured data protection

#### **Model-Based Redaction**
- **Method**: NER model inference
- **Model**: BERT-based transformer
- **Entities**: PERSON, ORG, LOC, MISC
- **Performance**: Slower but more comprehensive

### 7. Output Format

#### **Standardized JSON Structure**
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

### 8. Configuration Options

#### **FileProcessor Initialization**
```python
processor = FileProcessor(
    use_model_detector=True,      # Enable NER model
    ner_model="dslim/bert-base-NER",  # NER model name
    enable_logo_redaction=True,   # Enable logo detection
    enable_ocr=True              # Enable OCR for images
)
```

#### **SensitiveDataMasker Initialization**
```python
masker = SensitiveDataMasker(
    use_model_detector=True,     # Enable NER model
    ner_model="dslim/bert-base-NER"  # Custom NER model
)
```

### 9. Error Handling

#### **Comprehensive Error Management**
- **File Not Found**: Graceful handling with error metadata
- **Unsupported Formats**: Clear error messages
- **Extraction Failures**: Partial success with error reporting
- **Model Failures**: Fallback to pattern-based detection
- **Storage Errors**: Retry mechanisms and fallback storage

#### **Error Response Format**
```json
{
  "extraction_metadata": {
    "success": false,
    "error": "Detailed error message",
    "extractor_used": "PDFExtractor"
  }
}
```

### 10. Performance Considerations

#### **Optimization Strategies**
- **Lazy Loading**: Extractors loaded on demand
- **Chunked Processing**: Large files processed in chunks
- **Caching**: Model loading and caching
- **Parallel Processing**: Batch file processing

#### **Resource Management**
- **Memory Usage**: Streaming for large files
- **CPU Usage**: Efficient regex compilation
- **Storage**: Temporary file cleanup
- **Network**: Efficient API responses

### 11. Security Features

#### **Data Protection**
- **No Persistent Storage**: Original files not stored
- **Secure Redaction**: Multiple redaction layers
- **Audit Trail**: Comprehensive logging
- **User Isolation**: Per-user data separation

#### **Compliance Support**
- **GDPR**: Personal data protection
- **HIPAA**: Health information protection
- **PCI-DSS**: Payment card data protection
- **SOX**: Financial data protection

### 12. Testing and Validation

#### **Test Coverage**
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Large file processing
- **Security Tests**: Redaction effectiveness

#### **Test Files**
- `test_single_file.py`: Single file processing
- `test_multiple_images.py`: Batch image processing
- `test_file_types.py`: Format support testing
- `comprehensive_dry_run.py`: Full system testing

### 13. Future Enhancements

#### **Planned Features**
- **Advanced OCR**: Better text extraction from images
- **Custom Models**: Industry-specific NER models
- **Real-time Processing**: Streaming file processing
- **Enhanced Redaction**: Context-aware redaction
- **Audit Dashboard**: Comprehensive reporting interface

#### **Scalability Improvements**
- **Distributed Processing**: Multi-node processing
- **Cloud Integration**: AWS/Azure support
- **API Rate Limiting**: Production-ready throttling
- **Monitoring**: Comprehensive system monitoring

## Usage Examples

### Basic File Masking
```python
from file_processor import FileProcessor

# Initialize processor
processor = FileProcessor(use_model_detector=True)

# Process single file
result = processor.process_file("document.pdf", mask_sensitive=True)

# Process multiple files
results = processor.process_multiple_files(["file1.pdf", "file2.pptx"])
```

### API Usage
```python
import requests

# Upload and mask file
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/process",
        files={"file": f},
        headers={"Authorization": "Bearer <token>"}
    )
    
masked_data = response.json()
```

### Custom Masking
```python
from sensitive_data_masking import SensitiveDataMasker

# Initialize masker
masker = SensitiveDataMasker(use_model_detector=True)

# Detect sensitive data
detected = masker.detect_sensitive_data("Contact: john@example.com")

# Mask sensitive data
masked = masker.mask_text("Contact: john@example.com")

# Generate report
report = masker.generate_masking_report(content)
```

## Conclusion

The masking implementation provides a comprehensive, production-ready solution for sensitive data protection across multiple file formats. It combines pattern-based detection with advanced ML models to ensure thorough data protection while maintaining usability and performance.

The system is designed with security, compliance, and scalability in mind, making it suitable for enterprise environments where data protection is critical.
