#!/usr/bin/env python3
"""
Comprehensive dry run test for all files in the Files directory
Tests both masking and analysis functionality directly without server
"""

import os
import json
from pathlib import Path
from datetime import datetime
from file_processor import FileProcessor
from sensitive_data_masking import SensitiveDataMasker
from server.analysis.advanced_analyzer import AdvancedDataAnalyzer

def comprehensive_test():
    """Run comprehensive tests on all files"""
    
    print("🔍 COMPREHENSIVE DRY RUN TEST")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print()
    
    # Initialize components
    processor = FileProcessor(use_model_detector=True, enable_logo_redaction=True, enable_ocr=True)
    masker = SensitiveDataMasker(use_model_detector=True)
    analyzer = AdvancedDataAnalyzer()
    
    files_dir = Path("Files")
    if not files_dir.exists():
        print("❌ Files directory not found")
        return
    
    # Get all test files
    test_files = []
    for pattern in ["*.pdf", "*.xlsx", "*.pptx", "*.png", "*.jpg", "*.jpeg"]:
        test_files.extend(files_dir.glob(pattern))
    
    test_files.sort()
    
    print(f"📁 Found {len(test_files)} test files:")
    for f in test_files:
        print(f"   - {f.name}")
    print()
    
    results = {
        "test_summary": {
            "total_files": len(test_files),
            "successful_extractions": 0,
            "successful_maskings": 0,
            "successful_analyses": 0,
            "failed_files": []
        },
        "file_results": {}
    }
    
    # Test each file
    for i, file_path in enumerate(test_files, 1):
        print(f"📄 [{i}/{len(test_files)}] Testing: {file_path.name}")
        print("-" * 40)
        
        file_result = {
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "extraction": {"success": False, "error": None},
            "masking": {"success": False, "error": None, "sensitive_count": 0},
            "analysis": {"success": False, "error": None}
        }
        
        try:
            # Step 1: File type detection
            file_type = processor.get_file_type(str(file_path))
            print(f"   📋 File Type: {file_type}")
            file_result["file_type"] = file_type
            
            # Step 2: Content extraction
            extractor = processor.extractors.get(file_type)
            if not extractor:
                raise Exception(f"No extractor available for {file_type}")
            
            print(f"   🔧 Using extractor: {extractor.__class__.__name__}")
            
            # Extract content
            if file_type == "application/pdf":
                content = extractor.extract(str(file_path), enable_ocr=True)
            else:
                content = extractor.extract(str(file_path))
            
            print(f"   📊 Content keys: {list(content.keys())}")
            file_result["extraction"]["success"] = True
            file_result["content_keys"] = list(content.keys())
            results["test_summary"]["successful_extractions"] += 1
            
            # Special handling for images
            if file_type.startswith("image/"):
                if "ocr_text" in content:
                    ocr_text = content["ocr_text"].strip()
                    print(f"   📝 OCR Text: {len(ocr_text)} characters")
                    if ocr_text:
                        print(f"   📖 Sample: {repr(ocr_text[:50])}...")
                    file_result["ocr_length"] = len(ocr_text)
                
                if "image_info" in content:
                    info = content["image_info"]
                    print(f"   🖼️  Image: {info.get('width')}x{info.get('height')} {info.get('format')}")
                    file_result["image_info"] = info
                
                if "logo_detections" in content:
                    logos = content["logo_detections"]
                    print(f"   🏷️  Logo detections: {len(logos)}")
                    file_result["logo_detections"] = len(logos)
                
                if "text_redactions" in content:
                    redactions = content["text_redactions"]
                    print(f"   🔒 Text redactions: {len(redactions)}")
                    file_result["text_redactions"] = len(redactions)
            
            # Step 3: Masking
            print(f"   🎭 Applying masking...")
            masked_content = masker.mask_sensitive_data(content)
            
            # Count sensitive items detected
            sensitive_count = 0
            def count_sensitive(obj):
                nonlocal sensitive_count
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key.endswith('_masked') or 'MASKED' in str(value):
                            sensitive_count += 1
                        else:
                            count_sensitive(value)
                elif isinstance(obj, list):
                    for item in obj:
                        count_sensitive(item)
            
            count_sensitive(masked_content)
            
            print(f"   🔍 Sensitive items detected: {sensitive_count}")
            file_result["masking"]["success"] = True
            file_result["masking"]["sensitive_count"] = sensitive_count
            results["test_summary"]["successful_maskings"] += 1
            
            # Step 4: Analysis
            print(f"   🤖 Running analysis...")
            analysis_result = analyzer.analyze(content, file_type)
            
            print(f"   📈 Risk Level: {analysis_result['riskLevel']}")
            print(f"   📊 Data Quality: {analysis_result['dataQuality']}")
            print(f"   🔒 Sensitive Fields: {analysis_result['sensitiveFields']}")
            print(f"   📂 Categories: {', '.join(analysis_result.get('contentCategories', []))}")
            print(f"   📝 Description: {analysis_result['description'][:100]}...")
            
            file_result["analysis"]["success"] = True
            file_result["analysis"]["result"] = {
                "riskLevel": analysis_result["riskLevel"],
                "dataQuality": analysis_result["dataQuality"],
                "sensitiveFields": analysis_result["sensitiveFields"],
                "contentCategories": analysis_result.get("contentCategories", []),
                "description": analysis_result["description"]
            }
            results["test_summary"]["successful_analyses"] += 1
            
            print(f"   ✅ SUCCESS: All steps completed")
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            file_result["error"] = str(e)
            results["test_summary"]["failed_files"].append({
                "file": file_path.name,
                "error": str(e)
            })
        
        results["file_results"][file_path.name] = file_result
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    summary = results["test_summary"]
    print(f"Total files tested: {summary['total_files']}")
    print(f"Successful extractions: {summary['successful_extractions']}")
    print(f"Successful maskings: {summary['successful_maskings']}")
    print(f"Successful analyses: {summary['successful_analyses']}")
    print(f"Failed files: {len(summary['failed_files'])}")
    
    if summary["failed_files"]:
        print("\n❌ FAILED FILES:")
        for fail in summary["failed_files"]:
            print(f"   - {fail['file']}: {fail['error']}")
    
    # Save detailed results
    results_file = f"dry_run_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Calculate success rates
    total = summary['total_files']
    extraction_rate = (summary['successful_extractions'] / total) * 100 if total > 0 else 0
    masking_rate = (summary['successful_maskings'] / total) * 100 if total > 0 else 0
    analysis_rate = (summary['successful_analyses'] / total) * 100 if total > 0 else 0
    
    print(f"\n📈 SUCCESS RATES:")
    print(f"   Extraction: {extraction_rate:.1f}%")
    print(f"   Masking: {masking_rate:.1f}%")
    print(f"   Analysis: {analysis_rate:.1f}%")
    
    return results

if __name__ == "__main__":
    comprehensive_test()
