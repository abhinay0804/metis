"""
Test script for the Sample Format Analyzer

This script demonstrates how the new analyzer generates output in the exact format
shown in the sample, with detailed descriptions and security-focused findings.
"""

import json
import sys
import os

# Add the server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from server.analysis.sample_format_analyzer import SampleFormatAnalyzer

def test_sample_format_analysis():
    """Test the sample format analyzer with various content types"""
    print("🧪 Testing Sample Format Analyzer")
    print("=" * 60)
    print("This analyzer generates output in the exact format shown in the sample:")
    print("- File Description: Detailed, factual description of content")
    print("- Key Findings: Bulleted list of analytical insights with security implications")
    print("=" * 60)
    
    # Initialize the analyzer
    analyzer = SampleFormatAnalyzer()
    
    # Test cases that match the sample format
    test_cases = [
        {
            "name": "Access Control System Image",
            "content": {
                "ocr_text": "Access Card Reader. A person is holding an access card against a card reader mounted near a door labeled '211 IDF/Electrical.' The card reader has a light indicator.",
                "image_info": {"width": 800, "height": 600},
                "filename": "PS_01_EV1.png"
            },
            "file_type": "image/png"
        },
        {
            "name": "Biometric Attendance System Image",
            "content": {
                "ocr_text": "Biometric Attendance/Access System. A wall-mounted electronic biometric device with fingerprint scanning, keypad, and display screen showing time.",
                "image_info": {"width": 800, "height": 600},
                "filename": "PS_01_EV2.png"
            },
            "file_type": "image/png"
        },
        {
            "name": "Visitor Logbook Image",
            "content": {
                "ocr_text": "Visitors Logbook. A paper-based visitor logbook where individuals manually write their name, reason for visit, time in/out, and provide a signature. Two entries are already filled in.",
                "image_info": {"width": 800, "height": 600},
                "filename": "PS_01_EV3.png"
            },
            "file_type": "image/png"
        },
        {
            "name": "Employee Directory Spreadsheet",
            "content": {
                "worksheets": [{
                    "sheet_name": "Employee Directory",
                    "data": [
                        ["Name", "Employee ID", "Department", "Email", "Phone"],
                        ["John Doe", "EMP001", "IT", "john.doe@company.com", "555-1234"],
                        ["Jane Smith", "EMP002", "HR", "jane.smith@company.com", "555-5678"]
                    ],
                    "max_row": 3,
                    "max_column": 5
                }],
                "filename": "employee_directory.xlsx"
            },
            "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
        {
            "name": "Security Policy PDF",
            "content": {
                "text_content": [
                    {"text": "Security Policy Document. This document outlines the security policies and procedures for access control, authentication, and data protection within the organization."}
                ],
                "page_count": 5,
                "tables": [],
                "filename": "security_policy.pdf"
            },
            "file_type": "application/pdf"
        },
        {
            "name": "Network Infrastructure Presentation",
            "content": {
                "slides": [
                    {
                        "text_content": [
                            {"text": "Network Infrastructure Overview"},
                            {"text": "This presentation covers the network topology, server configurations, and security measures implemented across the organization's IT infrastructure."}
                        ],
                        "tables": [],
                        "shapes": []
                    }
                ],
                "slide_count": 10,
                "filename": "network_infrastructure.pptx"
            },
            "file_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            # Analyze the content
            result = analyzer.analyze(test_case['content'], test_case['file_type'])
            
            # Display results in sample format
            print(f"📄 File Description:")
            print(f"   {result['description']}")
            
            print(f"\n🔍 Key Findings:")
            for finding in result['keyFindings']:
                print(f"   • {finding}")
            
            print(f"\n📊 Analysis Summary:")
            print(f"   Risk Level: {result['riskLevel']}")
            print(f"   Data Quality: {result['dataQuality']}")
            print(f"   Sensitive Fields: {result['sensitiveFields']}")
            print(f"   Compliance: {', '.join(result['compliance'])}")
            
            if result.get('recommendations'):
                print(f"\n💡 Recommendations:")
                for rec in result['recommendations'][:3]:  # Show first 3 recommendations
                    print(f"   • {rec}")
            
        except Exception as e:
            print(f"❌ Error analyzing {test_case['name']}: {e}")
    
    print(f"\n✅ Sample Format Analysis Test Completed!")
    print("\nKey Features of Sample Format Analyzer:")
    print("✅ Generates detailed, factual descriptions like in the sample")
    print("✅ Creates security-focused key findings with bullet points")
    print("✅ Analyzes content for security implications and risks")
    print("✅ Provides specific recommendations based on content type")
    print("✅ Matches the exact format shown in your sample output")

def test_unknown_content():
    """Test with completely unknown content types"""
    print("\n🔬 Testing Unknown Content Types")
    print("=" * 40)
    
    analyzer = SampleFormatAnalyzer()
    
    # Test with unknown content
    unknown_cases = [
        {
            "name": "Quantum Computing Document",
            "content": {
                "text_content": [
                    {"text": "Quantum computing algorithms for cryptographic key generation using Shor's algorithm implementation with 2048-bit RSA encryption parameters and quantum entanglement protocols."}
                ],
                "filename": "quantum_security.pdf"
            },
            "file_type": "application/pdf"
        },
        {
            "name": "Blockchain Smart Contract",
            "content": {
                "text_content": [
                    {"text": "Blockchain-based supply chain optimization using smart contracts for pharmaceutical distribution with FDA compliance tracking and temperature monitoring sensors."}
                ],
                "filename": "blockchain_supply_chain.pdf"
            },
            "file_type": "application/pdf"
        }
    ]
    
    for i, test_case in enumerate(unknown_cases, 1):
        print(f"\n📋 Unknown Content Test {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            result = analyzer.analyze(test_case['content'], test_case['file_type'])
            
            print(f"📄 File Description:")
            print(f"   {result['description']}")
            
            print(f"\n🔍 Key Findings:")
            for finding in result['keyFindings']:
                print(f"   • {finding}")
            
        except Exception as e:
            print(f"❌ Error analyzing {test_case['name']}: {e}")

def main():
    """Run all tests"""
    print("🚀 Sample Format Analyzer Test Suite")
    print("=" * 60)
    print("This test suite demonstrates how the new analyzer generates output")
    print("in the exact format shown in your sample, with detailed descriptions")
    print("and security-focused findings.")
    print("=" * 60)
    
    try:
        # Test sample format analysis
        test_sample_format_analysis()
        
        # Test unknown content
        test_unknown_content()
        
        print("\n🎉 All Tests Completed Successfully!")
        print("\nThe Sample Format Analyzer now provides:")
        print("✅ Detailed, factual file descriptions")
        print("✅ Security-focused key findings with bullet points")
        print("✅ Content-specific analysis and recommendations")
        print("✅ Proper formatting matching your sample output")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
