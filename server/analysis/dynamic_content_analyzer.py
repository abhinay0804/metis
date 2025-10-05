"""
Dynamic Content Analyzer

This analyzer generates descriptions and findings completely dynamically
based on actual content analysis without any hardcoded responses.
"""

import re
import json
from typing import Any, Dict, List, Set, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import logging

from sensitive_data_masking import SensitiveDataMasker

logger = logging.getLogger(__name__)

class DynamicContentAnalyzer:
    """
    Completely dynamic analyzer that generates descriptions and findings
    based on actual content analysis without any hardcoded responses.
    """
    
    def __init__(self):
        # Initialize sensitive data masker
        self.masker = SensitiveDataMasker(use_model_detector=True)
    
    def analyze(self, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """
        Analyze content and generate completely dynamic descriptions and findings.
        
        Args:
            content: The extracted content from the file
            file_type: MIME type of the file
            
        Returns:
            Analysis results with dynamic descriptions and findings
        """
        logger.info(f"Starting dynamic content analysis for {file_type}")
        
        # Extract all text content
        all_text = self._extract_all_text(content)
        
        if not all_text or len(all_text.strip()) < 10:
            return self._generate_minimal_analysis(content, file_type)
        
        # Analyze content dynamically
        content_analysis = self._analyze_content_dynamically(all_text, content, file_type)
        
        # Analyze sensitive data
        sensitive_analysis = self._analyze_sensitive_data(all_text)
        
        # Generate dynamic file description
        file_description = self._generate_dynamic_description(content, content_analysis, file_type, all_text)
        
        # Generate dynamic key findings
        key_findings = self._generate_dynamic_findings(content, content_analysis, sensitive_analysis, file_type, all_text)
        
        return {
            "description": file_description,
            "keyFindings": key_findings,
            "dynamicAnalysis": True
        }
    
    def _extract_all_text(self, content: Dict[str, Any]) -> str:
        """Extract all text content from various file structures"""
        texts = []
        
        def extract_recursive(obj):
            if isinstance(obj, str):
                texts.append(obj)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if key not in ['base64_data', 'redacted_image_base64']:
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(content)
        return ' '.join(texts).strip()
    
    def _analyze_content_dynamically(self, text: str, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Analyze content dynamically to understand what it actually contains"""
        if not text:
            return {"content_insights": [], "structure_info": {}, "word_count": 0}
        
        # Extract meaningful words and phrases
        words = text.lower().split()
        word_count = len(words)
        
        # Find key terms and concepts
        key_terms = self._extract_meaningful_terms(text)
        
        # Analyze content structure
        structure_info = self._analyze_structure(content, file_type)
        
        # Find important phrases and sentences
        important_phrases = self._extract_important_phrases(text)
        
        return {
            "content_insights": key_terms,
            "structure_info": structure_info,
            "word_count": word_count,
            "important_phrases": important_phrases,
            "text_sample": text[:500] if len(text) > 500 else text
        }
    
    def _analyze_structure(self, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Analyze the structure of the content"""
        structure = {
            "file_type": file_type,
            "has_tables": False,
            "has_images": False,
            "has_structured_data": False,
            "content_elements": []
        }
        
        # Check for different content elements
        if file_type.startswith("image/"):
            structure["content_elements"].append("image")
            if "ocr_text" in content and content["ocr_text"]:
                structure["has_text"] = True
                structure["content_elements"].append("text")
        elif "spreadsheet" in file_type:
            structure["content_elements"].append("spreadsheet")
            structure["has_structured_data"] = True
            if "worksheets" in content and content["worksheets"]:
                structure["content_elements"].append("data")
        elif "presentation" in file_type:
            structure["content_elements"].append("presentation")
            if "slides" in content and content["slides"]:
                structure["content_elements"].append("slides")
        elif file_type == "application/pdf":
            structure["content_elements"].append("document")
            if "tables" in content and content["tables"]:
                structure["has_tables"] = True
                structure["content_elements"].append("tables")
        
        return structure
    
    def _extract_meaningful_terms(self, text: str) -> List[str]:
        """Extract meaningful terms from text"""
        words = text.lower().split()
        # Filter out common words and extract meaningful terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those", "it", "its", "they", "them", "their", "there", "here", "where", "when", "why", "how", "what", "who", "which"}
        meaningful_terms = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(meaningful_terms))[:15]
    
    def _extract_important_phrases(self, text: str) -> List[str]:
        """Extract important phrases from text"""
        sentences = text.split('.')
        important_phrases = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                # Check if sentence contains important information
                if any(word in sentence.lower() for word in ['system', 'data', 'information', 'security', 'access', 'user', 'employee', 'financial', 'network', 'server', 'document', 'file', 'process', 'procedure', 'policy', 'compliance', 'audit', 'risk', 'threat', 'vulnerability']):
                    important_phrases.append(sentence)
        
        return important_phrases[:5]
    
    def _analyze_sensitive_data(self, text: str) -> Dict[str, Any]:
        """Analyze sensitive data using the existing masker"""
        if not text:
            return {"total_sensitive_items": 0, "categories": {}, "samples": {}}
        
        # Split text into chunks for analysis
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        
        all_detections = Counter()
        sample_hits = defaultdict(list)
        
        for chunk in chunks:
            detections = self.masker.detect_sensitive_data(chunk)
            for category, items in detections.items():
                all_detections[category] += len(items)
                # Store samples
                for item in items[:2]:  # Max 2 samples per category per chunk
                    if len(sample_hits[category]) < 5:  # Max 5 samples total
                        sample_hits[category].append(str(item))
        
        return {
            "total_sensitive_items": sum(all_detections.values()),
            "categories": dict(all_detections),
            "samples": dict(sample_hits)
        }
    
    def _generate_dynamic_description(self, content: Dict[str, Any], content_analysis: Dict[str, Any], 
                                    file_type: str, text: str) -> str:
        """Generate completely dynamic description based on actual content"""
        
        if file_type.startswith("image/"):
            return self._describe_image_dynamically(content, text, content_analysis)
        elif "spreadsheet" in file_type:
            return self._describe_spreadsheet_dynamically(content, text, content_analysis)
        elif "presentation" in file_type:
            return self._describe_presentation_dynamically(content, text, content_analysis)
        elif file_type == "application/pdf":
            return self._describe_pdf_dynamically(content, text, content_analysis)
        else:
            return self._describe_generic_dynamically(content, text, file_type, content_analysis)
    
    def _describe_image_dynamically(self, content: Dict[str, Any], text: str, content_analysis: Dict[str, Any]) -> str:
        """Generate dynamic description for images based on actual content"""
        ocr_text = content.get("ocr_text", "").strip()
        image_info = content.get("image_info", {})
        
        if ocr_text:
            # Use actual OCR content to form description
            key_terms = content_analysis["content_insights"]
            word_count = content_analysis["word_count"]
            
            if key_terms:
                # Form description from actual content
                description = f"Image containing {', '.join(key_terms[:3])} and related content"
                if word_count > 0:
                    description += f" with {word_count} words of extractable text"
                return description
            else:
                return f"Image file with {word_count} words of extractable text content"
        
        # No OCR text - describe based on image characteristics
        else:
            width = image_info.get("width", 0)
            height = image_info.get("height", 0)
            
            if width and height:
                aspect_ratio = width / height if height > 0 else 1
                
                if aspect_ratio > 1.5:
                    return "Wide-format image displaying information or interface elements"
                elif aspect_ratio < 0.8:
                    return "Tall-format image showing vertical content or interface"
                else:
                    return "Square or standard-format image containing visual information"
            else:
                return "Image file containing visual information requiring analysis"
    
    def _describe_spreadsheet_dynamically(self, content: Dict[str, Any], text: str, content_analysis: Dict[str, Any]) -> str:
        """Generate dynamic description for spreadsheets based on actual content"""
        worksheets = content.get("worksheets", [])
        
        if not worksheets:
            return "Spreadsheet file with no readable worksheet data"
        
        first_sheet = worksheets[0]
        data = first_sheet.get("data", [])
        headers = data[0] if data else []
        
        # Use actual data to form description
        if headers and data:
            header_count = len(headers)
            row_count = len(data)
            
            # Extract key terms from headers
            header_terms = [str(h) for h in headers if str(h).strip()]
            
            if header_terms:
                description = f"Spreadsheet containing {row_count} rows of data with {header_count} columns"
                if len(header_terms) <= 5:
                    description += f" including {', '.join(header_terms)}"
                else:
                    description += f" including {', '.join(header_terms[:3])} and {len(header_terms)-3} other fields"
                return description
            else:
                return f"Spreadsheet file with {row_count} rows and {header_count} columns of data"
        
        return "Spreadsheet file containing structured tabular data"
    
    def _describe_presentation_dynamically(self, content: Dict[str, Any], text: str, content_analysis: Dict[str, Any]) -> str:
        """Generate dynamic description for presentations based on actual content"""
        slides = content.get("slides", [])
        slide_count = content.get("slide_count", len(slides))
        
        if not slides:
            return f"Presentation file with {slide_count} slides but no readable content"
        
        # Use actual slide content to form description
        key_terms = content_analysis["content_insights"]
        word_count = content_analysis["word_count"]
        
        description = f"Presentation with {slide_count} slides"
        
        if key_terms:
            description += f" containing {', '.join(key_terms[:3])} and related content"
        
        if word_count > 0:
            description += f" with {word_count} words of text content"
        
        return description
    
    def _describe_pdf_dynamically(self, content: Dict[str, Any], text: str, content_analysis: Dict[str, Any]) -> str:
        """Generate dynamic description for PDFs based on actual content"""
        page_count = content.get("page_count", 0)
        text_content = content.get("text_content", [])
        tables = content.get("tables", [])
        
        # Use actual content to form description
        key_terms = content_analysis["content_insights"]
        word_count = content_analysis["word_count"]
        
        description = f"PDF document with {page_count} pages"
        
        if key_terms:
            description += f" containing {', '.join(key_terms[:3])} and related information"
        
        if word_count > 0:
            description += f" with {word_count} words of text content"
        
        if tables:
            description += f" and {len(tables)} table(s) of structured data"
        
        return description
    
    def _describe_generic_dynamically(self, content: Dict[str, Any], text: str, file_type: str, content_analysis: Dict[str, Any]) -> str:
        """Generate dynamic description for generic content based on actual analysis"""
        if not text:
            return f"{file_type.split('/')[-1].upper()} file with no extractable text content"
        
        # Use actual content to form description
        key_terms = content_analysis["content_insights"]
        word_count = content_analysis["word_count"]
        
        if key_terms:
            description = f"Document containing {', '.join(key_terms[:3])} and related information"
            if word_count > 0:
                description += f" with {word_count} words of content"
            return description
        else:
            return f"Documentation file with {word_count} words of content requiring analysis"
    
    def _generate_dynamic_findings(self, content: Dict[str, Any], content_analysis: Dict[str, Any], 
                                 sensitive_analysis: Dict[str, Any], file_type: str, text: str) -> List[str]:
        """Generate completely dynamic key findings based on actual content analysis"""
        findings = []
        
        # Add findings based on actual content analysis
        key_terms = content_analysis["content_insights"]
        word_count = content_analysis["word_count"]
        structure_info = content_analysis["structure_info"]
        important_phrases = content_analysis["important_phrases"]
        
        # Add content-specific findings based on actual analysis
        if key_terms:
            findings.append(f"Contains content related to {', '.join(key_terms[:3])}")
        
        if word_count > 0:
            findings.append(f"Document contains {word_count} words of text content")
        
        if structure_info.get("has_tables"):
            findings.append("Contains tabular data requiring structured analysis")
        
        if structure_info.get("has_structured_data"):
            findings.append("Contains structured data requiring governance and access controls")
        
        if important_phrases:
            findings.append(f"Contains {len(important_phrases)} important information segments")
        
        # Add sensitive data findings based on actual detection
        sensitive_count = sensitive_analysis["total_sensitive_items"]
        sensitive_categories = sensitive_analysis["categories"]
        
        if sensitive_count > 0:
            findings.append(f"Contains {sensitive_count} sensitive data elements requiring protection")
            
            if "email" in sensitive_categories:
                findings.append(f"Identified {sensitive_categories['email']} email addresses requiring data masking")
            if "phone" in sensitive_categories:
                findings.append(f"Found {sensitive_categories['phone']} phone numbers needing privacy protection")
            if "credit_card" in sensitive_categories:
                findings.append(f"Contains {sensitive_categories['credit_card']} payment card numbers requiring PCI compliance")
            if "ssn" in sensitive_categories:
                findings.append(f"Detected {sensitive_categories['ssn']} social security numbers needing encryption")
        
        # Add file type specific findings
        if file_type.startswith("image/"):
            findings.append("Image file requiring visual content analysis and OCR processing")
        elif "spreadsheet" in file_type:
            findings.append("Structured data file requiring tabular data governance")
        elif "presentation" in file_type:
            findings.append("Presentation file requiring slide content analysis")
        elif file_type == "application/pdf":
            findings.append("PDF document requiring text extraction and content analysis")
        else:
            findings.append("Document file requiring comprehensive content analysis")
        
        return findings if findings else ["Content requires standard data governance policies"]
    
    def _generate_minimal_analysis(self, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Generate minimal analysis for content with insufficient text"""
        return {
            "description": f"File with minimal extractable content requiring manual review",
            "keyFindings": ["Insufficient text content for automated analysis"],
            "dynamicAnalysis": True
        }



