#!/usr/bin/env python3
"""
Debug which specific checks are failing
"""

from verification_engine import VerificationEngine

def debug_verification_checks():
    """Debug exactly which checks are failing"""
    print("Debugging Verification Checks")
    print("=" * 40)
    
    verifier = VerificationEngine()
    
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
    
    print("\\n✅ Checks Passed:")
    for check in result.get('checks_passed', []):
        print(f"   • {check}")
    
    print("\\n❌ Checks Failed:")
    for check in result.get('checks_failed', []):
        print(f"   • {check}")
    
    print("\\n⚠️  Anomalies:")
    for anomaly in result.get('anomalies', []):
        print(f"   • {anomaly}")
    
    print("\\n📊 Detailed Scores:")
    for check, score in result.get('detailed_scores', {}).items():
        print(f"   {check}: {score}")
    
    print(f"\\n📊 Overall Confidence: {result.get('confidence', 0):.1f}%")
    print(f"✅ Final Result: {'AUTHENTIC' if result.get('is_authentic') else 'NOT AUTHENTIC'}")

if __name__ == "__main__":
    debug_verification_checks()