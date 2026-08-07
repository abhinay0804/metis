import pytest
from unittest.mock import patch, MagicMock
from server.detectors.ensemble_detector import EnsembleDetector

@pytest.fixture
def mock_ensemble():
    # We mock the initialization so it doesn't try to load the 400MB HuggingFace model
    with patch('detectors.ner_detector.NERDetector.__init__', return_value=None), \
         patch('detectors.ner_detector.NERDetector.detect_entities', return_value=[]):
        detector = EnsembleDetector(use_model_detector=True)
        # Mock the NER detector instance that got created
        detector.ner = MagicMock()
        return detector

def test_ensemble_regex_only(mock_ensemble):
    text = "My email is john.doe@example.com and my phone is (555) 123-4567."
    
    # Simulate NER returning nothing
    mock_ensemble.ner.detect_entities.return_value = []
    
    entities = mock_ensemble.detect_entities(text)
    
    # Should catch email and phone via Regex
    entity_types = [e["pii_type"] for e in entities]
    assert "email" in entity_types
    assert "phone" in entity_types
    
def test_ensemble_ner_integration(mock_ensemble):
    text = "John Smith lives in New York City."
    
    # Simulate NER finding a Person and Location
    mock_ensemble.ner.detect_entities.return_value = [
        {"pii_type": "PERSON", "value": "John Smith", "start": 0, "end": 10, "score": 0.99},
        {"pii_type": "LOCATION", "value": "New York City", "start": 20, "end": 33, "score": 0.98}
    ]
    
    entities = mock_ensemble.detect_entities(text)
    
    entity_types = [e["pii_type"] for e in entities]
    assert "PERSON" in entity_types
    assert "LOCATION" in entity_types
    
    # Validate merging (regex wouldn't find these, so the ensemble should pass them through)
    assert len(entities) == 2
