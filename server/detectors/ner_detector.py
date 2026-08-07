"""
NER detector using HuggingFace Transformers pipeline.
Loads the fine-tuned RoBERTa model if available, otherwise falls back to BERT base NER.
Identifies PII entities to support redaction.
"""

import os
from typing import List, Dict, Any

from transformers import pipeline

# We look for the fine-tuned model in ml/models/pii-roberta relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINE_TUNED_MODEL_PATH = os.path.join(PROJECT_ROOT, "ml", "models", "pii-roberta")


class NERDetector:
    """Wrapper around a local HF token-classification pipeline for NER."""

    def __init__(self, model: str = None):
        if pipeline is None:
            raise ImportError("transformers is not installed")
            
        # Determine which model to use
        # Use our newly trained local RoBERTa model!
        self.model_path = model or FINE_TUNED_MODEL_PATH
        if not os.path.exists(self.model_path):
            self.model_path = "dslim/bert-base-NER"
            
        self.is_finetuned = ("pii-roberta" in self.model_path)
        print(f"Using NER model: {self.model_path}")

        # grouped_entities provides aggregated spans with start/end offsets
        self.pipe = pipeline(
            task="token-classification",
            model=self.model_path,
            aggregation_strategy="simple",
        )

        # Map model entity groups to PII categories
        if self.is_finetuned:
            # Assuming our fine-tuned RoBERTa emits these tags
            self.entity_to_pii = {
                "NAME": "name",
                "EMAIL": "email",
                "PHONE": "phone",
                "SSN": "ssn",
                "CREDIT_CARD": "credit_card",
                "ADDRESS": "address",
                "ORG": "organization",
                "LOC": "location",
                "DATE": "date_of_birth",
            }
        else:
            # dslim/bert-base-NER emits PER/ORG/LOC/MISC
            self.entity_to_pii = {
                "PER": "name",
                "ORG": "organization",
                "LOC": "location",
                "MISC": "misc",
            }

    def detect_entities(self, text: str) -> List[Dict[str, Any]]:
        """Return list of spans with start, end, label, score for redaction."""
        if not text:
            return []
            
        # Title-case the text to help the NER model recognize ALL-CAPS names
        # The offsets will still map correctly to the original text length
        cased_text = text.title()
        outputs = self.pipe(cased_text)
        spans: List[Dict[str, Any]] = []
        for ent in outputs:
            start = ent.get("start")
            end = ent.get("end")
            label = ent.get("entity_group")
            score = ent.get("score")
            
            if start is None or end is None or label is None:
                continue
                
            pii_type = self.entity_to_pii.get(str(label).upper(), "unknown")
            
            spans.append({
                "start": int(start),
                "end": int(end),
                "label": str(label),
                "pii_type": pii_type,
                "score": float(score) if score is not None else 1.0,
                "value": text[int(start):int(end)]
            })
        return spans

    def redact_text(self, text: str, placeholder: str = "[REDACT]") -> str:
        """Redact detected entity spans from text using placeholder."""
        spans = self.detect_entities(text)
        if not spans:
            return text
        # Merge overlaps and apply from right to left
        spans = sorted(spans, key=lambda s: (s["start"], s["end"]))
        merged: List[Dict[str, int]] = []
        for s in spans:
            if not merged or s["start"] > merged[-1]["end"]:
                merged.append({"start": s["start"], "end": s["end"]})
            else:
                merged[-1]["end"] = max(merged[-1]["end"], s["end"])
        redacted = text
        for s in reversed(merged):
            redacted = redacted[: s["start"]] + placeholder + redacted[s["end"] :]
        return redacted
