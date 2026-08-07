import json
import logging
import re
from typing import Any, Dict
from google import genai
from google.genai import types

from server.sensitive_data_masking import SensitiveDataMasker

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """
    Analyzer that generates genuine high-quality descriptions and findings
    by communicating with the Gemini API.
    """
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.masker = SensitiveDataMasker(use_model_detector=False)
    
    def analyze(self, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """
        Analyze content using Gemini and generate high-quality descriptions and findings.
        
        Args:
            content: The extracted content from the file
            file_type: MIME type of the file
            
        Returns:
            Analysis results matching AnalysisReport schema
        """
        logger.info(f"Starting Gemini content analysis for {file_type}")
        
        # Extract all text content
        all_text = self._extract_all_text(content)
        
        if not all_text or len(all_text.strip()) < 10:
            return self._generate_minimal_analysis()
            
        # Accurately count sensitive fields
        redact_matches = len(re.findall(r'\[REDACT(?:ED)?\]', all_text, re.IGNORECASE))
        
        chunks = [all_text[i:i+1000] for i in range(0, len(all_text), 1000)]
        raw_sensitive_count = 0
        for chunk in chunks:
            detections = self.masker.detect_sensitive_data(chunk)
            for items in detections.values():
                raw_sensitive_count += len(items)
                
        actual_sensitive_count = redact_matches + raw_sensitive_count
        
        # Build prompt for Gemini
        prompt = f"""
You are a Data Security and Privacy Expert. I have extracted text from a file of type: {file_type}.
Please analyze the following text and provide a concise, high-quality description of the document, along with key findings, data quality, risk level, sensitive fields count, and compliance standards.

IMPORTANT INSTRUCTIONS FOR SENSITIVE FIELDS:
1. You MUST identify and count all raw sensitive data (PII, PHI, PCI, financial data, emails, phone numbers, SSNs, personal names, etc.).
2. You MUST ALSO count any occurrences of the "[REDACT]" or "[REDACTED]" placeholders as a sensitive field, as this indicates data that was already found and masked.
3. The "sensitiveFields" count MUST be exactly {actual_sensitive_count}, as pre-calculated by our scanner.
4. Appropriately factor the presence of these {actual_sensitive_count} fields into the "riskLevel" and "compliance".

Format your response as a JSON object matching this structure:
{{
    "description": "string (1-2 paragraphs)",
    "keyFindings": ["string", "string"],
    "dataQuality": "High" | "Medium" | "Low",
    "riskLevel": "High" | "Medium" | "Low",
    "sensitiveFields": integer,
    "compliance": ["string", "string"]
}}
        
Content:
{all_text[:20000]} # Limit context
"""

        try:
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            
            result_json = response.text
            parsed = json.loads(result_json)
            
            return {
                "description": parsed.get("description", "File analyzed by Gemini."),
                "keyFindings": parsed.get("keyFindings", []),
                "dataQuality": parsed.get("dataQuality", "Medium"),
                "riskLevel": parsed.get("riskLevel", "Medium"),
                "sensitiveFields": actual_sensitive_count,
                "compliance": parsed.get("compliance", []),
                "qualityAnalysis": True
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise ValueError(f"Gemini API error: {str(e)}")
            
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

    def _generate_minimal_analysis(self) -> Dict[str, Any]:
        """Generate minimal analysis for content with insufficient text"""
        return {
            "description": "File with minimal extractable content requiring manual review.",
            "keyFindings": ["Insufficient text content for automated analysis."],
            "qualityAnalysis": True
        }
