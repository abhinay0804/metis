import pytest
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.analysis.fallback_analyzer import FallbackAnalyzer

def test_fallback_analyzer_basic_quality():
    analyzer = FallbackAnalyzer()
    
    # Analyze a mock document
    content = {"text": "This is a basic document that talks about nothing in particular. It just has some text to meet the length requirement for quality assessment."}
    file_type = "text/plain"
    
    result = analyzer.analyze(content, file_type)
    
    # Check that required keys are present
    assert "dataQuality" in result
    assert "riskLevel" in result
    assert "sensitiveFields" in result
    assert "fallbackAnalysis" in result
    
    # Since there are no sensitive fields, risk should be Low
    assert result["sensitiveFields"] == 0
    assert result["riskLevel"] == "Low"

def test_fallback_analyzer_high_risk():
    analyzer = FallbackAnalyzer()
    
    # Analyze a document with fake PII
    content = {"text": "Employee John Doe (john.doe@example.com) with SSN 000-00-0000 has a salary of $100,000."}
    file_type = "text/plain"
    
    result = analyzer.analyze(content, file_type)
    
    # Should detect sensitive fields and assign higher risk
    assert result["sensitiveFields"] > 0
    assert result["riskLevel"] in ["Medium", "High"]
