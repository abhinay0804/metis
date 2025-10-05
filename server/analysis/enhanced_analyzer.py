"""
Enhanced Dynamic Analyzer

This analyzer combines the best of both worlds - the sophisticated analysis
from the original system with dynamic, NLP-powered content understanding.
It can handle any content type, including completely unknown scenarios.
"""

import re
import json
from typing import Any, Dict, List, Set, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
import logging

from sensitive_data_masking import SensitiveDataMasker
from .dynamic_analyzer import DynamicContentAnalyzer
from .fallback_analyzer import FallbackAnalyzer
from .dynamic_templates import template_manager

logger = logging.getLogger(__name__)

class EnhancedDynamicAnalyzer:
    """
    Enhanced analyzer that combines pattern-based analysis with dynamic NLP understanding.
    Can handle any content type, including completely unknown scenarios.
    """
    
    def __init__(self, use_openai: bool = False, openai_api_key: str = None):
        # Try to initialize the dynamic analyzer, fallback to basic analyzer if NLP libraries not available
        try:
            self.dynamic_analyzer = DynamicContentAnalyzer(use_openai, openai_api_key)
            self.use_dynamic = True
            logger.info("Dynamic analyzer initialized successfully")
        except Exception as e:
            logger.warning(f"Dynamic analyzer failed to initialize: {e}")
            logger.info("Falling back to basic analyzer")
            self.dynamic_analyzer = FallbackAnalyzer()
            self.use_dynamic = False
        
        # Initialize sensitive data masker
        self.masker = SensitiveDataMasker(use_model_detector=True)
        
        # Content understanding patterns (configurable, not hardcoded)
        self.content_patterns = self._load_content_patterns()
        
    def _load_content_patterns(self) -> Dict[str, Any]:
        """Load configurable content patterns instead of hardcoded ones"""
        return {
            "security_indicators": [
                r'\b(?:access|entry|door|card|badge|swipe|tap|reader|biometric|fingerprint)\b',
                r'\b(?:authentication|authorization|login|credential|token)\b',
                r'\b(?:security|permission|privilege|role|admin)\b'
            ],
            "network_indicators": [
                r'\b(?:ip|network|subnet|vlan|router|switch|firewall|gateway)\b',
                r'\b(?:port|protocol|tcp|udp|http|https|ssh|ftp)\b',
                r'\b(?:dns|dhcp|nat|vpn|wan|lan|wifi)\b'
            ],
            "employee_indicators": [
                r'\b(?:employee|staff|personnel|worker|team|member)\b',
                r'\b(?:name|id|email|phone|department|position|title)\b',
                r'\b(?:salary|wage|payroll|benefits|hr|human resources)\b'
            ],
            "financial_indicators": [
                r'\b(?:payment|transaction|invoice|billing|account|balance)\b',
                r'\b(?:credit|debit|bank|financial|money|cost|price)\b',
                r'\b(?:budget|expense|revenue|profit|loss)\b'
            ],
            "compliance_indicators": [
                r'\b(?:audit|compliance|regulation|policy|procedure|standard)\b',
                r'\b(?:gdpr|hipaa|pci|sox|iso|nist|cis)\b',
                r'\b(?:review|approval|certification|validation)\b'
            ],
            "infrastructure_indicators": [
                r'\b(?:server|database|application|system|platform|service)\b',
                r'\b(?:backup|recovery|maintenance|monitoring|logging)\b',
                r'\b(?:cloud|aws|azure|gcp|datacenter|hosting)\b'
            ]
        }
    
    def analyze(self, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """
        Enhanced analysis that combines pattern-based and dynamic NLP analysis.
        
        Args:
            content: The extracted content from the file
            file_type: MIME type of the file
            
        Returns:
            Enhanced analysis results with both pattern-based and dynamic insights
        """
        logger.info(f"Starting enhanced analysis for {file_type}")
        
        # Extract all text content
        all_text = self._extract_all_text(content)
        
        if not all_text or len(all_text.strip()) < 10:
            return self._generate_minimal_analysis(content, file_type)
        
        # Perform both pattern-based and dynamic analysis
        pattern_analysis = self._analyze_with_patterns(all_text, content, file_type)
        
        if self.use_dynamic:
            dynamic_analysis = self.dynamic_analyzer.analyze(content, file_type)
            # Combine insights from both approaches
            combined_analysis = self._combine_analyses(pattern_analysis, dynamic_analysis, all_text, file_type)
        else:
            # Use fallback analyzer
            fallback_analysis = self.dynamic_analyzer.analyze(content, file_type)
            # Enhance fallback with pattern analysis
            combined_analysis = self._enhance_fallback_analysis(fallback_analysis, pattern_analysis, all_text, file_type)
        
        return combined_analysis
    
    def _enhance_fallback_analysis(self, fallback_analysis: Dict[str, Any], pattern_analysis: Dict[str, Any], 
                                  text: str, file_type: str) -> Dict[str, Any]:
        """Enhance fallback analysis with pattern insights"""
        enhanced = fallback_analysis.copy()
        
        # Enhance description with pattern insights
        if pattern_analysis["primary_category"] != "general":
            pattern_desc = self._generate_pattern_description(pattern_analysis, text, file_type)
            if pattern_desc:
                enhanced["description"] = f"{fallback_analysis['description']} {pattern_desc}"
        
        # Enhance findings with pattern insights
        pattern_findings = self._generate_pattern_findings(pattern_analysis, text, file_type)
        if pattern_findings:
            enhanced["keyFindings"] = fallback_analysis["keyFindings"] + pattern_findings
        
        # Enhance recommendations with pattern insights
        pattern_recommendations = self._generate_pattern_recommendations(pattern_analysis, text, file_type)
        if pattern_recommendations:
            enhanced["recommendations"] = fallback_analysis["recommendations"] + pattern_recommendations
        
        # Add pattern-based insights
        enhanced["patternInsights"] = {
            "categories": pattern_analysis["categories"],
            "primary_category": pattern_analysis["primary_category"],
            "confidence": pattern_analysis["confidence"]
        }
        
        # Mark as enhanced fallback analysis
        enhanced["enhancedFallbackAnalysis"] = True
        
        return enhanced
    
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
    
    def _analyze_with_patterns(self, text: str, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Analyze content using configurable patterns"""
        text_lower = text.lower()
        pattern_scores = {}
        
        # Score each pattern category
        for category, patterns in self.content_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                # Normalize score by text length
                pattern_scores[category] = score / max(1, len(text_lower) / 1000)
        
        # Determine primary category
        primary_category = "general"
        confidence = 0
        if pattern_scores:
            primary_category = max(pattern_scores.keys(), key=lambda k: pattern_scores[k])
            confidence = min(100, int(pattern_scores[primary_category] * 20))
        
        # Get top categories
        top_categories = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        categories = [cat for cat, score in top_categories if score > 0.1]
        
        return {
            "categories": categories,
            "primary_category": primary_category,
            "confidence": confidence,
            "scores": pattern_scores
        }
    
    def _combine_analyses(self, pattern_analysis: Dict[str, Any], dynamic_analysis: Dict[str, Any], 
                        text: str, file_type: str) -> Dict[str, Any]:
        """Combine pattern-based and dynamic analysis results"""
        
        # Use dynamic analysis as base, enhance with pattern insights
        combined = dynamic_analysis.copy()
        
        # Enhance description with pattern insights
        if pattern_analysis["primary_category"] != "general":
            pattern_desc = self._generate_pattern_description(pattern_analysis, text, file_type)
            if pattern_desc:
                combined["description"] = f"{dynamic_analysis['description']} {pattern_desc}"
        
        # Enhance findings with pattern insights
        pattern_findings = self._generate_pattern_findings(pattern_analysis, text, file_type)
        if pattern_findings:
            combined["keyFindings"] = dynamic_analysis["keyFindings"] + pattern_findings
        
        # Enhance recommendations with pattern insights
        pattern_recommendations = self._generate_pattern_recommendations(pattern_analysis, text, file_type)
        if pattern_recommendations:
            combined["recommendations"] = dynamic_analysis["recommendations"] + pattern_recommendations
        
        # Combine risk assessment
        combined_risk = self._combine_risk_assessment(dynamic_analysis, pattern_analysis)
        combined["riskLevel"] = combined_risk["level"]
        
        # Add pattern-based insights
        combined["patternInsights"] = {
            "categories": pattern_analysis["categories"],
            "primary_category": pattern_analysis["primary_category"],
            "confidence": pattern_analysis["confidence"]
        }
        
        # Mark as enhanced analysis
        combined["enhancedAnalysis"] = True
        
        return combined
    
    def _generate_pattern_description(self, pattern_analysis: Dict[str, Any], text: str, file_type: str) -> str:
        """Generate description based on pattern analysis"""
        primary_category = pattern_analysis["primary_category"]
        confidence = pattern_analysis["confidence"]
        
        if confidence < 30:
            return ""
        
        # Generate contextual description based on patterns
        category_descriptions = {
            "security_indicators": "with security and access control elements",
            "network_indicators": "containing network and infrastructure information",
            "employee_indicators": "with employee and personnel data",
            "financial_indicators": "containing financial and monetary information",
            "compliance_indicators": "with compliance and regulatory content",
            "infrastructure_indicators": "containing system and infrastructure details"
        }
        
        return category_descriptions.get(primary_category, "")
    
    def _generate_pattern_findings(self, pattern_analysis: Dict[str, Any], text: str, file_type: str) -> List[str]:
        """Generate findings based on pattern analysis"""
        findings = []
        primary_category = pattern_analysis["primary_category"]
        confidence = pattern_analysis["confidence"]
        
        if confidence < 30:
            return findings
        
        # Generate findings based on detected patterns
        if primary_category == "security_indicators":
            findings.append("Contains security-related content requiring access control review")
            findings.append("May include authentication mechanisms or security procedures")
        elif primary_category == "network_indicators":
            findings.append("Contains network infrastructure information requiring IT security review")
            findings.append("May include network topology or connectivity details")
        elif primary_category == "employee_indicators":
            findings.append("Contains employee information requiring HR data governance")
            findings.append("May include personnel data requiring privacy protection")
        elif primary_category == "financial_indicators":
            findings.append("Contains financial information requiring accounting controls")
            findings.append("May include monetary data requiring compliance oversight")
        elif primary_category == "compliance_indicators":
            findings.append("Contains compliance documentation requiring regulatory review")
            findings.append("May include policy or procedure information requiring governance")
        elif primary_category == "infrastructure_indicators":
            findings.append("Contains system infrastructure details requiring technical review")
            findings.append("May include configuration or operational information")
        
        return findings
    
    def _generate_pattern_recommendations(self, pattern_analysis: Dict[str, Any], text: str, file_type: str) -> List[str]:
        """Generate recommendations based on pattern analysis"""
        recommendations = []
        primary_category = pattern_analysis["primary_category"]
        confidence = pattern_analysis["confidence"]
        
        if confidence < 30:
            return recommendations
        
        # Generate recommendations based on detected patterns
        if primary_category == "security_indicators":
            recommendations.append("Implement enhanced security controls and monitoring")
            recommendations.append("Apply access control policies and authentication measures")
        elif primary_category == "network_indicators":
            recommendations.append("Implement network security monitoring and controls")
            recommendations.append("Apply network segmentation and access controls")
        elif primary_category == "employee_indicators":
            recommendations.append("Implement HR data governance and privacy controls")
            recommendations.append("Apply employee data protection and access controls")
        elif primary_category == "financial_indicators":
            recommendations.append("Implement financial data governance and compliance controls")
            recommendations.append("Apply accounting oversight and audit controls")
        elif primary_category == "compliance_indicators":
            recommendations.append("Implement compliance monitoring and governance controls")
            recommendations.append("Apply regulatory oversight and policy controls")
        elif primary_category == "infrastructure_indicators":
            recommendations.append("Implement system security and configuration controls")
            recommendations.append("Apply infrastructure monitoring and operational controls")
        
        return recommendations
    
    def _combine_risk_assessment(self, dynamic_analysis: Dict[str, Any], pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine risk assessment from both analyses"""
        dynamic_risk = dynamic_analysis.get("riskLevel", "Low")
        pattern_confidence = pattern_analysis.get("confidence", 0)
        
        # Adjust risk based on pattern confidence
        if pattern_confidence > 70:
            if dynamic_risk == "Low":
                return {"level": "Medium", "factors": ["high_pattern_confidence"]}
            elif dynamic_risk == "Medium":
                return {"level": "High", "factors": ["high_pattern_confidence", "medium_dynamic_risk"]}
        
        return {"level": dynamic_risk, "factors": []}
    
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
            "contentInsights": {
                "categories": "unknown",
                "confidence": 0.1,
                "insights": "Content requires manual analysis",
                "riskFactors": []
            },
            "patternInsights": {
                "categories": [],
                "primary_category": "general",
                "confidence": 0
            },
            "structureInfo": {"has_text": False},
            "enhancedAnalysis": True
        }
    
    def add_custom_pattern(self, category: str, patterns: List[str]):
        """Add custom pattern for content analysis"""
        if category not in self.content_patterns:
            self.content_patterns[category] = []
        
        self.content_patterns[category].extend(patterns)
        logger.info(f"Added custom patterns for category: {category}")
    
    def update_pattern(self, category: str, patterns: List[str]):
        """Update patterns for existing category"""
        self.content_patterns[category] = patterns
        logger.info(f"Updated patterns for category: {category}")
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get current analysis configuration"""
        return {
            "content_patterns": self.content_patterns,
            "template_config": template_manager.templates,
            "pattern_config": template_manager.patterns
        }
    
    def save_analysis_config(self, config_path: str = "analysis_config.json"):
        """Save current analysis configuration"""
        config = self.get_analysis_config()
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Analysis configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Error saving analysis configuration: {e}")
    
    def load_analysis_config(self, config_path: str = "analysis_config.json"):
        """Load analysis configuration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if "content_patterns" in config:
                self.content_patterns.update(config["content_patterns"])
            
            if "template_config" in config:
                template_manager.templates.update(config["template_config"])
            
            if "pattern_config" in config:
                template_manager.patterns.update(config["pattern_config"])
            
            logger.info(f"Analysis configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Error loading analysis configuration: {e}")

# Create enhanced analyzer instance
enhanced_analyzer = EnhancedDynamicAnalyzer()
