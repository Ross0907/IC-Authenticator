#!/usr/bin/env python3
"""
Test the improved authentication logic with simulated Type 1 and Type 2 IC data
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from verification_engine import VerificationEngine
from web_scraper import DatasheetScraper

def test_type1_vs_type2():
    """Test Type 1 (counterfeit) vs Type 2 (authentic) ICs with internet-only verification"""
    print("Testing Type 1 vs Type 2 IC Authentication")
    print("Using ONLY legitimate internet datasheet sources")
    print("=" * 55)
    
    verifier = VerificationEngine()
    scraper = DatasheetScraper()
    
    # Type 1 IC - Should be COUNTERFEIT
    # CRITICAL: NO date code present + suspicious manufacturer text
    type1_data = {
        'manufacturer': 'AmeL',  # Suspicious text - should be "Atmel"
        'part_number': 'ATMEGA328P',
        'date_code': None,  # CRITICAL: Missing date code
        'lot_code': None,
        'confidence': 0.67,  # Lower confidence
        'raw_text': 'AmeL ATMEGA 328p',  # Mixed case, suspicious
        'ocr_confidence': 0.48  # Low OCR confidence
    }
    
    # Type 2 IC - Should be AUTHENTIC  
    # HAS date code + proper manufacturer text
    type2_data = {
        'manufacturer': 'Atmel',  # Proper manufacturer
        'part_number': 'ATMEGA328P',
        'date_code': '0723',  # CRITICAL: Valid date code present
        'lot_code': None,
        'confidence': 1.0,  # High confidence
        'raw_text': 'ATMEGA328P 20AU 0723',  # Clean, professional text
        'ocr_confidence': 0.55  # Reasonable OCR confidence
    }
    
    test_cases = [
        ("Type 1 (Should be COUNTERFEIT)", type1_data),
        ("Type 2 (Should be AUTHENTIC)", type2_data)
    ]
    
    for test_name, extracted_data in test_cases:
        print(f"\\n📊 Testing: {test_name}")
        print("-" * 35)
        
        # Verify component - NO official data provided, must fetch from internet
        result = verifier.verify_component(extracted_data, {}, {})
        
        # Display results
        authentic = result.get('is_authentic', False)
        confidence = result.get('confidence', 0)
        
        print(f"✅ Result: {'AUTHENTIC' if authentic else 'COUNTERFEIT'}")
        print(f"📊 Confidence: {confidence:.1f}%")
        print(f"🔍 Checks Passed: {len(result.get('checks_passed', []))}")
        print(f"❌ Checks Failed: {len(result.get('checks_failed', []))}")
        
        # Show critical failures (especially date code)
        failed_checks = result.get('checks_failed', [])
        for check in failed_checks:
            if 'Date Code' in check or 'CRITICAL' in check:
                print(f"🚨 CRITICAL: {check}")
        
        # Show specific check results
        if 'detailed_scores' in result:
            scores = result['detailed_scores']
            
            # Text quality check
            if 'text_quality' in scores:
                tq = scores['text_quality']
                print(f"📝 Text Quality: {'PASS' if tq.get('passed') else 'FAIL'} ({tq.get('score', 0):.0f})")
                if tq.get('issues'):
                    for issue in tq['issues']:
                        print(f"   ⚠️  {issue}")
            
            # Manufacturer check
            if 'manufacturer' in scores:
                mfr = scores['manufacturer']
                print(f"🏭 Manufacturer: {'PASS' if mfr.get('passed') else 'FAIL'} ({mfr.get('score', 0):.0f})")
                print(f"   Extracted: '{mfr.get('extracted', 'None')}'")
        
        # Show data source verification
        if result.get('data_source') == 'internet_only':
            print(f"🌐 Data Source: Verified internet sources only")
        
        # Show anomalies
        if result.get('anomalies'):
            print(f"⚠️  Anomalies ({len(result['anomalies'])}):")
            for anomaly in result['anomalies'][:3]:  # Show first 3
                print(f"   • {anomaly}")
    
    print("\n" + "=" * 55)
    print("Expected Results:")
    print("✅ Type 1: Should be COUNTERFEIT (no date code + suspicious 'AmeL' text)")
    print("✅ Type 2: Should be AUTHENTIC (has date code + proper markings)")

if __name__ == "__main__":
    test_type1_vs_type2()