import pytest
from unittest.mock import MagicMock, patch
import tempfile
import os

from server.extractors.txt_extractor import TXTExtractor
from server.extractors.csv_extractor import CSVExtractor
from server.extractors.pdf_extractor import PDFExtractor

def test_txt_extractor():
    extractor = TXTExtractor()
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
        tmp.write("Hello, this is a test text file containing an email: test@example.com.")
        tmp_path = tmp.name
    
    try:
        content = extractor.extract(tmp_path)
        assert "text" in content
        assert "test@example.com" in content["text"]
        assert "Hello" in content["text"]
    finally:
        os.unlink(tmp_path)

def test_csv_extractor():
    extractor = CSVExtractor()
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
        tmp.write("Name,Email,Phone\nJohn Doe,john@example.com,555-1234\nJane Doe,jane@example.com,555-5678")
        tmp_path = tmp.name
        
    try:
        content = extractor.extract(tmp_path)
        assert "headers" in content
        assert "rows" in content
        assert "Name" in content["headers"]
        assert "john@example.com" in content["rows"][0]
        assert "555-5678" in content["rows"][1]
    finally:
        os.unlink(tmp_path)

@patch('pdfplumber.open')
def test_pdf_extractor(mock_pdf_open):
    # Mocking pdfplumber
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Mocked PDF content with SSN 000-00-0000"
    mock_page.extract_tables.return_value = []
    mock_pdf.pages = [mock_page]
    mock_pdf.metadata = {}
    mock_pdf_open.return_value.__enter__.return_value = mock_pdf
    
    extractor = PDFExtractor()
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as tmp:
        tmp_path = tmp.name
        
    try:
        content = extractor.extract(tmp_path, enable_ocr=False)
        assert "text_content" in content
        assert len(content["text_content"]) > 0
        assert "Mocked PDF content" in content["text_content"][0]["text"]
        assert "000-00-0000" in content["text_content"][0]["text"]
    finally:
        os.unlink(tmp_path)
