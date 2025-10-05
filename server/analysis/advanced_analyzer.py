"""
Advanced Content-Aware Data Analyzer

This analyzer examines the actual extracted content from files and provides
contextual, meaningful analysis based on the real data present in each file.
Works with any file type and content structure.
"""

from typing import Any, Dict, List, Set, Tuple, Optional
from collections import Counter, defaultdict
import re
import json
from datetime import datetime

from sensitive_data_masking import SensitiveDataMasker


class AdvancedDataAnalyzer:
    """
    Content-aware analyzer that examines actual extracted content to provide
    unique, contextual analysis for each file regardless of type or content.
    """

    def __init__(self):
        self.masker = SensitiveDataMasker(use_model_detector=False)
        
        # Content type patterns for better classification
        self.security_patterns = {
            'access_control': [
                r'\b(?:access|entry|door|card|badge|swipe|tap|reader|biometric|fingerprint)\b',
                r'\b(?:authentication|authorization|login|credential|token)\b',
                r'\b(?:security|permission|privilege|role|admin)\b'
            ],
            'network': [
                r'\b(?:ip|network|subnet|vlan|router|switch|firewall|gateway)\b',
                r'\b(?:port|protocol|tcp|udp|http|https|ssh|ftp)\b',
                r'\b(?:dns|dhcp|nat|vpn|wan|lan|wifi)\b'
            ],
            'employee_data': [
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
        Analyze extracted content and provide contextual insights.
        
        Args:
            content: The extracted content from the file
            file_type: MIME type of the file
            
        Returns:
            Analysis results with description, key findings, and metrics
        """
        
        # Extract all text content from the file
        all_text = self._extract_all_text(content)
        
        # Analyze sensitive data
        sensitive_analysis = self._analyze_sensitive_data(all_text)
        
        # Determine content categories and context
        content_analysis = self._analyze_content_categories(all_text, content)
        
        # Generate quality metrics
        quality_metrics = self._calculate_quality_metrics(content, all_text, file_type)
        
        # Determine risk level
        risk_level = self._assess_risk_level(sensitive_analysis, content_analysis)
        
        # Generate compliance recommendations
        compliance = self._determine_compliance_standards(sensitive_analysis, content_analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            sensitive_analysis, content_analysis, risk_level, file_type
        )
        
        # Generate contextual description
        description = self._generate_description(content, content_analysis, file_type, all_text)
        
        # Generate key findings
        key_findings = self._generate_key_findings(
            content, content_analysis, sensitive_analysis, file_type
        )
        
        return {
            "dataQuality": quality_metrics["overall_quality"],
            "sensitiveFields": sensitive_analysis["total_sensitive_items"],
            "compliance": compliance,
            "recommendations": recommendations,
            "riskLevel": risk_level,
            "description": description,
            "keyFindings": key_findings,
            # Additional metadata for debugging/enhancement
            "contentCategories": content_analysis["categories"],
            "structureInfo": quality_metrics["structure_info"]
        }

    def _extract_all_text(self, content: Dict[str, Any]) -> str:
        """Extract all text content from various file structures."""
        texts = []
        
        def extract_recursive(obj):
            if isinstance(obj, str):
                texts.append(obj)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if key not in ['base64_data', 'redacted_image_base64']:  # Skip binary data
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)
        
        extract_recursive(content)
        return ' '.join(texts).strip()

    def _analyze_sensitive_data(self, text: str) -> Dict[str, Any]:
        """Analyze sensitive data patterns in the text."""
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

    def _analyze_content_categories(self, text: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content to determine categories and context."""
        if not text:
            return {"categories": [], "primary_category": "unknown", "confidence": 0}
        
        text_lower = text.lower()
        category_scores = {}
        
        # Score each category based on pattern matches
        for category, patterns in self.security_patterns.items():
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

    def _calculate_quality_metrics(self, content: Dict[str, Any], text: str, file_type: str) -> Dict[str, Any]:
        """Calculate data quality metrics based on content structure and completeness."""
        quality = 0
        structure_info = {}
        
        # Base quality for having content
        if text and len(text.strip()) > 10:
            quality += 30
            structure_info["has_text"] = True
        
        # File type specific quality assessment
        if file_type.startswith("image/"):
            # Image quality factors
            if "ocr_text" in content and content["ocr_text"]:
                quality += 25
                structure_info["has_ocr"] = True
            if "image_info" in content:
                info = content["image_info"]
                if info.get("width", 0) > 500 and info.get("height", 0) > 500:
                    quality += 15
                    structure_info["good_resolution"] = True
        
        elif "application/vnd.openxmlformats" in file_type:
            # Office documents
            if "slides" in content or "worksheets" in content or "paragraphs" in content:
                quality += 20
                structure_info["structured_document"] = True
            
            # Check for tables
            if self._has_tables(content):
                quality += 15
                structure_info["has_tables"] = True
        
        elif file_type == "application/pdf":
            if "text_content" in content and content["text_content"]:
                quality += 25
                structure_info["extractable_text"] = True
            if "tables" in content and content["tables"]:
                quality += 15
                structure_info["has_tables"] = True
        
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

    def _has_tables(self, content: Dict[str, Any]) -> bool:
        """Check if content contains tabular data."""
        def check_recursive(obj):
            if isinstance(obj, dict):
                if "tables" in obj or "data" in obj:
                    return True
                return any(check_recursive(v) for v in obj.values())
            elif isinstance(obj, list):
                return any(check_recursive(item) for item in obj)
            return False
        
        return check_recursive(content)

    def _assess_risk_level(self, sensitive_analysis: Dict[str, Any], content_analysis: Dict[str, Any]) -> str:
        """Assess overall risk level based on sensitive data and content type."""
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
        high_risk_categories = {"employee_data", "financial", "access_control"}
        if any(cat in high_risk_categories for cat in categories):
            base_risk = min(3, base_risk + 1)
        
        risk_levels = ["Low", "Low", "Medium", "High"]
        return risk_levels[base_risk]

    def _determine_compliance_standards(self, sensitive_analysis: Dict[str, Any], content_analysis: Dict[str, Any]) -> List[str]:
        """Determine applicable compliance standards."""
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
        if "employee_data" in content_categories or "compliance" in content_categories:
            standards.add("HIPAA")
        
        # SOX for financial data
        if "financial" in content_categories:
            standards.add("SOX")
        
        # ISO 27001 for security-related content
        if any(cat in content_categories for cat in ["access_control", "network", "infrastructure"]):
            standards.add("ISO 27001")
        
        return list(standards) if standards else ["General"]

    def _generate_recommendations(self, sensitive_analysis: Dict[str, Any], content_analysis: Dict[str, Any], 
                                risk_level: str, file_type: str) -> List[str]:
        """Generate contextual recommendations based on analysis."""
        recommendations = []
        
        sensitive_categories = sensitive_analysis["categories"]
        content_categories = content_analysis["categories"]
        
        # Sensitive data recommendations
        if "email" in sensitive_categories or "phone" in sensitive_categories:
            recommendations.append("Implement data masking for personal identifiers (emails, phone numbers)")
        
        if "credit_card" in sensitive_categories:
            recommendations.append("Apply PCI-DSS compliant tokenization for payment card data")
        
        if "ssn" in sensitive_categories:
            recommendations.append("Encrypt and restrict access to social security numbers")
        
        # Content-specific recommendations
        if "employee_data" in content_categories:
            recommendations.append("Establish role-based access controls for HR data")
            recommendations.append("Implement audit logging for employee data access")
        
        if "financial" in content_categories:
            recommendations.append("Apply financial data governance policies")
            recommendations.append("Enable transaction monitoring and anomaly detection")
        
        if "access_control" in content_categories:
            recommendations.append("Review and validate access control configurations")
            recommendations.append("Implement multi-factor authentication where applicable")
        
        if "network" in content_categories:
            recommendations.append("Conduct network security assessment")
            recommendations.append("Implement network segmentation and monitoring")
        
        # File type specific recommendations
        if file_type.startswith("image/"):
            recommendations.append("Apply OCR-based redaction for text in images")
        
        if risk_level in ["Medium", "High"]:
            recommendations.append("Restrict access and enable comprehensive audit logging")
            recommendations.append("Implement data loss prevention (DLP) controls")
        
        return recommendations if recommendations else ["No specific security concerns identified"]

    def _generate_description(self, content: Dict[str, Any], content_analysis: Dict[str, Any], 
                            file_type: str, text: str) -> str:
        """Generate contextual description based on actual content."""
        
        primary_category = content_analysis["primary_category"]
        confidence = content_analysis["confidence"]
        
        # Try to generate specific description based on content
        if file_type.startswith("image/"):
            return self._describe_image_content(content, primary_category, text)
        
        elif "application/vnd.openxmlformats-officedocument.spreadsheetml" in file_type:
            return self._describe_spreadsheet_content(content, primary_category)
        
        elif "application/vnd.openxmlformats-officedocument.presentationml" in file_type:
            return self._describe_presentation_content(content, primary_category)
        
        elif file_type == "application/pdf":
            return self._describe_pdf_content(content, primary_category, text)
        
        elif "application/vnd.openxmlformats-officedocument.wordprocessingml" in file_type:
            return self._describe_document_content(content, primary_category, text)
        
        else:
            return self._describe_generic_content(content, primary_category, file_type, text)

    def _describe_image_content(self, content: Dict[str, Any], category: str, text: str) -> str:
        """Generate description for image content based on actual extracted data."""
        ocr_text = content.get("ocr_text", "").strip()
        image_info = content.get("image_info", {})
        
        # Get image dimensions and format
        width = image_info.get("width", "unknown")
        height = image_info.get("height", "unknown")
        format_type = image_info.get("format", "image").upper()
        file_size = content.get("file_size", 0)
        
        base_desc = f"{format_type} image ({width}x{height})"
        
        # If no OCR text, analyze based on image characteristics and filename patterns
        if not ocr_text or len(ocr_text.strip()) == 0:
            # Analyze filename for content hints
            filename = content.get("filename", "").lower()
            
            # Check for logo detections
            logo_detections = content.get("logo_detections", [])
            if logo_detections:
                return "Corporate Branding/Logo Display"
            
            # Check for text redactions (indicates text was found but redacted)
            text_redactions = content.get("text_redactions", [])
            if text_redactions:
                return "Document with Redacted Information"
            
            # Analyze image characteristics for content type
            if width and height:
                aspect_ratio = width / height if height > 0 else 1
                
                # Screen capture patterns (16:9, 4:3, etc.)
                if 1.7 <= aspect_ratio <= 1.8:  # ~16:9
                    return "System Interface Screenshot"
                elif 1.3 <= aspect_ratio <= 1.6:  # ~4:3 to wider
                    return "Security Monitor Display"
                elif aspect_ratio > 2:  # Wide format
                    return "Network Infrastructure Layout"
                elif 0.7 <= aspect_ratio <= 1.3:  # Square-ish
                    return "Access Control Panel"
                else:
                    return "Security System Interface"
            
            return "Security Infrastructure Component"
        
        # If we have OCR text, analyze it for content-specific descriptions
        ocr_lower = ocr_text.lower()
        word_count = len(ocr_text.split())
        
        # Remove hardcoded categories - use pure content analysis
        
        # Dynamic content analysis based on actual OCR text
        if ocr_text and len(ocr_text.strip()) > 0:
            return self._generate_intelligent_description(ocr_text, image_info)
        
        # Generic description with actual OCR content sample
        words = ocr_text.split() if ocr_text else []
        if len(words) > 3:
            # Take first few meaningful words (skip very short words)
            meaningful_words = [w for w in words[:10] if len(w) > 2][:5]
            if meaningful_words:
                snippet = " ".join(meaningful_words)
                return f"Document containing: \"{snippet}...\" ({len(words)} total words)"
        
        return f"Document with {len(words)} words of extracted text content."

    def _generate_intelligent_description(self, ocr_text: str, image_info: Dict[str, Any]) -> str:
        """Generate intelligent description based on actual content analysis."""
        text_lower = ocr_text.lower()
        words = ocr_text.split()
        
        # Extract key terms and concepts
        significant_words = [w for w in words if len(w) > 3 and w.isalpha()]
        
        # Analyze content patterns dynamically
        content_themes = self._identify_content_themes(text_lower, significant_words)
        
        # Generate natural description based on themes
        if content_themes:
            primary_theme = max(content_themes.items(), key=lambda x: x[1])
            theme_name, confidence = primary_theme
            
            if confidence >= 2:  # Strong theme detected
                return self._describe_theme(theme_name, ocr_text, significant_words)
        
        # Fallback to content-based description
        if len(significant_words) >= 3:
            # Create a natural description from the most meaningful words
            key_terms = significant_words[:3]
            return f"Document containing {', '.join(key_terms)} and related information"
        
        return f"Document with {len(words)} words of content"

    def _identify_content_themes(self, text_lower: str, significant_words: List[str]) -> Dict[str, int]:
        """Identify themes in content dynamically."""
        themes = {}
        
        # Infrastructure/Facility theme (room signs, facility labels)
        infrastructure_indicators = ["idf", "electrical", "mechanical", "server", "room", "floor", "building", "facility", "equipment", "utility"]
        infrastructure_score = sum(1 for word in infrastructure_indicators if word in text_lower)
        if infrastructure_score > 0:
            themes["infrastructure_facility"] = infrastructure_score
        
        # Network/IT theme
        network_indicators = ["network", "internet", "dmz", "trusted", "privileged", "vpn", "gateway", "firewall", "router", "switch", "services", "mainframe"]
        network_score = sum(1 for word in network_indicators if word in text_lower)
        if network_score > 0:
            themes["network_infrastructure"] = network_score
        
        # Access/Security theme  
        access_indicators = ["access", "card", "reader", "badge", "door", "entry", "security", "authentication", "login", "password", "key"]
        access_score = sum(1 for word in access_indicators if word in text_lower)
        if access_score > 0:
            themes["access_security"] = access_score
        
        # Document/Form theme
        document_indicators = ["form", "application", "request", "report", "document", "policy", "procedure", "manual", "guide", "instructions"]
        document_score = sum(1 for word in document_indicators if word in text_lower)
        if document_score > 0:
            themes["documentation"] = document_score
        
        # Employee/HR theme
        employee_indicators = ["employee", "staff", "personnel", "name", "department", "position", "title", "phone", "email", "address"]
        employee_score = sum(1 for word in employee_indicators if word in text_lower)
        if employee_score > 0:
            themes["employee_data"] = employee_score
        
        # Financial theme
        financial_indicators = ["payment", "invoice", "billing", "account", "balance", "transaction", "amount", "cost", "price", "budget", "expense"]
        financial_score = sum(1 for word in financial_indicators if word in text_lower)
        if financial_score > 0:
            themes["financial"] = financial_score
        
        # System/Technical theme
        technical_indicators = ["system", "application", "software", "database", "config", "configuration", "settings", "parameters", "version", "update"]
        technical_score = sum(1 for word in technical_indicators if word in text_lower)
        if technical_score > 0:
            themes["technical_system"] = technical_score
        
        return themes

    def _describe_theme(self, theme_name: str, ocr_text: str, significant_words: List[str]) -> str:
        """Generate description based on identified theme."""
        key_terms = significant_words[:4]  # Top 4 significant words
        
        theme_descriptions = {
            "infrastructure_facility": f"Infrastructure facility signage showing {', '.join(key_terms)}",
            "network_infrastructure": f"Network infrastructure documentation containing {', '.join(key_terms)}",
            "access_security": f"Access control system documentation with {', '.join(key_terms)}",
            "documentation": f"Organizational documentation regarding {', '.join(key_terms)}",
            "employee_data": f"Employee information document containing {', '.join(key_terms)}",
            "financial": f"Financial document with {', '.join(key_terms)}",
            "technical_system": f"Technical system documentation covering {', '.join(key_terms)}"
        }
        
        return theme_descriptions.get(theme_name, f"Document containing {', '.join(key_terms)}")

    def _generate_dynamic_findings(self, ocr_text: str, content: Dict[str, Any]) -> List[str]:
        """Generate dynamic findings based on actual content analysis."""
        findings = []
        text_lower = ocr_text.lower()
        words = ocr_text.split()
        significant_words = [w for w in words if len(w) > 3 and w.isalpha()]
        
        # Identify content themes
        content_themes = self._identify_content_themes(text_lower, significant_words)
        
        if content_themes:
            # Generate findings based on the strongest theme
            primary_theme = max(content_themes.items(), key=lambda x: x[1])
            theme_name, confidence = primary_theme
            
            findings.extend(self._generate_theme_findings(theme_name, ocr_text, significant_words, confidence))
        
        # Add general content analysis
        if len(significant_words) > 0:
            findings.append(f"Contains {len(words)} words with key terms: {', '.join(significant_words[:5])}")
        
        # Check for potential sensitive information patterns
        sensitive_patterns = self._detect_content_patterns(text_lower)
        if sensitive_patterns:
            findings.extend(sensitive_patterns)
        
        return findings if findings else [f"Document contains {len(words)} words of content requiring analysis"]

    def _generate_theme_findings(self, theme_name: str, ocr_text: str, significant_words: List[str], confidence: int) -> List[str]:
        """Generate findings based on identified theme."""
        findings = []
        
        if theme_name == "infrastructure_facility":
            findings.extend([
                "Infrastructure facility identification signage or room labeling.",
                "Contains facility location information and infrastructure designations.",
                "May indicate electrical, mechanical, or IT infrastructure areas requiring access control."
            ])
        elif theme_name == "network_infrastructure":
            findings.extend([
                "Network infrastructure documentation with system architecture details.",
                "Contains network topology and security zone information.",
                "May include IP addresses, server names, and connectivity details requiring protection."
            ])
        elif theme_name == "access_security":
            findings.extend([
                "Access control system documentation with security mechanisms.",
                "Contains authentication and authorization details.",
                "May include credentials, access codes, or security procedures requiring protection."
            ])
        elif theme_name == "employee_data":
            findings.extend([
                "Employee information document with personnel details.",
                "Contains personal and organizational data.",
                "May include contact information, roles, or HR data requiring privacy protection."
            ])
        elif theme_name == "financial":
            findings.extend([
                "Financial document with monetary or transaction information.",
                "Contains accounting, billing, or payment details.",
                "May include sensitive financial data requiring compliance controls."
            ])
        elif theme_name == "technical_system":
            findings.extend([
                "Technical system documentation with configuration details.",
                "Contains system settings, parameters, or operational information.",
                "May include technical specifications requiring security review."
            ])
        elif theme_name == "documentation":
            findings.extend([
                "Organizational documentation with procedural or policy information.",
                "Contains guidelines, instructions, or operational procedures.",
                "May include internal processes requiring access control."
            ])
        else:
            # Generic findings for unidentified themes
            key_terms = significant_words[:3]
            findings.extend([
                f"Document contains information about {', '.join(key_terms)} and related topics.",
                "Content requires review for sensitive information and access controls.",
                "May contain operational or organizational details requiring protection."
            ])
        
        return findings

    def _detect_content_patterns(self, text_lower: str) -> List[str]:
        """Detect specific content patterns that might indicate sensitive information."""
        patterns = []
        
        # Look for common sensitive data indicators
        if any(term in text_lower for term in ["password", "secret", "key", "token", "credential"]):
            patterns.append("Contains potential authentication credentials requiring secure handling.")
        
        if any(term in text_lower for term in ["confidential", "private", "restricted", "internal"]):
            patterns.append("Marked as confidential or restricted content requiring access controls.")
        
        if any(term in text_lower for term in ["address", "phone", "email", "contact"]):
            patterns.append("Contains contact information that may require privacy protection.")
        
        if any(term in text_lower for term in ["server", "database", "ip", "port", "host"]):
            patterns.append("Contains technical infrastructure details requiring security review.")
        
        return patterns

    def _describe_spreadsheet_content(self, content: Dict[str, Any], category: str) -> str:
        """Generate description for spreadsheet content."""
        worksheets = content.get("worksheets", [])
        
        if not worksheets:
            return "Excel spreadsheet with no readable worksheet data."
        
        sheet_count = len(worksheets)
        first_sheet = worksheets[0]
        
        # Analyze first sheet structure
        max_row = first_sheet.get("max_row", 0)
        max_col = first_sheet.get("max_column", 0)
        sheet_name = first_sheet.get("sheet_name", "Sheet1")
        
        # Look at headers to understand content
        data = first_sheet.get("data", [])
        headers = data[0] if data else []
        
        base_desc = f"Excel spreadsheet with {sheet_count} worksheet(s), containing {max_row} rows and {max_col} columns"
        
        if category == "employee_data":
            if any(term in str(headers).lower() for term in ["employee", "name", "id", "email"]):
                return f"{base_desc}. Contains employee directory or HR data with personal information and organizational details."
        
        elif category == "financial":
            if any(term in str(headers).lower() for term in ["amount", "cost", "price", "payment"]):
                return f"{base_desc}. Contains financial data including transactions, budgets, or accounting information."
        
        elif category == "access_control":
            if any(term in str(headers).lower() for term in ["access", "permission", "role", "token"]):
                return f"{base_desc}. Contains access control data including user permissions, tokens, or security credentials."
        
        # Generic description with header analysis
        if headers and len(headers) > 2:
            header_sample = ", ".join(str(h) for h in headers[:4])
            return f"{base_desc}. Column headers include: {header_sample}."
        
        return f"{base_desc}. Contains structured tabular data for analysis and reporting."

    def _describe_presentation_content(self, content: Dict[str, Any], category: str) -> str:
        """Generate description for presentation content."""
        slides = content.get("slides", [])
        slide_count = content.get("slide_count", len(slides))
        
        if not slides:
            return f"PowerPoint presentation with {slide_count} slides but no readable content."
        
        # Analyze slide content
        has_tables = any(slide.get("tables") for slide in slides)
        has_images = any(
            any(shape.get("shape_type", "").startswith("PICTURE") for shape in slide.get("shapes", []))
            for slide in slides
        )
        
        # Look for title or key content
        title_content = []
        for slide in slides[:3]:  # Check first 3 slides
            for text_item in slide.get("text_content", []):
                text = text_item.get("text", "").strip()
                if text and len(text) > 5:
                    title_content.append(text)
        
        base_desc = f"PowerPoint presentation with {slide_count} slides"
        
        if category == "compliance":
            if any(term in " ".join(title_content).lower() for term in ["review", "audit", "compliance", "policy"]):
                return f"{base_desc} containing compliance documentation, audit reports, or policy reviews."
        
        elif category == "network":
            return f"{base_desc} documenting network architecture, system designs, or technical infrastructure."
        
        elif category == "employee_data":
            return f"{base_desc} with organizational information, team structures, or employee-related content."
        
        # Generic description with content hints
        features = []
        if has_tables:
            features.append("tabular data")
        if has_images:
            features.append("images/diagrams")
        
        feature_text = " and ".join(features) if features else "text content"
        
        if title_content:
            sample_text = title_content[0][:50]
            return f"{base_desc} including {feature_text}. Content includes: \"{sample_text}...\""
        
        return f"{base_desc} including {feature_text} for business or technical communication."

    def _describe_pdf_content(self, content: Dict[str, Any], category: str, text: str) -> str:
        """Generate description for PDF content."""
        page_count = content.get("page_count", 0)
        text_content = content.get("text_content", [])
        tables = content.get("tables", [])
        
        base_desc = f"PDF document with {page_count} page(s)"
        
        if not text_content and not tables:
            return f"{base_desc} with no extractable text content (may be image-based)."
        
        # Analyze first page content
        first_page_text = ""
        if text_content:
            first_page_text = text_content[0].get("text", "")[:200]
        
        if category == "compliance":
            return f"{base_desc} containing compliance documentation, policies, or regulatory information."
        elif category == "financial":
            return f"{base_desc} with financial reports, statements, or transaction records."
        elif category == "network":
            return f"{base_desc} documenting network configurations, technical specifications, or system architecture."
        
        # Generic description
        features = []
        if tables:
            features.append(f"{len(tables)} table(s)")
        if text_content:
            features.append("formatted text")
        
        feature_text = " and ".join(features) if features else "content"
        
        if first_page_text:
            snippet = first_page_text.split('.')[0][:80]
            return f"{base_desc} containing {feature_text}. Begins with: \"{snippet}...\""
        
        return f"{base_desc} containing {feature_text} for documentation or reporting purposes."

    def _describe_document_content(self, content: Dict[str, Any], category: str, text: str) -> str:
        """Generate description for Word document content."""
        paragraphs = content.get("paragraphs", [])
        tables = content.get("tables", [])
        
        para_count = len(paragraphs)
        table_count = len(tables)
        
        base_desc = f"Word document with {para_count} paragraph(s)"
        if table_count > 0:
            base_desc += f" and {table_count} table(s)"
        
        if category == "compliance":
            return f"{base_desc} containing policy documentation, procedures, or compliance guidelines."
        elif category == "employee_data":
            return f"{base_desc} with employee handbook, HR policies, or organizational information."
        
        # Look at first paragraph for context
        if paragraphs:
            first_para = paragraphs[0][:100]
            return f"{base_desc}. Content begins: \"{first_para}...\""
        
        return f"{base_desc} containing formatted text and structured information."

    def _describe_generic_content(self, content: Dict[str, Any], category: str, file_type: str, text: str) -> str:
        """Generate generic description for unknown file types."""
        word_count = len(text.split()) if text else 0
        
        type_name = file_type.split('/')[-1].upper() if '/' in file_type else file_type.upper()
        
        if word_count == 0:
            return f"{type_name} file with no extractable text content."
        
        if category != "general":
            category_desc = {
                "access_control": "access control and security",
                "network": "network and infrastructure",
                "employee_data": "employee and organizational",
                "financial": "financial and accounting",
                "compliance": "compliance and regulatory",
                "infrastructure": "system and infrastructure"
            }.get(category, category)
            
            return f"{type_name} file containing {category_desc} information with {word_count} words of content."
        
        return f"{type_name} file with {word_count} words of structured content for analysis."

    def _generate_key_findings(self, content: Dict[str, Any], content_analysis: Dict[str, Any], 
                             sensitive_analysis: Dict[str, Any], file_type: str) -> List[str]:
        """Generate key findings based on actual content analysis."""
        findings = []
        
        categories = content_analysis["categories"]
        primary_category = content_analysis["primary_category"]
        sensitive_categories = sensitive_analysis["categories"]
        sensitive_count = sensitive_analysis["total_sensitive_items"]
        
        # Sensitive data findings (always based on actual detection)
        if sensitive_count > 0:
            findings.append(f"Contains {sensitive_count} sensitive data elements across {len(sensitive_categories)} categories")
            
            # Specific sensitive data types found
            if "email" in sensitive_categories:
                findings.append(f"Identified {sensitive_categories['email']} email addresses requiring protection")
            if "phone" in sensitive_categories:
                findings.append(f"Found {sensitive_categories['phone']} phone numbers needing masking")
            if "credit_card" in sensitive_categories:
                findings.append(f"Contains {sensitive_categories['credit_card']} payment card numbers requiring PCI compliance")
            if "ssn" in sensitive_categories:
                findings.append(f"Detected {sensitive_categories['ssn']} social security numbers needing encryption")
        
        # Content structure findings based on actual file content
        if file_type.startswith("image/"):
            ocr_text = content.get("ocr_text", "").strip()
            logo_detections = content.get("logo_detections", [])
            text_redactions = content.get("text_redactions", [])
            
            # Dynamic content analysis for any type of content
            if ocr_text:
                findings.extend(self._generate_dynamic_findings(ocr_text, content))
            
            # Enhanced analysis for images without OCR text
            elif not ocr_text:
                # Get image info for analysis
                image_info = content.get("image_info", {})
                width = image_info.get("width", 0)
                height = image_info.get("height", 0)
                
                if width and height:
                    aspect_ratio = width / height if height > 0 else 1
                    
                    # Provide contextual analysis based on image characteristics
                    if 1.7 <= aspect_ratio <= 1.8:  # ~16:9 (screenshot-like)
                        findings.extend([
                            "System interface or application screenshot captured for documentation.",
                            "May contain sensitive configuration details or user information.",
                            "Requires review for data exposure in UI elements, menus, or displayed content."
                        ])
                    elif 1.3 <= aspect_ratio <= 1.6:  # ~4:3 to wider (monitor-like)
                        findings.extend([
                            "Security monitoring display or control panel interface.",
                            "Likely contains operational status, alerts, or system information.",
                            "May expose network topology, device status, or security configurations."
                        ])
                    elif aspect_ratio > 2:  # Wide format
                        findings.extend([
                            "Network infrastructure diagram or system architecture layout.",
                            "Contains technical specifications and connectivity information.",
                            "May reveal network topology, IP ranges, or system dependencies."
                        ])
                    elif 0.7 <= aspect_ratio <= 1.3:  # Square-ish
                        findings.extend([
                            "Access control panel or security device interface.",
                            "Physical security system component requiring access management.",
                            "May contain authentication mechanisms or entry control features."
                        ])
                    else:
                        findings.extend([
                            "Security system interface or infrastructure component.",
                            "Requires assessment for sensitive information exposure.",
                            "May contain operational data or configuration details."
                        ])
                else:
                    findings.extend([
                        "Security infrastructure component or system interface.",
                        "Visual content requires manual review for sensitive information.",
                        "May contain operational details or configuration data."
                    ])
            
            if logo_detections:
                findings.append(f"Detected {len(logo_detections)} logo(s) or branding elements requiring review")
            
            if text_redactions:
                findings.append(f"Automatically redacted {len(text_redactions)} sensitive text regions")
        
        elif "spreadsheet" in file_type:
            worksheets = content.get("worksheets", [])
            if worksheets:
                total_rows = sum(ws.get("max_row", 0) for ws in worksheets)
                total_cols = sum(ws.get("max_column", 0) for ws in worksheets)
                findings.append(f"Structured data with {total_rows} rows and {total_cols} columns across {len(worksheets)} worksheet(s)")
                
                # Analyze headers for content type
                for ws in worksheets:
                    data = ws.get("data", [])
                    if data and len(data) > 0:
                        headers = [str(h).lower() for h in data[0]]
                        if any("employee" in h or "name" in h for h in headers):
                            findings.append("Contains employee or personnel data requiring HR governance")
                        if any("email" in h or "phone" in h for h in headers):
                            findings.append("Includes contact information subject to privacy regulations")
                        break
        
        elif "presentation" in file_type:
            slides = content.get("slides", [])
            slide_count = content.get("slide_count", len(slides))
            
            if slides:
                findings.append(f"Presentation contains {slide_count} slides with structured content")
                
                # Check for tables and content types
                total_tables = sum(len(slide.get("tables", [])) for slide in slides)
                if total_tables > 0:
                    findings.append(f"Includes {total_tables} table(s) with tabular data requiring governance")
                
                # Check for text content
                total_text_items = sum(len(slide.get("text_content", [])) for slide in slides)
                if total_text_items > 0:
                    findings.append(f"Contains {total_text_items} text elements across slides")
        
        elif file_type == "application/pdf":
            page_count = content.get("page_count", 0)
            text_content = content.get("text_content", [])
            tables = content.get("tables", [])
            
            if page_count > 0:
                findings.append(f"PDF document with {page_count} page(s) of content")
            
            if text_content:
                total_text_pages = len(text_content)
                findings.append(f"Extractable text found on {total_text_pages} page(s)")
            
            if tables:
                findings.append(f"Contains {len(tables)} table(s) with structured data")
        
        # Category-based findings (only if we have strong evidence)
        if primary_category != "general" and content_analysis["confidence"] > 30:
            category_findings = {
                "access_control": "Access control or security system documentation identified",
                "employee_data": "Employee or personnel information requiring HR data governance",
                "financial": "Financial data subject to accounting and audit requirements",
                "network": "Network infrastructure documentation requiring IT security review",
                "compliance": "Compliance or regulatory documentation requiring controlled access",
                "infrastructure": "System infrastructure details requiring security classification"
            }
            
            if primary_category in category_findings:
                findings.append(category_findings[primary_category])
        
        # Default findings if none generated
        if not findings:
            if sensitive_count == 0:
                findings.append("No sensitive data patterns detected in content")
            else:
                findings.append("Content requires standard data governance policies")
            
            # Add a basic structural finding
            if file_type.startswith("image/"):
                findings.append("Image file processed for content analysis")
            elif "spreadsheet" in file_type:
                findings.append("Spreadsheet data structure analyzed")
            elif "presentation" in file_type:
                findings.append("Presentation content structure reviewed")
            else:
                findings.append("Document content analyzed for data governance requirements")
        
        return findings
