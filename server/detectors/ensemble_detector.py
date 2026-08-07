"""
Ensemble PII Detector.
Combines deterministic regex patterns with ML-based NER detection.
Merges and deduplicates overlapping detections to provide a unified PII extraction list.
"""

import re
from typing import List, Dict, Any, Optional

class EnsembleDetector:
    def __init__(self, use_model_detector: bool = True, ner_model: Optional[str] = None):
        self.use_model_detector = use_model_detector
        self.ner = None
        if self.use_model_detector:
            try:
                from server.detectors.ner_detector import NERDetector
                self.ner = NERDetector(model=ner_model)
            except Exception as e:
                print(f"Failed to load NER detector: {e}")
                self.use_model_detector = False

        # Define high-confidence regex patterns for structured PII
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
            'date_of_birth': r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12][0-9]|3[01])[-/](19|20)\d{2}\b',
            'bank_account': r'\b\d{8,17}\b',
            'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
            'driver_license': r'\b[A-Z]\d{7,8}\b',
            'generic_id': r'\b(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{6,15}\b'
        }

    def detect_regex(self, text: str) -> List[Dict[str, Any]]:
        """Detect entities using regex patterns."""
        spans = []
        for pii_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                spans.append({
                    "start": match.start(),
                    "end": match.end(),
                    "label": pii_type.upper(),
                    "pii_type": pii_type,
                    "score": 1.0,  # Regex gets 100% confidence
                    "value": match.group(0),
                    "source": "regex"
                })
        return spans

    def detect_entities(self, text: str) -> List[Dict[str, Any]]:
        """Run both NER and regex, then merge overlapping spans."""
        if not text:
            return []

        all_spans = self.detect_regex(text)
        
        if self.use_model_detector and self.ner:
            ner_spans = self.ner.detect_entities(text)
            for s in ner_spans:
                s["source"] = "ner"
            all_spans.extend(ner_spans)

        # Merge overlapping spans
        return self._merge_spans(all_spans)

    def _merge_spans(self, spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge overlapping spans. If regex and NER overlap, prefer regex (since it's exact).
        If two of the same type overlap, keep the wider one.
        """
        if not spans:
            return []
            
        # Sort by start index, then by length (longest first)
        sorted_spans = sorted(spans, key=lambda s: (s["start"], -(s["end"] - s["start"])))
        merged = []
        
        for current in sorted_spans:
            if not merged:
                merged.append(current)
                continue
                
            prev = merged[-1]
            # Check for overlap
            if current["start"] < prev["end"]:
                # If they overlap, decide which to keep or how to merge
                if prev["source"] == "regex" and current["source"] == "ner":
                    # Regex trumps NER for the same overlapping region
                    pass 
                elif prev["source"] == "ner" and current["source"] == "regex":
                    # Replace NER with regex if regex is fully contained or overlapping
                    # (For simplicity, if they overlap and current is regex, we'll keep both if they cover different things, 
                    # but if one subsumes the other, keep the regex). Let's just favor regex if they heavily overlap.
                    if current["end"] >= prev["end"] and current["start"] <= prev["start"]:
                        merged[-1] = current
                else:
                    # Same source or we don't care, just extend the span if same pii_type, else keep the highest score
                    if prev["pii_type"] == current["pii_type"]:
                        prev["end"] = max(prev["end"], current["end"])
                    elif current["score"] > prev["score"]:
                        merged[-1] = current
            else:
                merged.append(current)
                
        return merged

    def redact_text(self, text: str, placeholder: str = "[REDACT]") -> str:
        """Redact detected entity spans from text."""
        spans = self.detect_entities(text)
        if not spans:
            return text
            
        # Sort just to be safe before redaction
        spans = sorted(spans, key=lambda s: s["start"])
        redacted = text
        # Apply from right to left to avoid offset shifting
        for s in reversed(spans):
            redacted = redacted[: s["start"]] + placeholder + redacted[s["end"] :]
        return redacted
