from server.detectors.ner_detector import NERDetector

text = "My name is John Doe, and you can reach me at john.doe@example.com or 555-123-4567. My credit card is 4111-1111-1111-1111. I live in Seattle, WA."

print(f"Testing text: {text}\n")

detector = NERDetector()
entities = detector.detect_entities(text)

print("Detected Entities:")
for ent in entities:
    print(ent)

redacted = detector.redact_text(text)
print("\nRedacted Text:")
print(redacted)
