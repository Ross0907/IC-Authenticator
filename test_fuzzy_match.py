"""Test fuzzy matching for OCR error correction"""

from verification_engine import VerificationEngine
from ic_marking_extractor import ICMarkingExtractor

# Initialize
ve = VerificationEngine()
ext = ICMarkingExtractor()

# Test case: type2.jpg OCR result with error (3282 instead of 328P)
test_data = {
    'raw_text': 'AMEl ATMEGA3282 20AU 0723',
    'manufacturer': 'Atmel',
    'date_code': '0723'
}

print("Testing fuzzy matching for OCR error correction")
print("=" * 60)
print(f"Input text: {test_data['raw_text']}")
print(f"Expected: ATMEGA328P (OCR read as: ATMEGA3282)")
print("=" * 60)

# Run verification with fuzzy matching
result = ve.verify_component(test_data, {}, {})

print("\n=== VERIFICATION RESULT ===")
print(f"Is Authentic: {result.get('is_authentic', False)}")
print(f"Confidence: {result.get('confidence', 0):.1f}%")
print(f"Matched Part: {test_data.get('part_number', 'None')}")
print(f"Checks Passed: {len(result.get('checks_passed', []))}")
print(f"Checks Failed: {len(result.get('checks_failed', []))}")

if result.get('checks_passed'):
    print("\nPassed checks:")
    for check in result['checks_passed']:
        print(f"  ✓ {check}")

if result.get('checks_failed'):
    print("\nFailed checks:")
    for check in result['checks_failed']:
        print(f"  ✗ {check}")

print("\n" + "=" * 60)
if test_data.get('part_number') == 'ATMEGA328P':
    print("✅ SUCCESS: Fuzzy matching corrected OCR error!")
    print("   OCR read: ATMEGA3282 → Found datasheet for: ATMEGA328P")
elif 'ATMEGA328P' in str(result):
    print("⚠️ PARTIAL: Found ATMEGA328P but not set as part_number")
else:
    print("❌ FAILED: Did not correct OCR error")
