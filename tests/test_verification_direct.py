#!/usr/bin/env python3
"""
Simple test of verification with manually created data
"""

from verification_engine import VerificationEngine

def test_verification_directly():
    """Test verification logic directly with known data"""
    print("Testing Verification Logic Directly")
    print("=" * 45)
    
    verifier = VerificationEngine()
    
    # Test case 1: Good extracted data with good official data
    print("\\n📊 Test 1: Good data with proper official markings")
    extracted_data = {
        'manufacturer': 'Atmel',
        'part_number': 'ATMEGA328P',
        'date_code': '1004',
        'confidence': 0.85
    }
    
    official_data = {
        'found': True,
        'part_marking': 'ATMEGA328P',
        'date_code_format': 'YYWW',
        'package_marking': '-AU, -PU'
    }
    
    result = verifier.verify_component(extracted_data, official_data, {})
    print(f"✅ Authentic: {result.get('is_authentic', False)}")
    print(f"📊 Confidence: {result.get('confidence', 0):.1f}%")
    print(f"🔍 Checks Passed: {len(result.get('checks_passed', []))}")
    print(f"❌ Checks Failed: {len(result.get('checks_failed', []))}")
    
    # Test case 2: Good extracted data with no official data
    print("\\n📊 Test 2: Good extracted data, no official data")
    official_data_missing = {'found': False}
    
    result2 = verifier.verify_component(extracted_data, official_data_missing, {})
    print(f"✅ Authentic: {result2.get('is_authentic', False)}")
    print(f"📊 Confidence: {result2.get('confidence', 0):.1f}%")
    print(f"🔍 Checks Passed: {len(result2.get('checks_passed', []))}")
    print(f"❌ Checks Failed: {len(result2.get('checks_failed', []))}")
    
    # Test case 3: No extracted data (YOLO failure)
    print("\\n📊 Test 3: No extracted data (OCR failure)")
    extracted_data_empty = {
        'manufacturer': None,
        'part_number': None,
        'date_code': None,
        'confidence': 0.0
    }
    
    result3 = verifier.verify_component(extracted_data_empty, official_data_missing, {})
    print(f"✅ Authentic: {result3.get('is_authentic', False)}")
    print(f"📊 Confidence: {result3.get('confidence', 0):.1f}%")
    print(f"🔍 Checks Passed: {len(result3.get('checks_passed', []))}")
    print(f"❌ Checks Failed: {len(result3.get('checks_failed', []))}")
    
    print("\\n" + "=" * 45)
    print("Expected: Test 1 and 2 should be AUTHENTIC")
    print("Expected: Test 3 should handle OCR failure gracefully")

if __name__ == "__main__":
    test_verification_directly()