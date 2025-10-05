"""
PDF content extractor using pdfplumber.
"""

import pdfplumber
import pytesseract
from pdfplumber.page import Page
from PIL import Image as PILImage
import io
from typing import Dict, Any, List
import json


class PDFExtractor:
    """Extract text, tables, and metadata from PDF files."""
    
    def extract(self, file_path: str, enable_ocr: bool = True) -> Dict[str, Any]:
        """
        Extract content from PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted content
        """
        content = {
            "text_content": [],
            "tables": [],
            "metadata": {},
            "images": [],
            "page_count": 0
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                content["page_count"] = len(pdf.pages)
                content["metadata"] = pdf.metadata or {}
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        content["text_content"].append({
                            "page": page_num,
                            "text": text.strip()
                        })
                    elif enable_ocr:
                        # OCR rasterized page
                        try:
                            pil_img = self._page_to_image(page)
                            ocr_text = pytesseract.image_to_string(pil_img)
                            if ocr_text.strip():
                                content["text_content"].append({
                                    "page": page_num,
                                    "text": ocr_text.strip(),
                                    "source": "ocr"
                                })
                        except Exception:
                            pass
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table_num, table in enumerate(tables, 1):
                            content["tables"].append({
                                "page": page_num,
                                "table_number": table_num,
                                "data": table
                            })
                    
                    # Extract images (basic info)
                    images = page.images
                    if images:
                        for img_num, img in enumerate(images, 1):
                            content["images"].append({
                                "page": page_num,
                                "image_number": img_num,
                                "bbox": img.get("bbox", []),
                                "x0": img.get("x0", 0),
                                "y0": img.get("y0", 0),
                                "x1": img.get("x1", 0),
                                "y1": img.get("y1", 0)
                            })
        
        except Exception as e:
            raise Exception(f"Error extracting PDF content: {str(e)}")
        
        return content

    def _page_to_image(self, page: Page) -> PILImage:
        # Render page to image via pdfplumber's underlying pypdfium2
        # Use page.to_image() which returns a Rasterized object
        raster = page.to_image(resolution=200)
        buf = io.BytesIO()
        raster.original.save(buf, format='PNG')
        buf.seek(0)
        return PILImage.open(buf)
