"""Test part number extraction from the new OCR results"""

from ic_marking_extractor import ICMarkingExtractor

extractor = ICMarkingExtractor()

test_cases = [
    ("QJRZBABEZ ADC 0831CCN", "ADC0831CCN"),
    ("Cy8c29666-24PvX | 0 05 PHi 2007 CyP 606541", "Cy8C29666"),
    ("Cy8C29666-24PVYI B 05 PHI 1025 CYP 634342", "Cy8C29666"),
    ("SN74HCSOSN", "SN74HC595N"),
    ("AME AtMEQAS2BP AU 1004", "ATMEGA328P"),
    ("dmec AIMEGA328P 2OAU 0723", "ATMEGA328P"),
]

print("=" * 80)
print("TESTING PART NUMBER EXTRACTION")
print("=" * 80)

for ocr_text, expected in test_cases:
    parts = extractor.extract_all_part_numbers(ocr_text)
    print(f"\nOCR Text: {ocr_text}")
    print(f"Expected: {expected}")
    print(f"Extracted: {parts}")
    
    if expected.upper() in [p.upper() for p in parts]:
        print("✅ Correct part number found")
    else:
        print("❌ Expected part number NOT in extracted list")
        if parts:
            print(f"   ⚠️  Got: {parts[0]} instead")
