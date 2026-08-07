"""
Dynamic Template System for Content Analysis

This module provides configurable templates and patterns for generating
dynamic descriptions, findings, and recommendations without hardcoding.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import os

@dataclass
class AnalysisTemplate:
    """Template for generating analysis content"""
    name: str
    description_template: str
    findings_templates: List[str]
    recommendations_templates: List[str]
    risk_factors: List[str]
    confidence_threshold: float = 0.5

class DynamicTemplateManager:
    """
    Manages dynamic templates for content analysis.
    Allows for configuration-driven analysis without hardcoding.
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "analysis_templates.json"
        self.templates = {}
        self.patterns = {}
        self.load_templates()
    
    def load_templates(self):
        """Load templates from configuration file or create defaults"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.templates = config.get('templates', {})
                    self.patterns = config.get('patterns', {})
            except Exception as e:
                print(f"Error loading templates: {e}")
                self._create_default_templates()
        else:
            self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default dynamic templates"""
        self.templates = {
            "content_categories": {
                "technical_documentation": {
                    "description_template": "Technical documentation containing {key_terms} and {entity_count} technical references",
                    "findings_templates": [
                        "Contains technical specifications requiring security review",
                        "May include system configuration details needing protection",
                        "Technical content with {entity_count} system references"
                    ],
                    "recommendations_templates": [
                        "Apply technical data governance policies",
                        "Implement system configuration security controls",
                        "Enable technical content monitoring"
                    ],
                    "risk_factors": ["technical_exposure", "system_configuration"]
                },
                "business_communication": {
                    "description_template": "Business communication document with {key_terms} and organizational context",
                    "findings_templates": [
                        "Contains business information requiring data governance",
                        "Organizational content with {entity_count} business references",
                        "Business communication requiring access controls"
                    ],
                    "recommendations_templates": [
                        "Apply business data governance policies",
                        "Implement organizational access controls",
                        "Enable business content monitoring"
                    ],
                    "risk_factors": ["business_exposure", "organizational_data"]
                },
                "personal_information": {
                    "description_template": "Document containing personal information with {entity_count} individual references",
                    "findings_templates": [
                        "Contains personal information requiring privacy protection",
                        "Individual data with {entity_count} person references",
                        "Personal content requiring data protection controls"
                    ],
                    "recommendations_templates": [
                        "Implement data masking for personal identifiers",
                        "Apply privacy protection controls",
                        "Enable personal data monitoring"
                    ],
                    "risk_factors": ["privacy_exposure", "personal_data"]
                },
                "financial_data": {
                    "description_template": "Financial document with monetary information and {entity_count} financial references",
                    "findings_templates": [
                        "Contains financial information requiring accounting controls",
                        "Monetary data with {entity_count} financial references",
                        "Financial content requiring compliance controls"
                    ],
                    "recommendations_templates": [
                        "Apply financial data governance policies",
                        "Implement accounting compliance controls",
                        "Enable financial monitoring"
                    ],
                    "risk_factors": ["financial_exposure", "monetary_data"]
                },
                "security_information": {
                    "description_template": "Security-related document with {key_terms} and security context",
                    "findings_templates": [
                        "Contains security information requiring access controls",
                        "Security content with {entity_count} security references",
                        "Security information requiring enhanced protection"
                    ],
                    "recommendations_templates": [
                        "Apply enhanced security controls",
                        "Implement security monitoring",
                        "Enable security access controls"
                    ],
                    "risk_factors": ["security_exposure", "access_control"]
                }
            },
            "content_purposes": {
                "operational_procedure": {
                    "description_template": "Operational procedure document outlining {key_terms} processes",
                    "findings_templates": [
                        "Contains operational procedures requiring process controls",
                        "Procedure documentation with {entity_count} operational references",
                        "Operational content requiring workflow controls"
                    ],
                    "recommendations_templates": [
                        "Implement process governance controls",
                        "Apply operational monitoring",
                        "Enable procedure access controls"
                    ],
                    "risk_factors": ["process_exposure", "operational_data"]
                },
                "analytical_report": {
                    "description_template": "Analytical report containing {key_terms} and analytical findings",
                    "findings_templates": [
                        "Contains analytical information requiring data controls",
                        "Report content with {entity_count} analytical references",
                        "Analytical data requiring research controls"
                    ],
                    "recommendations_templates": [
                        "Apply analytical data governance",
                        "Implement research monitoring",
                        "Enable analytical access controls"
                    ],
                    "risk_factors": ["analytical_exposure", "research_data"]
                },
                "system_configuration": {
                    "description_template": "System configuration document with {key_terms} and technical parameters",
                    "findings_templates": [
                        "Contains system configuration requiring technical controls",
                        "Configuration data with {entity_count} system references",
                        "System settings requiring configuration controls"
                    ],
                    "recommendations_templates": [
                        "Apply system configuration security",
                        "Implement technical monitoring",
                        "Enable configuration access controls"
                    ],
                    "risk_factors": ["configuration_exposure", "system_data"]
                },
                "policy_documentation": {
                    "description_template": "Policy document outlining {key_terms} and compliance requirements",
                    "findings_templates": [
                        "Contains policy information requiring compliance controls",
                        "Policy content with {entity_count} compliance references",
                        "Policy documentation requiring governance controls"
                    ],
                    "recommendations_templates": [
                        "Apply policy governance controls",
                        "Implement compliance monitoring",
                        "Enable policy access controls"
                    ],
                    "risk_factors": ["policy_exposure", "compliance_data"]
                }
            },
            "sensitive_patterns": {
                "confidential_marking": {
                    "description_addition": "marked as confidential or proprietary",
                    "findings_addition": "Contains confidential markings requiring restricted access",
                    "recommendations_addition": "Implement confidential data controls and restricted access",
                    "risk_factor": "confidential_content"
                },
                "classification_marking": {
                    "description_addition": "classified or restricted content",
                    "findings_addition": "Contains classification markings requiring security controls",
                    "recommendations_addition": "Apply classification-based access controls",
                    "risk_factor": "classified_content"
                },
                "privacy_marking": {
                    "description_addition": "personal or private information",
                    "findings_addition": "Contains privacy markings requiring data protection",
                    "recommendations_addition": "Implement privacy protection controls",
                    "risk_factor": "privacy_content"
                }
            }
        }
        
        self.patterns = {
            "entity_thresholds": {
                "high_volume_person": 5,
                "high_volume_org": 3,
                "high_volume_location": 2
            },
            "confidence_factors": {
                "entity_richness": 0.2,
                "sentiment_clarity": 0.1,
                "text_complexity": 0.1
            },
            "risk_scoring": {
                "high_volume_personal": 2,
                "confidential_content": 3,
                "credential_content": 3,
                "financial_content": 2,
                "default_risk": 1
            }
        }
    
    def get_template(self, category: str, purpose: str = None) -> Dict[str, Any]:
        """Get template for specific content category and purpose"""
        template = self.templates.get("content_categories", {}).get(category, {})
        
        if purpose:
            purpose_template = self.templates.get("content_purposes", {}).get(purpose, {})
            # Merge purpose-specific overrides
            for key, value in purpose_template.items():
                if key in template:
                    if isinstance(value, list) and isinstance(template[key], list):
                        template[key].extend(value)
                    else:
                        template[key] = value
                else:
                    template[key] = value
        
        return template
    
    def get_sensitive_pattern_template(self, pattern_type: str) -> Dict[str, Any]:
        """Get template for sensitive content patterns"""
        return self.templates.get("sensitive_patterns", {}).get(pattern_type, {})
    
    def generate_description(self, category: str, purpose: str, key_terms: List[str], 
                          entity_count: int, sensitive_patterns: List[str] = None) -> str:
        """Generate dynamic description using templates"""
        template = self.get_template(category, purpose)
        description_template = template.get("description_template", "Content document with {key_terms}")
        
        # Format template with actual values
        description = description_template.format(
            key_terms=", ".join(key_terms[:3]) if key_terms else "various topics",
            entity_count=entity_count
        )
        
        # Add sensitive pattern descriptions
        if sensitive_patterns:
            for pattern in sensitive_patterns:
                pattern_template = self.get_sensitive_pattern_template(pattern)
                if pattern_template.get("description_addition"):
                    description += f" ({pattern_template['description_addition']})"
        
        return description
    
    def generate_findings(self, category: str, purpose: str, entity_count: int, 
                         sensitive_patterns: List[str] = None) -> List[str]:
        """Generate dynamic findings using templates"""
        template = self.get_template(category, purpose)
        findings_templates = template.get("findings_templates", ["Content requires analysis"])
        
        findings = []
        for template_str in findings_templates:
            finding = template_str.format(entity_count=entity_count)
            findings.append(finding)
        
        # Add sensitive pattern findings
        if sensitive_patterns:
            for pattern in sensitive_patterns:
                pattern_template = self.get_sensitive_pattern_template(pattern)
                if pattern_template.get("findings_addition"):
                    findings.append(pattern_template["findings_addition"])
        
        return findings
    
    def generate_recommendations(self, category: str, purpose: str, 
                               sensitive_patterns: List[str] = None) -> List[str]:
        """Generate dynamic recommendations using templates"""
        template = self.get_template(category, purpose)
        recommendations_templates = template.get("recommendations_templates", 
                                               ["Apply standard data governance policies"])
        
        recommendations = list(recommendations_templates)
        
        # Add sensitive pattern recommendations
        if sensitive_patterns:
            for pattern in sensitive_patterns:
                pattern_template = self.get_sensitive_pattern_template(pattern)
                if pattern_template.get("recommendations_addition"):
                    recommendations.append(pattern_template["recommendations_addition"])
        
        return recommendations
    
    def get_risk_factors(self, category: str, purpose: str, sensitive_patterns: List[str] = None) -> List[str]:
        """Get risk factors for content category and purpose"""
        template = self.get_template(category, purpose)
        risk_factors = template.get("risk_factors", [])
        
        # Add sensitive pattern risk factors
        if sensitive_patterns:
            for pattern in sensitive_patterns:
                pattern_template = self.get_sensitive_pattern_template(pattern)
                if pattern_template.get("risk_factor"):
                    risk_factors.append(pattern_template["risk_factor"])
        
        return risk_factors
    
    def save_templates(self):
        """Save current templates to configuration file"""
        config = {
            "templates": self.templates,
            "patterns": self.patterns
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving templates: {e}")
    
    def add_custom_template(self, category: str, template_data: Dict[str, Any]):
        """Add custom template for new content category"""
        if "content_categories" not in self.templates:
            self.templates["content_categories"] = {}
        
        self.templates["content_categories"][category] = template_data
        self.save_templates()
    
    def add_custom_purpose_template(self, purpose: str, template_data: Dict[str, Any]):
        """Add custom template for new content purpose"""
        if "content_purposes" not in self.templates:
            self.templates["content_purposes"] = {}
        
        self.templates["content_purposes"][purpose] = template_data
        self.save_templates()
    
    def add_sensitive_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """Add custom sensitive pattern template"""
        if "sensitive_patterns" not in self.templates:
            self.templates["sensitive_patterns"] = {}
        
        self.templates["sensitive_patterns"][pattern_name] = pattern_data
        self.save_templates()

# Global template manager instance
template_manager = DynamicTemplateManager()

def get_dynamic_description(category: str, purpose: str, key_terms: List[str], 
                          entity_count: int, sensitive_patterns: List[str] = None) -> str:
    """Get dynamic description using template manager"""
    return template_manager.generate_description(category, purpose, key_terms, entity_count, sensitive_patterns)

def get_dynamic_findings(category: str, purpose: str, entity_count: int, 
                        sensitive_patterns: List[str] = None) -> List[str]:
    """Get dynamic findings using template manager"""
    return template_manager.generate_findings(category, purpose, entity_count, sensitive_patterns)

def get_dynamic_recommendations(category: str, purpose: str, 
                               sensitive_patterns: List[str] = None) -> List[str]:
    """Get dynamic recommendations using template manager"""
    return template_manager.generate_recommendations(category, purpose, sensitive_patterns)

def get_risk_factors(category: str, purpose: str, sensitive_patterns: List[str] = None) -> List[str]:
    """Get risk factors using template manager"""
    return template_manager.get_risk_factors(category, purpose, sensitive_patterns)
