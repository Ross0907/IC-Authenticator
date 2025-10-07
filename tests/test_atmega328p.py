#!/usr/bin/env python3
"""
Test the ATMEGA328P IC from the UI screenshot to verify authentication improvements
"""

import cv2
import numpy as np
from ocr_engine import OCREngine
from verification_engine import VerificationEngine
from web_scraper import DatasheetScraper

def test_atmega328p():
    """Test ATMEGA328P authentication with improved logic"""
    print("Testing ATMEGA328P IC Authentication")
    print("=" * 50)
    
    # Initialize components
    ocr_engine = OCREngine()
    verifier = VerificationEngine()
    scraper = DatasheetScraper()
    
    # Simulate the ATMEGA328P IC from your UI
    # Based on the UI screenshot, the IC shows: ATMEL ATMEGA328P-AU 1004
    
    # Test with simulated good extracted data
    good_extracted_data = {
        'manufacturer': 'Atmel',
        'part_number': 'ATMEGA328P',
        'date_code': '1004',
        'lot_code': None,
        'package_type': 'AU',
        'confidence': 0.85,
        'raw_text': 'ATMEL ATMEGA328P-AU 1004'
    }
    
    # Test with simulated poor OCR data (like YOLO failure case)
    poor_extracted_data = {
        'manufacturer': None,
        'part_number': None,
        'date_code': None,
        'lot_code': None,
        'package_type': None,
        'confidence': 0.0,
        'raw_text': ''
    }
    
    # Test with partial OCR data (some detection)
    partial_extracted_data = {
        'manufacturer': None,
        'part_number': 'ATMEGA32',  # Slightly different from expected
        'date_code': None,
        'lot_code': None,
        'package_type': None,
        'confidence': 0.65,
        'raw_text': 'ATMEGA32'
    }
    
    test_cases = [
        ("Good OCR Data", good_extracted_data),
        ("Poor OCR Data (YOLO failure)", poor_extracted_data),
        ("Partial OCR Data", partial_extracted_data)
    ]
    
    for test_name, extracted_data in test_cases:
        print(f"\\n📊 Test Case: {test_name}")
        print("-" * 30)
        
        # Simulate official data lookup (will likely fail due to network)
        print("🔍 Looking up official datasheet...")
        official_data = scraper.search_component_datasheet(
            extracted_data.get('part_number', 'ATMEGA328P'),
            extracted_data.get('manufacturer', 'Atmel')
        )
        
        print(f"📋 Official data found: {official_data.get('found', False)}")
        
        # Verify component
        verification_result = verifier.verify_component(
            extracted_data,
            official_data,
            {}  # No image data for this test
        )
        
        # Display results
        print(f"✅ Authentic: {verification_result.get('is_authentic', False)}")
        print(f"📊 Confidence: {verification_result.get('confidence', 0):.1f}%")
        print(f"🔍 Checks Passed: {len(verification_result.get('checks_passed', []))}")
        print(f"❌ Checks Failed: {len(verification_result.get('checks_failed', []))}")
        
        recommendation = verification_result.get('recommendation', '')
        if 'REJECT' in recommendation.upper():
            print("🚨 Recommendation: REJECT")
        else:
            print("✅ Recommendation: ACCEPT (with caution)")
        
        if verification_result.get('anomalies'):
            print(f"⚠️  Anomalies ({len(verification_result['anomalies'])}):")
            for anomaly in verification_result['anomalies'][:2]:  # Show first 2
                print(f"   • {anomaly}")
    
    print("\\n" + "=" * 50)
    print("🎯 ATMEGA328P Test Complete!")
    print("\\nExpected results:")
    print("✅ Good OCR Data: Should be AUTHENTIC")
    print("✅ Poor OCR Data: Should be AUTHENTIC (OCR failure, not counterfeit)")
    print("✅ Partial OCR: Should be AUTHENTIC (close enough match)")

if __name__ == "__main__":
    test_atmega328p()