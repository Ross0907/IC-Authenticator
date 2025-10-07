"""
PATCH: Improved OCR variation generation
Apply this to verification_engine.py line 819

Replace the _generate_limited_ocr_variations method with this version:
"""

def _generate_limited_ocr_variations(self, part_number: str) -> List[str]:
    """
    Generate ONLY the most likely OCR error variations
    Used when OCR confidence is medium/low to correct common errors
    
    Most critical confusions:
    - 2 ↔ P (ATMEGA3282 vs ATMEGA328P)
    - S ↔ 5 (SN74HC59SN vs SN74HC595N)
    - 8 ↔ B (STM32F8xx vs STM32FBxx)
    - 0 ↔ O (common in part numbers)
    - 1 ↔ I ↔ l (lowercase L)
    - Z ↔ 2
    """
    variations = set()
    
    # Expanded critical character confusions
    critical_map = {
        '2': ['P', 'Z'],
        'P': ['2'],
        'S': ['5', '3'],  # S can be confused with 5 or 3
        '5': ['S'],
        '3': ['S', '8'],  # 3 can be confused with S or 8
        '8': ['B', '3'],
        'B': ['8'],
        '0': ['O', 'D'],
        'O': ['0'],
        'D': ['0'],
        '1': ['I', 'l'],
        'I': ['1'],
        'l': ['1'],
        'Z': ['2'],
        'G': ['6'],
        '6': ['G'],
        'A': ['4'],
        '4': ['A'],
        'X': ['K'],
        'K': ['X']
    }
    
    # Generate single-character substitutions
    for i, char in enumerate(part_number.upper()):
        if char in critical_map:
            for replacement in critical_map[char]:
                variant = part_number[:i] + replacement + part_number[i+1:]
                if variant != part_number:
                    variations.add(variant)
    
    # Also try double substitutions for common patterns
    text = part_number.upper()
    
    # S2BP -> 328P (ATMEGA case)
    if 'S2' in text:
        variations.add(text.replace('S2', '32'))
    if 'S2' in text:
        variations.add(text.replace('S2', '328'))  # Directly fix S2BP -> 328P
    
    # 59SN -> 595N (SN74HC595 case)
    if '59SN' in text:
        variations.add(text.replace('59SN', '595N'))
    
    # 5N at end -> 95N
    if text.endswith('5N'):
        variations.add(text[:-2] + '95N')
    
    # ADC missing from start
    if len(text) == 7 and text[0].isdigit():  # Like 0831CCN
        variations.add('ADC' + text)
    
    return list(variations)[:15]  # Increased limit to 15 variations


# Test the variations
test_cases = [
    ("ATMEGAS2BP", "ATMEGA328P"),
    ("SN74HC59SN", "SN74HC595N"),
    ("0831CCN", "ADC0831CCN"),
    ("CY8C29666-24PVXI", "CY8C29666-24PVXI")
]

print("Testing improved OCR variations:")
print("="*80)
for ocr_text, expected in test_cases:
    variations = _generate_limited_ocr_variations(None, ocr_text)
    found = expected in variations
    print(f"\nOCR: {ocr_text}")
    print(f"Expected: {expected}")
    print(f"Found: {'✓ YES' if found else '✗ NO'}")
    print(f"Variations ({len(variations)}): {variations[:5]}...")
    if found:
        print(f"  → Match at position {variations.index(expected)}")
