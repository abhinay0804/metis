"""
Sensitive data detection and masking functionality.
"""

import re
import json
from typing import Dict, Any, List, Union, Optional
import hashlib


class SensitiveDataMasker:
    """
    Detect and mask sensitive information in extracted content.
    Phase 1 redaction policy: replace detected sensitive values with the literal
    string "[REDACT]". Additionally, redact values based on sensitive key names
    (e.g., name, email, ssn) regardless of the value content.
    """
    
    def __init__(self, use_model_detector: bool = False, ner_model: Optional[str] = None):
        # Define patterns for sensitive data detection
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
            'date_of_birth': r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12][0-9]|3[01])[-/](19|20)\d{2}\b',
            'bank_account': r'\b\d{8,17}\b',  # Basic pattern for account numbers
            'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
            'driver_license': r'\b[A-Z]\d{7,8}\b'
        }
        
        # Sensitive keys for key-based redaction (case-insensitive)
        self.sensitive_keys = {
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

        # Optional model-based NER detector
        self.use_model_detector = use_model_detector
        self.ner = None
        if self.use_model_detector:
            try:
                from detectors.ner_detector import NERDetector
                self.ner = NERDetector(model=ner_model or "dslim/bert-base-NER")
            except Exception as e:  # Fallback silently to regex-only
                self.use_model_detector = False
    
    def _redact_pattern(self, text: str, pattern_key: str) -> str:
        """Replace all matches of a pattern with [REDACT]."""
        return re.sub(self.patterns[pattern_key], '[REDACT]', text, flags=re.IGNORECASE)
    
    def detect_sensitive_data(self, text: str) -> Dict[str, List[str]]:
        """
        Detect sensitive data in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with detected sensitive data types and values
        """
        detected = {}
        
        for data_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[data_type] = list(set(matches))  # Remove duplicates
        
        return detected
    
    def mask_text(self, text: str) -> str:
        """
        Mask sensitive data in text.
        
        Args:
            text: Text to mask
            
        Returns:
            Masked text
        """
        masked_text = text
        
        for data_type in self.patterns.keys():
            masked_text = self._redact_pattern(masked_text, data_type)

        # Optional NER redaction (names, orgs, locations, etc.)
        if self.use_model_detector and self.ner is not None:
            masked_text = self.ner.redact_text(masked_text, placeholder='[REDACT]')
        
        return masked_text
    
    def mask_sensitive_data(self, content: Union[Dict, List, str]) -> Union[Dict, List, str]:
        """
        Recursively mask sensitive data in content structure.
        
        Args:
            content: Content to mask (can be dict, list, or string)
            
        Returns:
            Content with sensitive data masked
        """
        if isinstance(content, str):
            return self.mask_text(content)
        
        elif isinstance(content, dict):
            masked_dict = {}
            for key, value in content.items():
                key_lower = str(key).lower()
                if key_lower in self.sensitive_keys:
                    masked_dict[key] = "[REDACT]"
                else:
                    masked_dict[key] = self.mask_sensitive_data(value)
            return masked_dict
        
        elif isinstance(content, list):
            return [self.mask_sensitive_data(item) for item in content]
        
        else:
            return content
    
    def generate_masking_report(self, original_content: Union[Dict, List, str]) -> Dict[str, Any]:
        """
        Generate a report of what sensitive data was detected and masked.
        
        Args:
            original_content: Original content before masking
            
        Returns:
            Report with detected sensitive data
        """
        report = {
            "total_detections": 0,
            "detected_types": {},
            "sample_detections": {}
        }
        
        def analyze_content(content, path=""):
            if isinstance(content, str):
                detected = self.detect_sensitive_data(content)
                if detected:
                    report["detected_types"].update(detected)
                    report["total_detections"] += sum(len(values) for values in detected.values())
                    
                    # Store sample detections with context
                    for data_type, values in detected.items():
                        if data_type not in report["sample_detections"]:
                            report["sample_detections"][data_type] = []
                        report["sample_detections"][data_type].extend(values[:3])  # Store first 3 examples
            
            elif isinstance(content, dict):
                for key, value in content.items():
                    analyze_content(value, f"{path}.{key}" if path else key)
            
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    analyze_content(item, f"{path}[{i}]" if path else f"[{i}]")
        
        analyze_content(original_content)
        
        return report


if __name__ == "__main__":
    # Example usage
    masker = SensitiveDataMasker()
    
    # Test text
    test_text = """
    Contact John Doe at john.doe@example.com or call (555) 123-4567.
    SSN: 123-45-6789
    Credit Card: 4532-1234-5678-9012
    IP: 192.168.1.1
    """
    
    print("Original text:")
    print(test_text)
    print("\nMasked text:")
    print(masker.mask_text(test_text))
    print("\nDetection report:")
    print(json.dumps(masker.generate_masking_report(test_text), indent=2))
