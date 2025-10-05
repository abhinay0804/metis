"""
Fallback Analyzer for Basic Content Analysis

This analyzer provides basic content analysis without requiring external NLP libraries.
It serves as a fallback when advanced NLP models are not available.
"""

import re
import json
from typing import Any, Dict, List, Set, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import logging

from sensitive_data_masking import SensitiveDataMasker

logger = logging.getLogger(__name__)

class FallbackAnalyzer:
    """
    Basic analyzer that provides content analysis without external dependencies.
    Uses simple text processing and pattern matching.
    """
    
    def __init__(self):
        # Initialize sensitive data masker
        self.masker = SensitiveDataMasker(use_model_detector=False)
        
        # Basic content patterns
        self.content_patterns = {
            'security': [
                r'\b(?:access|entry|door|card|badge|swipe|tap|reader|biometric|fingerprint)\b',
                r'\b(?:authentication|authorization|login|credential|token)\b',
                r'\b(?:security|permission|privilege|role|admin)\b'
            ],
            'network': [
                r'\b(?:ip|network|subnet|vlan|router|switch|firewall|gateway)\b',
                r'\b(?:port|protocol|tcp|udp|http|https|ssh|ftp)\b',
                r'\b(?:dns|dhcp|nat|vpn|wan|lan|wifi)\b'
            ],
            'employee': [
                r'\b(?:employee|staff|personnel|worker|team|member)\b',
                r'\b(?:name|id|email|phone|department|position|title)\b',
                r'\b(?:salary|wage|payroll|benefits|hr|human resources)\b'
            ],
            'financial': [
                r'\b(?:payment|transaction|invoice|billing|account|balance)\b',
                r'\b(?:credit|debit|bank|financial|money|cost|price)\b',
                r'\b(?:budget|expense|revenue|profit|loss)\b'
            ],
            'compliance': [
                r'\b(?:audit|compliance|regulation|policy|procedure|standard)\b',
                r'\b(?:gdpr|hipaa|pci|sox|iso|nist|cis)\b',
                r'\b(?:review|approval|certification|validation)\b'
            ],
            'infrastructure': [
                r'\b(?:server|database|application|system|platform|service)\b',
                r'\b(?:backup|recovery|maintenance|monitoring|logging)\b',
                r'\b(?:cloud|aws|azure|gcp|datacenter|hosting)\b'
            ]
        }
    
    def analyze(self, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """
        Analyze content using basic text processing.
        
        Args:
            content: The extracted content from the file
            file_type: MIME type of the file
            
        Returns:
            Basic analysis results
        """
        logger.info(f"Starting fallback analysis for {file_type}")
        
        # Extract all text content
        all_text = self._extract_all_text(content)
        
        if not all_text or len(all_text.strip()) < 10:
            return self._generate_minimal_analysis(content, file_type)
        
        # Analyze content using basic patterns
        content_analysis = self._analyze_content_patterns(all_text)
        
        # Analyze sensitive data
        sensitive_analysis = self._analyze_sensitive_data(all_text)
        
        # Generate quality metrics
        quality_metrics = self._calculate_quality_metrics(content, all_text, file_type)
        
        # Assess risk level
        risk_level = self._assess_risk_level(sensitive_analysis, content_analysis)
        
        # Generate compliance requirements
        compliance = self._determine_compliance_standards(sensitive_analysis, content_analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(sensitive_analysis, content_analysis, risk_level, file_type)
        
        # Generate description
        description = self._generate_description(content, content_analysis, file_type, all_text)
        
        # Generate key findings
        key_findings = self._generate_key_findings(content, content_analysis, sensitive_analysis, file_type)
        
        return {
            "dataQuality": quality_metrics["overall_quality"],
            "sensitiveFields": sensitive_analysis["total_sensitive_items"],
            "compliance": compliance,
            "recommendations": recommendations,
            "riskLevel": risk_level,
            "description": description,
            "keyFindings": key_findings,
            "contentCategories": content_analysis["categories"],
            "structureInfo": quality_metrics["structure_info"],
            "fallbackAnalysis": True
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
    
    def _analyze_content_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze content using basic pattern matching"""
        if not text:
            return {"categories": [], "primary_category": "general", "confidence": 0}
        
        text_lower = text.lower()
        category_scores = {}
        
        # Score each category based on pattern matches
        for category, patterns in self.content_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                # Normalize score by text length
                category_scores[category] = score / max(1, len(text_lower) / 1000)
        
        # Determine primary category
        primary_category = "general"
        confidence = 0
        if category_scores:
            primary_category = max(category_scores.keys(), key=lambda k: category_scores[k])
            confidence = min(100, int(category_scores[primary_category] * 20))
        
        # Get top categories
        top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        categories = [cat for cat, score in top_categories if score > 0.1]
        
        return {
            "categories": categories,
            "primary_category": primary_category,
            "confidence": confidence,
            "scores": category_scores
        }
    
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
    
    def _calculate_quality_metrics(self, content: Dict[str, Any], text: str, file_type: str) -> Dict[str, Any]:
        """Calculate basic quality metrics"""
        quality = 0
        structure_info = {}
        
        # Base quality for having content
        if text and len(text.strip()) > 10:
            quality += 30
            structure_info["has_text"] = True
        
        # File type specific quality assessment
        if file_type.startswith("image/"):
            if "ocr_text" in content and content["ocr_text"]:
                quality += 25
                structure_info["has_ocr"] = True
        
        # Content richness
        word_count = len(text.split())
        if word_count > 50:
            quality += 10
        if word_count > 200:
            quality += 10
        
        structure_info["word_count"] = word_count
        
        # Ensure quality is within bounds
        quality = max(0, min(100, quality))
        
        return {
            "overall_quality": quality,
            "structure_info": structure_info
        }
    
    def _assess_risk_level(self, sensitive_analysis: Dict[str, Any], content_analysis: Dict[str, Any]) -> str:
        """Assess risk level based on sensitive data and content type"""
        sensitive_count = sensitive_analysis["total_sensitive_items"]
        categories = content_analysis["categories"]
        
        # Base risk from sensitive data count
        if sensitive_count == 0:
            base_risk = 0
        elif sensitive_count < 5:
            base_risk = 1
        elif sensitive_count < 20:
            base_risk = 2
        else:
            base_risk = 3
        
        # Adjust based on content categories
        high_risk_categories = {"employee", "financial", "security"}
        if any(cat in high_risk_categories for cat in categories):
            base_risk = min(3, base_risk + 1)
        
        risk_levels = ["Low", "Low", "Medium", "High"]
        return risk_levels[base_risk]
    
    def _determine_compliance_standards(self, sensitive_analysis: Dict[str, Any], content_analysis: Dict[str, Any]) -> List[str]:
        """Determine applicable compliance standards"""
        standards = set()
        
        sensitive_categories = sensitive_analysis["categories"]
        content_categories = content_analysis["categories"]
        
        # GDPR for personal data
        if any(cat in sensitive_categories for cat in ["email", "phone", "ssn", "date_of_birth"]):
            standards.add("GDPR")
        
        # PCI-DSS for payment data
        if "credit_card" in sensitive_categories:
            standards.add("PCI-DSS")
        
        # HIPAA for health data
        if "employee" in content_categories or "compliance" in content_categories:
            standards.add("HIPAA")
        
        # SOX for financial data
        if "financial" in content_categories:
            standards.add("SOX")
        
        # ISO 27001 for security-related content
        if any(cat in content_categories for cat in ["security", "network", "infrastructure"]):
            standards.add("ISO 27001")
        
        return list(standards) if standards else ["General"]
    
    def _generate_recommendations(self, sensitive_analysis: Dict[str, Any], content_analysis: Dict[str, Any], 
                                risk_level: str, file_type: str) -> List[str]:
        """Generate basic recommendations"""
        recommendations = []
        
        sensitive_categories = sensitive_analysis["categories"]
        content_categories = content_analysis["categories"]
        
        # Sensitive data recommendations
        if "email" in sensitive_categories or "phone" in sensitive_categories:
            recommendations.append("Implement data masking for personal identifiers")
        
        if "credit_card" in sensitive_categories:
            recommendations.append("Apply PCI-DSS compliant tokenization for payment card data")
        
        if "ssn" in sensitive_categories:
            recommendations.append("Encrypt and restrict access to social security numbers")
        
        # Content-specific recommendations
        if "employee" in content_categories:
            recommendations.append("Establish role-based access controls for HR data")
        
        if "financial" in content_categories:
            recommendations.append("Apply financial data governance policies")
        
        if "security" in content_categories:
            recommendations.append("Review and validate access control configurations")
        
        if "network" in content_categories:
            recommendations.append("Conduct network security assessment")
        
        if risk_level in ["Medium", "High"]:
            recommendations.append("Restrict access and enable comprehensive audit logging")
        
        return recommendations if recommendations else ["Apply standard data governance policies"]
    
    def _generate_description(self, content: Dict[str, Any], content_analysis: Dict[str, Any], 
                            file_type: str, text: str) -> str:
        """Generate basic description"""
        primary_category = content_analysis["primary_category"]
        confidence = content_analysis["confidence"]
        
        # Basic description based on content type
        if file_type.startswith("image/"):
            return f"Image file with {len(text.split())} words of extracted content"
        elif "spreadsheet" in file_type:
            return f"Spreadsheet document with structured data"
        elif "presentation" in file_type:
            return f"Presentation document with slide content"
        elif file_type == "application/pdf":
            return f"PDF document with {len(text.split())} words of content"
        else:
            return f"Document with {len(text.split())} words of content"
    
    def _generate_key_findings(self, content: Dict[str, Any], content_analysis: Dict[str, Any], 
                             sensitive_analysis: Dict[str, Any], file_type: str) -> List[str]:
        """Generate basic key findings"""
        findings = []
        
        categories = content_analysis["categories"]
        primary_category = content_analysis["primary_category"]
        sensitive_categories = sensitive_analysis["categories"]
        sensitive_count = sensitive_analysis["total_sensitive_items"]
        
        # Sensitive data findings
        if sensitive_count > 0:
            findings.append(f"Contains {sensitive_count} sensitive data elements")
            
            if "email" in sensitive_categories:
                findings.append(f"Identified {sensitive_categories['email']} email addresses")
            if "phone" in sensitive_categories:
                findings.append(f"Found {sensitive_categories['phone']} phone numbers")
            if "credit_card" in sensitive_categories:
                findings.append(f"Contains {sensitive_categories['credit_card']} payment card numbers")
        
        # Content structure findings
        if file_type.startswith("image/"):
            findings.append("Image file processed for content analysis")
        elif "spreadsheet" in file_type:
            findings.append("Spreadsheet data structure analyzed")
        elif "presentation" in file_type:
            findings.append("Presentation content structure reviewed")
        else:
            findings.append("Document content analyzed for data governance requirements")
        
        # Category-based findings
        if primary_category != "general" and content_analysis["confidence"] > 30:
            category_findings = {
                "security": "Security system documentation identified",
                "employee": "Employee or personnel information requiring HR data governance",
                "financial": "Financial data subject to accounting and audit requirements",
                "network": "Network infrastructure documentation requiring IT security review",
                "compliance": "Compliance or regulatory documentation requiring controlled access",
                "infrastructure": "System infrastructure details requiring security classification"
            }
            
            if primary_category in category_findings:
                findings.append(category_findings[primary_category])
        
        return findings if findings else ["Content requires standard data governance policies"]
    
    def _generate_minimal_analysis(self, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Generate minimal analysis for content with insufficient text"""
        return {
            "dataQuality": 20,
            "sensitiveFields": 0,
            "compliance": ["General"],
            "recommendations": ["Content requires manual review for analysis"],
            "riskLevel": "Low",
            "description": f"File with minimal extractable content requiring manual review",
            "keyFindings": ["Insufficient text content for automated analysis"],
            "contentCategories": [],
            "structureInfo": {"has_text": False},
            "fallbackAnalysis": True
        }
