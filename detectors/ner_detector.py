"""
Local NER detector using HuggingFace Transformers pipeline.
Identifies entities like PERSON/ORG/LOC to support name/location redaction.
"""

from typing import List, Dict, Any

try:
    from transformers import pipeline
except Exception:  # pragma: no cover
    pipeline = None


class NERDetector:
    """Wrapper around a local HF token-classification pipeline for NER."""

    def __init__(self, model: str = "dslim/bert-base-NER"):
        if pipeline is None:
            raise ImportError("transformers is not installed")
        # grouped_entities provides aggregated spans with start/end offsets
        self.pipe = pipeline(
            task="token-classification",
            model=model,
            aggregation_strategy="simple",
        )

        # Map model entity groups to PII categories
        # dslim/bert-base-NER emits PER/ORG/LOC/MISC
        self.entity_to_pii = {
            "PER": "name",
            "ORG": "organization",
            "LOC": "location",
            "MISC": "misc",
        }

    def detect_entities(self, text: str) -> List[Dict[str, Any]]:
        """Return list of spans with start, end, label for redaction."""
        if not text:
            return []
        outputs = self.pipe(text)
        spans: List[Dict[str, Any]] = []
        for ent in outputs:
            start = ent.get("start")
            end = ent.get("end")
            label = ent.get("entity_group")
            if start is None or end is None or label is None:
                continue
            spans.append({
                "start": int(start),
                "end": int(end),
                "label": str(label),
                "pii_type": self.entity_to_pii.get(str(label), "unknown")
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


