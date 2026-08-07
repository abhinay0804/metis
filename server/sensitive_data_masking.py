"""
Sensitive data detection and masking functionality.
Uses EnsembleDetector to combine regex and ML-based NER.
"""

import json
from typing import Dict, Any, List, Union, Optional
from server.detectors.ensemble_detector import EnsembleDetector

class SensitiveDataMasker:
    """
    Detect and mask sensitive information in extracted content.
    Phase 2 redaction policy: Uses EnsembleDetector (Regex + NER).
    """
    
    def __init__(self, use_model_detector: bool = True, ner_model: Optional[str] = None):
        self.use_model_detector = use_model_detector
        self.detector = EnsembleDetector(
            use_model_detector=use_model_detector, 
            ner_model=ner_model
        )
        
        # Sensitive keys for dictionary/JSON key-based redaction (case-insensitive)
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
    
    def detect_sensitive_data(self, text: str) -> Dict[str, List[str]]:
        """
        Detect sensitive data in text.
        Returns Dictionary with detected sensitive data types and values.
        """
        detected = {}
        spans = self.detector.detect_entities(text)
        for span in spans:
            pii_type = span["pii_type"]
            val = span["value"]
            if pii_type not in detected:
                detected[pii_type] = []
            if val not in detected[pii_type]:
                detected[pii_type].append(val)
        return detected
    
    def mask_text(self, text: str) -> str:
        """Mask sensitive data in text."""
        return self.detector.redact_text(text, placeholder='[REDACT]')
    
    def mask_sensitive_data(self, content: Union[Dict, List, str]) -> Union[Dict, List, str]:
        """Recursively mask sensitive data in content structure."""
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
        """Generate a report of what sensitive data was detected."""
        report = {
            "total_detections": 0,
            "detected_types": {},
            "sample_detections": {}
        }
        
        def analyze_content(content, path=""):
            if isinstance(content, str):
                detected = self.detect_sensitive_data(content)
                if detected:
                    for dtype, values in detected.items():
                        if dtype not in report["detected_types"]:
                            report["detected_types"][dtype] = 0
                        # Ensure we add the number of detected instances
                        report["detected_types"][dtype] += len(values)
                        
                    report["total_detections"] += sum(len(values) for values in detected.values())
                    
                    # Store sample detections with context
                    for data_type, values in detected.items():
                        if data_type not in report["sample_detections"]:
                            report["sample_detections"][data_type] = []
                        # Avoid duplicates in samples
                        for val in values[:3]:
                            if val not in report["sample_detections"][data_type]:
                                report["sample_detections"][data_type].append(val)
                        report["sample_detections"][data_type] = report["sample_detections"][data_type][:3]
            
            elif isinstance(content, dict):
                for key, value in content.items():
                    analyze_content(value, f"{path}.{key}" if path else key)
            
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    analyze_content(item, f"{path}[{i}]" if path else f"[{i}]")
        
        analyze_content(original_content)
        
        # Ensure detected_types values are ints (just to be safe, since they were lists before)
        return report

if __name__ == "__main__":
    masker = SensitiveDataMasker()
    test_text = "Contact John Doe at john.doe@example.com or call (555) 123-4567. SSN: 123-45-6789."
    print("Original text:", test_text)
    print("Masked text:", masker.mask_text(test_text))
    print("Report:", json.dumps(masker.generate_masking_report(test_text), indent=2))
