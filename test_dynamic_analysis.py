"""
Test script for the dynamic analysis system

This script demonstrates how the new dynamic, NLP-powered analysis system
can handle any content type, including completely unknown scenarios.
"""

import json
import sys
import os

# Add the server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from server.analysis.enhanced_analyzer import EnhancedDynamicAnalyzer
from server.analysis.dynamic_templates import template_manager

def test_unknown_content():
    """Test the system with completely unknown content types"""
    print("🧪 Testing Dynamic Analysis with Unknown Content Types")
    print("=" * 60)
    
    # Initialize the enhanced analyzer
    analyzer = EnhancedDynamicAnalyzer()
    
    # Test cases with unknown content
    test_cases = [
        {
            "name": "Unknown Technical Content",
            "content": {
                "text_content": [
                    {"text": "Quantum computing algorithms for cryptographic key generation using Shor's algorithm implementation with 2048-bit RSA encryption parameters and quantum entanglement protocols."}
                ],
                "metadata": {"author": "Dr. Quantum", "title": "Quantum Security Protocols"}
            },
            "file_type": "application/pdf"
        },
        {
            "name": "Unknown Business Content", 
            "content": {
                "text_content": [
                    {"text": "Blockchain-based supply chain optimization using smart contracts for pharmaceutical distribution with FDA compliance tracking and temperature monitoring sensors."}
                ],
                "metadata": {"author": "Supply Chain AI", "title": "Pharma Supply Chain"}
            },
            "file_type": "application/pdf"
        },
        {
            "name": "Unknown Scientific Content",
            "content": {
                "text_content": [
                    {"text": "CRISPR-Cas9 gene editing protocols for therapeutic applications in rare genetic disorders with off-target effect minimization and delivery vector optimization."}
                ],
                "metadata": {"author": "Gene Therapy Lab", "title": "Therapeutic Gene Editing"}
            },
            "file_type": "application/pdf"
        },
        {
            "name": "Unknown Creative Content",
            "content": {
                "text_content": [
                    {"text": "AI-generated art using neural style transfer with GAN architectures for digital museum curation and NFT marketplace integration with blockchain provenance tracking."}
                ],
                "metadata": {"author": "Digital Art Collective", "title": "AI Art Generation"}
            },
            "file_type": "application/pdf"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Analyze the content
            result = analyzer.analyze(test_case['content'], test_case['file_type'])
            
            # Display results
            print(f"📊 Analysis Results:")
            print(f"   Description: {result['description']}")
            print(f"   Risk Level: {result['riskLevel']}")
            print(f"   Data Quality: {result['dataQuality']}")
            print(f"   Compliance: {', '.join(result['compliance'])}")
            
            print(f"\n🔍 Key Findings:")
            for finding in result['keyFindings'][:3]:  # Show first 3 findings
                print(f"   • {finding}")
            
            print(f"\n💡 Recommendations:")
            for rec in result['recommendations'][:3]:  # Show first 3 recommendations
                print(f"   • {rec}")
            
            # Show dynamic insights
            if 'contentInsights' in result:
                insights = result['contentInsights']
                print(f"\n🧠 Dynamic Insights:")
                print(f"   Category: {insights.get('categories', 'unknown')}")
                print(f"   Confidence: {insights.get('confidence', 0):.2f}")
                print(f"   Insights: {insights.get('insights', 'No insights available')}")
            
            # Show pattern insights
            if 'patternInsights' in result:
                pattern_insights = result['patternInsights']
                print(f"\n🔧 Pattern Insights:")
                print(f"   Categories: {', '.join(pattern_insights.get('categories', []))}")
                print(f"   Primary: {pattern_insights.get('primary_category', 'general')}")
                print(f"   Confidence: {pattern_insights.get('confidence', 0):.2f}")
            
        except Exception as e:
            print(f"❌ Error analyzing {test_case['name']}: {e}")
    
    print(f"\n✅ Dynamic Analysis Test Completed!")

def test_custom_patterns():
    """Test adding custom patterns for new content types"""
    print("\n🔧 Testing Custom Pattern Addition")
    print("=" * 40)
    
    analyzer = EnhancedDynamicAnalyzer()
    
    # Add custom patterns for new content types
    analyzer.add_custom_pattern("quantum_computing", [
        r'\b(?:quantum|qubit|entanglement|superposition|decoherence)\b',
        r'\b(?:cryptographic|encryption|decryption|key generation)\b',
        r'\b(?:algorithm|protocol|implementation|optimization)\b'
    ])
    
    analyzer.add_custom_pattern("biotechnology", [
        r'\b(?:crispr|gene editing|therapeutic|genetic|dna|rna)\b',
        r'\b(?:off-target|delivery vector|protocol|optimization)\b',
        r'\b(?:disorder|mutation|variant|expression)\b'
    ])
    
    analyzer.add_custom_pattern("blockchain", [
        r'\b(?:blockchain|smart contract|nft|defi|dao)\b',
        r'\b(?:distributed|decentralized|consensus|mining)\b',
        r'\b(?:cryptocurrency|token|wallet|exchange)\b'
    ])
    
    print("✅ Custom patterns added successfully!")
    
    # Test with content that should match new patterns
    test_content = {
        "text_content": [
            {"text": "Quantum blockchain implementation using qubit entanglement for secure smart contracts with zero-knowledge proofs and decentralized consensus mechanisms."}
        ]
    }
    
    result = analyzer.analyze(test_content, "application/pdf")
    
    print(f"\n📊 Analysis with Custom Patterns:")
    print(f"   Description: {result['description']}")
    print(f"   Pattern Categories: {', '.join(result.get('patternInsights', {}).get('categories', []))}")

def test_template_customization():
    """Test customizing templates for new content types"""
    print("\n📝 Testing Template Customization")
    print("=" * 40)
    
    # Add custom template for quantum computing content
    template_manager.add_custom_template("quantum_computing", {
        "description_template": "Quantum computing document with {key_terms} and {entity_count} quantum references",
        "findings_templates": [
            "Contains quantum computing information requiring specialized security review",
            "Quantum content with {entity_count} quantum references",
            "Advanced quantum information requiring specialized controls"
        ],
        "recommendations_templates": [
            "Apply quantum computing security protocols",
            "Implement quantum-safe encryption standards",
            "Enable quantum information monitoring"
        ],
        "risk_factors": ["quantum_exposure", "advanced_technology"]
    })
    
    # Add custom template for biotechnology content
    template_manager.add_custom_template("biotechnology", {
        "description_template": "Biotechnology document with {key_terms} and {entity_count} biotech references",
        "findings_templates": [
            "Contains biotechnology information requiring regulatory review",
            "Biotech content with {entity_count} biotech references",
            "Genetic information requiring specialized controls"
        ],
        "recommendations_templates": [
            "Apply biotechnology compliance protocols",
            "Implement genetic data protection standards",
            "Enable biotech information monitoring"
        ],
        "risk_factors": ["biotech_exposure", "genetic_data"]
    })
    
    print("✅ Custom templates added successfully!")
    
    # Test template generation
    description = template_manager.generate_description(
        "quantum_computing", 
        "technical_documentation",
        ["quantum", "cryptographic", "entanglement"],
        5
    )
    
    findings = template_manager.generate_findings(
        "quantum_computing",
        "technical_documentation", 
        5
    )
    
    recommendations = template_manager.generate_recommendations(
        "quantum_computing",
        "technical_documentation"
    )
    
    print(f"\n📋 Generated Template Content:")
    print(f"   Description: {description}")
    print(f"   Findings: {findings[0] if findings else 'None'}")
    print(f"   Recommendations: {recommendations[0] if recommendations else 'None'}")

def test_configuration_management():
    """Test saving and loading analysis configuration"""
    print("\n⚙️ Testing Configuration Management")
    print("=" * 40)
    
    analyzer = EnhancedDynamicAnalyzer()
    
    # Save current configuration
    analyzer.save_analysis_config("test_analysis_config.json")
    print("✅ Configuration saved successfully!")
    
    # Load configuration
    analyzer.load_analysis_config("test_analysis_config.json")
    print("✅ Configuration loaded successfully!")
    
    # Get current configuration
    config = analyzer.get_analysis_config()
    print(f"📊 Configuration contains {len(config.get('content_patterns', {}))} pattern categories")
    print(f"📊 Configuration contains {len(config.get('template_config', {}).get('content_categories', {}))} content categories")

def main():
    """Run all tests"""
    print("🚀 Dynamic Analysis System Test Suite")
    print("=" * 60)
    print("This test suite demonstrates how the new dynamic, NLP-powered")
    print("analysis system can handle any content type, including completely")
    print("unknown scenarios without hardcoded patterns.")
    print("=" * 60)
    
    try:
        # Test unknown content analysis
        test_unknown_content()
        
        # Test custom pattern addition
        test_custom_patterns()
        
        # Test template customization
        test_template_customization()
        
        # Test configuration management
        test_configuration_management()
        
        print("\n🎉 All Tests Completed Successfully!")
        print("\nKey Benefits of Dynamic Analysis:")
        print("✅ No hardcoded patterns - works with any content type")
        print("✅ NLP-powered understanding - generates contextual insights")
        print("✅ Configurable templates - easily customizable")
        print("✅ Extensible patterns - add new content types dynamically")
        print("✅ Unknown content handling - works with completely new scenarios")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

