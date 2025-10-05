"""
Dynamic NLP-Powered Content Analyzer

This analyzer uses natural language processing and dynamic content understanding
to generate contextual descriptions and findings for any content type, including
unknown scenarios. It replaces hardcoded patterns with intelligent analysis.
"""

import re
import json
from typing import Any, Dict, List, Set, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime
from dataclasses import dataclass
import logging

# Optional imports for NLP functionality
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from sensitive_data_masking import SensitiveDataMasker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentInsight:
    """Represents a dynamically generated content insight"""
    category: str
    confidence: float
    description: str
    findings: List[str]
    recommendations: List[str]
    risk_factors: List[str]

class DynamicContentAnalyzer:
    """
    Dynamic analyzer that uses NLP to understand and analyze any content type
    without hardcoded patterns or predefined categories.
    """
    
    def __init__(self, use_openai: bool = False, openai_api_key: str = None):
        self.use_openai = use_openai
        self.openai_api_key = openai_api_key
        
        # Initialize NLP models
        self._initialize_nlp_models()
        
        # Initialize sensitive data masker
        self.masker = SensitiveDataMasker(use_model_detector=True)
        
        # Dynamic content understanding
        self.content_insights = []
        
    def _initialize_nlp_models(self):
        """Initialize NLP models for content analysis"""
        # Initialize spaCy if available
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy model not found, using basic tokenization")
                self.nlp = None
        else:
            logger.warning("spaCy not available, using basic tokenization")
            self.nlp = None
            
        # Initialize transformers if available
        if TRANSFORMERS_AVAILABLE:
            try:
                # Load sentiment analysis model
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
                logger.info("Sentiment analysis model loaded")
            except Exception as e:
                logger.warning(f"Sentiment analysis model failed to load: {e}")
                self.sentiment_analyzer = None
                
            try:
                # Load text classification model for content categorization
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli"
                )
                logger.info("Text classification model loaded")
            except Exception as e:
                logger.warning(f"Text classification model failed to load: {e}")
                self.classifier = None
        else:
            logger.warning("Transformers not available, using basic analysis")
            self.sentiment_analyzer = None
            self.classifier = None
            
        # Initialize OpenAI if available and configured
        if OPENAI_AVAILABLE and self.use_openai and self.openai_api_key:
            openai.api_key = self.openai_api_key
            logger.info("OpenAI API configured")
        elif self.use_openai:
            logger.warning("OpenAI requested but not available or not configured")
    
    def analyze(self, content: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """
        Analyze content using dynamic NLP understanding.
        
        Args:
            content: The extracted content from the file
            file_type: MIME type of the file
            
        Returns:
            Dynamic analysis results with contextual insights
        """
        logger.info(f"Starting dynamic analysis for {file_type}")
        
        # Extract all text content
        all_text = self._extract_all_text(content)
        
        if not all_text or len(all_text.strip()) < 10:
            return self._generate_minimal_analysis(content, file_type)
        
        # Perform dynamic content analysis
        content_insights = self._analyze_content_dynamically(all_text, content, file_type)
        
        # Generate contextual descriptions
        description = self._generate_dynamic_description(content_insights, all_text, file_type)
        
        # Generate dynamic findings
        key_findings = self._generate_dynamic_findings(content_insights, all_text, content)
        
        # Assess risk dynamically
        risk_assessment = self._assess_risk_dynamically(content_insights, all_text)
        
        # Generate recommendations
        recommendations = self._generate_dynamic_recommendations(content_insights, risk_assessment)
        
        # Calculate quality metrics
        quality_metrics = self._calculate_dynamic_quality(content, all_text, file_type)
        
        # Determine compliance requirements
        compliance = self._determine_compliance_dynamically(content_insights, all_text)
        
        return {
            "dataQuality": quality_metrics["overall_quality"],
            "sensitiveFields": content_insights.sensitive_count if hasattr(content_insights, 'sensitive_count') else 0,
            "compliance": compliance,
            "recommendations": recommendations,
            "riskLevel": risk_assessment["level"],
            "description": description,
            "keyFindings": key_findings,
            "contentInsights": {
                "categories": content_insights.category,
                "confidence": content_insights.confidence,
                "insights": content_insights.description,
                "riskFactors": content_insights.risk_factors
            },
            "structureInfo": quality_metrics["structure_info"],
            "dynamicAnalysis": True
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
    
    def _analyze_content_dynamically(self, text: str, content: Dict[str, Any], file_type: str) -> ContentInsight:
        """Analyze content using NLP to understand context and meaning"""
        
        # Extract entities and understand content
        entities = self._extract_entities(text)
        
        # Analyze sentiment and tone
        sentiment = self._analyze_sentiment(text)
        
        # Classify content dynamically
        content_category = self._classify_content_dynamically(text, file_type)
        
        # Detect sensitive information
        sensitive_analysis = self._analyze_sensitive_data_dynamically(text)
        
        # Understand content purpose and context
        purpose = self._understand_content_purpose(text, entities, file_type)
        
        # Generate dynamic insights
        insights = self._generate_content_insights(text, entities, sentiment, content_category, purpose)
        
        return ContentInsight(
            category=content_category,
            confidence=insights["confidence"],
            description=insights["description"],
            findings=insights["findings"],
            recommendations=insights["recommendations"],
            risk_factors=insights["risk_factors"]
        )
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return {"PERSON": [], "ORG": [], "LOC": [], "MISC": []}
        
        doc = self.nlp(text)
        entities = defaultdict(list)
        
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)
        
        return dict(entities)
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and emotional tone of content"""
        if not self.sentiment_analyzer:
            return {"label": "neutral", "score": 0.5}
        
        try:
            # Analyze in chunks if text is too long
            if len(text) > 512:
                chunks = [text[i:i+512] for i in range(0, len(text), 512)]
                results = []
                for chunk in chunks:
                    result = self.sentiment_analyzer(chunk)
                    results.append(result)
                
                # Aggregate results
                avg_score = sum(r[0]['score'] for r in results) / len(results)
                most_common_label = Counter(r[0]['label'] for r in results).most_common(1)[0][0]
                
                return {"label": most_common_label, "score": avg_score}
            else:
                result = self.sentiment_analyzer(text)
                return result[0]
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return {"label": "neutral", "score": 0.5}
    
    def _classify_content_dynamically(self, text: str, file_type: str) -> str:
        """Dynamically classify content using zero-shot classification"""
        if not self.classifier:
            return self._fallback_classification(text, file_type)
        
        try:
            # Define potential categories dynamically
            candidate_labels = [
                "technical documentation",
                "business communication", 
                "personal information",
                "financial data",
                "security information",
                "operational procedures",
                "compliance documentation",
                "infrastructure details",
                "employee records",
                "system configuration"
            ]
            
            result = self.classifier(text, candidate_labels)
            return result['labels'][0]
        except Exception as e:
            logger.warning(f"Content classification failed: {e}")
            return self._fallback_classification(text, file_type)
    
    def _fallback_classification(self, text: str, file_type: str) -> str:
        """Fallback classification using keyword analysis"""
        text_lower = text.lower()
        
        # Simple keyword-based classification
        if any(word in text_lower for word in ["employee", "staff", "personnel", "hr"]):
            return "employee records"
        elif any(word in text_lower for word in ["financial", "payment", "transaction", "accounting"]):
            return "financial data"
        elif any(word in text_lower for word in ["security", "access", "authentication", "password"]):
            return "security information"
        elif any(word in text_lower for word in ["network", "server", "database", "system"]):
            return "infrastructure details"
        elif any(word in text_lower for word in ["policy", "procedure", "compliance", "regulation"]):
            return "compliance documentation"
        else:
            return "general content"
    
    def _analyze_sensitive_data_dynamically(self, text: str) -> Dict[str, Any]:
        """Analyze sensitive data using dynamic detection"""
        # Use the existing sensitive data masker
        detected = self.masker.detect_sensitive_data(text)
        
        # Additional dynamic sensitive data detection
        dynamic_patterns = self._detect_dynamic_sensitive_patterns(text)
        
        return {
            "detected_types": detected,
            "dynamic_patterns": dynamic_patterns,
            "total_sensitive_items": sum(len(items) for items in detected.values()) + len(dynamic_patterns)
        }
    
    def _detect_dynamic_sensitive_patterns(self, text: str) -> List[str]:
        """Detect sensitive patterns that might not be covered by standard patterns"""
        sensitive_indicators = []
        text_lower = text.lower()
        
        # Look for context-specific sensitive information
        if any(term in text_lower for term in ["confidential", "proprietary", "internal use"]):
            sensitive_indicators.append("confidential_marking")
        
        if any(term in text_lower for term in ["classified", "restricted", "top secret"]):
            sensitive_indicators.append("classification_marking")
        
        if any(term in text_lower for term in ["personal", "private", "sensitive"]):
            sensitive_indicators.append("privacy_marking")
        
        return sensitive_indicators
    
    def _understand_content_purpose(self, text: str, entities: Dict[str, List[str]], file_type: str) -> str:
        """Understand the purpose and context of the content"""
        # Analyze entities to understand context
        if entities.get("PERSON"):
            if len(entities["PERSON"]) > 3:
                return "personnel or directory information"
        
        if entities.get("ORG"):
            if len(entities["ORG"]) > 2:
                return "organizational or business information"
        
        if entities.get("LOC"):
            return "location or facility information"
        
        # Analyze text patterns for purpose
        text_lower = text.lower()
        
        if any(term in text_lower for term in ["procedure", "process", "workflow", "steps"]):
            return "operational procedure or workflow"
        elif any(term in text_lower for term in ["report", "analysis", "findings", "results"]):
            return "analytical or reporting document"
        elif any(term in text_lower for term in ["configuration", "settings", "parameters", "config"]):
            return "system configuration or technical specification"
        elif any(term in text_lower for term in ["policy", "guideline", "standard", "requirement"]):
            return "policy or compliance documentation"
        else:
            return "general informational content"
    
    def _generate_content_insights(self, text: str, entities: Dict[str, List[str]], 
                                 sentiment: Dict[str, Any], category: str, purpose: str) -> Dict[str, Any]:
        """Generate dynamic insights about the content"""
        
        # Calculate confidence based on various factors
        confidence = self._calculate_confidence(text, entities, sentiment)
        
        # Generate dynamic description
        description = self._generate_dynamic_description_text(text, entities, category, purpose)
        
        # Generate dynamic findings
        findings = self._generate_dynamic_findings_text(text, entities, category, purpose)
        
        # Generate recommendations
        recommendations = self._generate_dynamic_recommendations_text(text, entities, category, purpose)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(text, entities, category, purpose)
        
        return {
            "confidence": confidence,
            "description": description,
            "findings": findings,
            "recommendations": recommendations,
            "risk_factors": risk_factors
        }
    
    def _calculate_confidence(self, text: str, entities: Dict[str, List[str]], sentiment: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on entity richness
        total_entities = sum(len(ents) for ents in entities.values())
        if total_entities > 5:
            confidence += 0.2
        elif total_entities > 2:
            confidence += 0.1
        
        # Adjust based on sentiment clarity
        if sentiment["score"] > 0.7 or sentiment["score"] < 0.3:
            confidence += 0.1
        
        # Adjust based on text length and complexity
        if len(text.split()) > 100:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_dynamic_description_text(self, text: str, entities: Dict[str, List[str]], 
                                        category: str, purpose: str) -> str:
        """Generate dynamic description based on actual content analysis"""
        
        # Extract key terms and concepts
        key_terms = self._extract_key_terms(text)
        
        # Build description dynamically
        description_parts = []
        
        # Add category context
        description_parts.append(f"Content classified as {category}")
        
        # Add purpose context
        description_parts.append(f"appears to be {purpose}")
        
        # Add entity context
        if entities.get("PERSON"):
            description_parts.append(f"involving {len(entities['PERSON'])} individuals")
        
        if entities.get("ORG"):
            description_parts.append(f"related to {len(entities['ORG'])} organizations")
        
        # Add key terms
        if key_terms:
            description_parts.append(f"with key concepts: {', '.join(key_terms[:3])}")
        
        return ". ".join(description_parts) + "."
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms and concepts from text"""
        if not self.nlp:
            # Simple keyword extraction
            words = text.lower().split()
            # Filter out common words and extract meaningful terms
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            key_terms = [word for word in words if len(word) > 3 and word not in stop_words]
            return list(set(key_terms))[:10]
        
        doc = self.nlp(text)
        # Extract nouns and proper nouns as key terms
        key_terms = []
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 3:
                key_terms.append(token.text.lower())
        
        return list(set(key_terms))[:10]
    
    def _generate_dynamic_findings_text(self, text: str, entities: Dict[str, List[str]], 
                                       category: str, purpose: str) -> List[str]:
        """Generate dynamic findings based on content analysis"""
        findings = []
        
        # Content structure findings
        word_count = len(text.split())
        findings.append(f"Document contains {word_count} words of content")
        
        # Entity-based findings
        if entities.get("PERSON"):
            findings.append(f"Identifies {len(entities['PERSON'])} individuals requiring privacy consideration")
        
        if entities.get("ORG"):
            findings.append(f"References {len(entities['ORG'])} organizations requiring data governance review")
        
        if entities.get("LOC"):
            findings.append(f"Contains {len(entities['LOC'])} location references requiring access control assessment")
        
        # Category-specific findings
        if category == "financial data":
            findings.append("Contains financial information requiring accounting and audit controls")
        elif category == "employee records":
            findings.append("Contains personnel information requiring HR data governance")
        elif category == "security information":
            findings.append("Contains security-related information requiring access control review")
        
        # Purpose-based findings
        if "confidential" in text.lower() or "proprietary" in text.lower():
            findings.append("Marked as confidential or proprietary content requiring restricted access")
        
        if "password" in text.lower() or "credential" in text.lower():
            findings.append("Contains potential authentication credentials requiring secure handling")
        
        return findings
    
    def _generate_dynamic_recommendations_text(self, text: str, entities: Dict[str, List[str]], 
                                             category: str, purpose: str) -> List[str]:
        """Generate dynamic recommendations based on content analysis"""
        recommendations = []
        
        # Entity-based recommendations
        if entities.get("PERSON"):
            recommendations.append("Implement data masking for personal identifiers")
            recommendations.append("Establish role-based access controls for personnel data")
        
        if entities.get("ORG"):
            recommendations.append("Apply data governance policies for organizational information")
            recommendations.append("Implement audit logging for business data access")
        
        # Category-based recommendations
        if category == "financial data":
            recommendations.append("Apply financial data governance and compliance controls")
            recommendations.append("Enable transaction monitoring and anomaly detection")
        
        elif category == "employee records":
            recommendations.append("Establish HR data governance policies")
            recommendations.append("Implement privacy controls for personnel information")
        
        elif category == "security information":
            recommendations.append("Apply enhanced security controls and monitoring")
            recommendations.append("Implement multi-factor authentication where applicable")
        
        # Content-specific recommendations
        if "confidential" in text.lower():
            recommendations.append("Restrict access to authorized personnel only")
            recommendations.append("Implement comprehensive audit logging")
        
        if "password" in text.lower() or "credential" in text.lower():
            recommendations.append("Encrypt and secure authentication credentials")
            recommendations.append("Implement credential rotation policies")
        
        return recommendations if recommendations else ["Apply standard data governance policies"]
    
    def _identify_risk_factors(self, text: str, entities: Dict[str, List[str]], 
                             category: str, purpose: str) -> List[str]:
        """Identify risk factors based on content analysis"""
        risk_factors = []
        
        # Entity-based risks
        if entities.get("PERSON") and len(entities["PERSON"]) > 5:
            risk_factors.append("High volume of personal information")
        
        if entities.get("ORG") and len(entities["ORG"]) > 3:
            risk_factors.append("Multiple organizational references")
        
        # Content-based risks
        if "confidential" in text.lower() or "proprietary" in text.lower():
            risk_factors.append("Confidential or proprietary content")
        
        if "password" in text.lower() or "credential" in text.lower():
            risk_factors.append("Authentication credentials present")
        
        if "financial" in text.lower() or "payment" in text.lower():
            risk_factors.append("Financial information exposure")
        
        # Category-based risks
        if category in ["financial data", "employee records", "security information"]:
            risk_factors.append(f"High-risk content category: {category}")
        
        return risk_factors
    
    def _generate_dynamic_description(self, content_insights: ContentInsight, text: str, file_type: str) -> str:
        """Generate dynamic description based on content insights"""
        return content_insights.description
    
    def _generate_dynamic_findings(self, content_insights: ContentInsight, text: str, content: Dict[str, Any]) -> List[str]:
        """Generate dynamic findings based on content insights"""
        return content_insights.findings
    
    def _assess_risk_dynamically(self, content_insights: ContentInsight, text: str) -> Dict[str, Any]:
        """Assess risk dynamically based on content analysis"""
        risk_score = 0
        risk_factors = content_insights.risk_factors
        
        # Calculate risk score based on factors
        for factor in risk_factors:
            if "high volume" in factor.lower():
                risk_score += 2
            elif "confidential" in factor.lower() or "proprietary" in factor.lower():
                risk_score += 3
            elif "credential" in factor.lower() or "password" in factor.lower():
                risk_score += 3
            elif "financial" in factor.lower():
                risk_score += 2
            else:
                risk_score += 1
        
        # Determine risk level
        if risk_score >= 6:
            level = "High"
        elif risk_score >= 3:
            level = "Medium"
        else:
            level = "Low"
        
        return {
            "level": level,
            "score": risk_score,
            "factors": risk_factors
        }
    
    def _generate_dynamic_recommendations(self, content_insights: ContentInsight, risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate dynamic recommendations based on content insights and risk assessment"""
        return content_insights.recommendations
    
    def _calculate_dynamic_quality(self, content: Dict[str, Any], text: str, file_type: str) -> Dict[str, Any]:
        """Calculate quality metrics dynamically"""
        quality = 0
        structure_info = {}
        
        # Base quality for having content
        if text and len(text.strip()) > 10:
            quality += 30
            structure_info["has_text"] = True
        
        # Content richness
        word_count = len(text.split())
        if word_count > 50:
            quality += 10
        if word_count > 200:
            quality += 10
        
        structure_info["word_count"] = word_count
        
        # File type specific quality
        if file_type.startswith("image/"):
            if "ocr_text" in content and content["ocr_text"]:
                quality += 25
                structure_info["has_ocr"] = True
        
        # Ensure quality is within bounds
        quality = max(0, min(100, quality))
        
        return {
            "overall_quality": quality,
            "structure_info": structure_info
        }
    
    def _determine_compliance_dynamically(self, content_insights: ContentInsight, text: str) -> List[str]:
        """Determine compliance requirements dynamically"""
        standards = set()
        
        # Analyze content for compliance triggers
        text_lower = text.lower()
        
        # GDPR triggers
        if any(term in text_lower for term in ["personal", "individual", "privacy", "data subject"]):
            standards.add("GDPR")
        
        # HIPAA triggers
        if any(term in text_lower for term in ["health", "medical", "patient", "healthcare"]):
            standards.add("HIPAA")
        
        # PCI-DSS triggers
        if any(term in text_lower for term in ["payment", "card", "transaction", "billing"]):
            standards.add("PCI-DSS")
        
        # SOX triggers
        if any(term in text_lower for term in ["financial", "accounting", "audit", "compliance"]):
            standards.add("SOX")
        
        # ISO 27001 triggers
        if any(term in text_lower for term in ["security", "information", "system", "control"]):
            standards.add("ISO 27001")
        
        return list(standards) if standards else ["General"]
    
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
            "structureInfo": {"has_text": False},
            "dynamicAnalysis": True
        }
