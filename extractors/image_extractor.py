"""
Image content extractor and processor.
"""

import base64
from PIL import Image
import cv2
import numpy as np
from detectors.logo_redactor import LogoRedactor
import pytesseract
from pytesseract import Output
from typing import Dict, Any
import io
import os
from sensitive_data_masking import SensitiveDataMasker


class ImageExtractor:
    """Extract and process image content."""

    def __init__(self, enable_logo_redaction: bool = True, templates_dir: str = "templates/logos", enable_ocr: bool = True):
        self.enable_logo_redaction = enable_logo_redaction
        self.logo_redactor = LogoRedactor(templates_dir=templates_dir) if enable_logo_redaction else None
        self.enable_ocr = enable_ocr

    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract content from image file.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary containing image information and base64 encoded data
        """
        content = {
            "image_info": {},
            "base64_data": "",
            "file_size": 0,
            "logo_detections": [],
            "redacted_image_base64": "",
            "ocr_text": ""
        }
        
        try:
            # Get file size
            content["file_size"] = os.path.getsize(file_path)
            
            # Open and get image information
            with Image.open(file_path) as img:
                content["image_info"] = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
            
            # Encode original image to base64
            with open(file_path, "rb") as image_file:
                base64_data = base64.b64encode(image_file.read()).decode('utf-8')
                content["base64_data"] = base64_data
            
            # Load image once for potential redactions
            bgr = cv2.imread(file_path, cv2.IMREAD_COLOR)
            redaction_boxes = []  # list of [x1,y1,x2,y2]

            # Optional: logo redaction
            if self.enable_logo_redaction and self.logo_redactor is not None and bgr is not None:
                detections = self.logo_redactor.find_logos(bgr)
                content["logo_detections"] = detections
                for det in detections:
                    x1, y1, x2, y2 = det.get("bbox", [0,0,0,0])
                    redaction_boxes.append([int(x1), int(y1), int(x2), int(y2)])

            # Optional: OCR text from image and redact sensitive text regions
            content["text_redactions"] = []
            tesseract_available = False
            
            if self.enable_ocr:
                # Check if tesseract is available
                try:
                    import subprocess
                    subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
                    tesseract_available = True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    tesseract_available = False
                
                try:
                    if tesseract_available:
                        with Image.open(file_path) as img:
                            # Convert to RGB if necessary for better OCR
                            if img.mode in ('RGBA', 'LA', 'P'):
                                img = img.convert('RGB')
                            ocr_text = pytesseract.image_to_string(img, config='--psm 6')
                            content["ocr_text"] = ocr_text.strip()
                    else:
                        # Fallback: try to detect text-like patterns in filename or use basic analysis
                        content["ocr_text"] = ""
                        content["ocr_error"] = "Tesseract OCR not available - please install tesseract-ocr"
                        print("Warning: Tesseract OCR not available. To enable OCR:")
                        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
                        print("2. Add to PATH or set TESSDATA_PREFIX")
                except Exception as e:
                    content["ocr_text"] = ""
                    content["ocr_error"] = f"OCR failed: {str(e)}"
                    print(f"OCR extraction failed: {str(e)}")
                
                # OCR box detection and redaction (only if tesseract is available)
                if tesseract_available:
                    try:
                        if bgr is not None:
                            data = pytesseract.image_to_data(bgr, output_type=Output.DICT)
                            masker = SensitiveDataMasker(use_model_detector=False)
                            n = len(data.get("text", []))
                            for i in range(n):
                                word = (data["text"][i] or "").strip()
                                conf = float(data.get("conf", ["0"]) [i] or 0)
                                if not word or conf < 50:  # skip low-confidence or empty
                                    continue
                                detected = masker.detect_sensitive_data(word)
                                if detected:  # any sensitive pattern matched
                                    x, y, w, h = int(data["left"][i]), int(data["top"][i]), int(data["width"][i]), int(data["height"][i])
                                    redaction_boxes.append([x, y, x + w, y + h])
                                    content["text_redactions"].append({
                                        "word": word,
                                        "bbox": [x, y, x + w, y + h],
                                        "types": list(detected.keys()),
                                        "confidence": conf,
                                    })
                    except Exception as e:
                        # OCR box redaction best-effort; log error but continue
                        print(f"OCR box detection failed: {str(e)}")
                        pass

            # If we gathered any redaction boxes, render a redacted image
            if bgr is not None and redaction_boxes:
                redacted = bgr.copy()
                for x1, y1, x2, y2 in redaction_boxes:
                    cv2.rectangle(redacted, (x1, y1), (x2, y2), (0, 0, 0), thickness=-1)
                _, buf = cv2.imencode('.png', redacted)
                content["redacted_image_base64"] = base64.b64encode(buf.tobytes()).decode('utf-8')

            # Add MIME type for base64 data
            ext = os.path.splitext(file_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.tiff': 'image/tiff'
            }
            content["mime_type"] = mime_types.get(ext, 'image/jpeg')
        
        except Exception as e:
            raise Exception(f"Error extracting image content: {str(e)}")
        
        return content
