"""
Quick Demo: Multi-Part-Number Search
Shows how the system now searches ALL extracted part numbers
"""

from ic_marking_extractor import ICMarkingExtractor

def demo_multi_part_extraction():
    """Demonstrate multi-part-number extraction"""
    print("="*70)
    print("DEMO: Multi-Part-Number Extraction")
    print("="*70)
    
    extractor = ICMarkingExtractor()
    
    # Test cases from user's example and common scenarios
    test_cases = [
        "52CXRZKE4 SN74HC595N",           # User's example: lot code + part number
        "ATMEGA328P-PU 1234A",            # ATmega + lot code
        "LM358N TI 2023",                 # Part + manufacturer + date
        "STM32F103C8T6 9AA 2021",         # STM32 + batch + date
        "AD8232 ACPZ 1922",               # Part + package + date
    ]
    
    print("\nExtracting ALL part numbers from various IC markings:\n")
    
    for i, text in enumerate(test_cases, 1):
        print(f"{i}. Input: '{text}'")
        
        # OLD WAY: Only first match
        single_part = extractor.extract_part_number(text)
        
        # NEW WAY: All possible part numbers
        all_parts = extractor.extract_all_part_numbers(text)
        
        print(f"   Old (single):  {single_part}")
        print(f"   New (all):     {all_parts}")
        print()
    
    print("="*70)
    print("✅ System now extracts ALL possible part numbers!")
    print("✅ Each number is searched for datasheets")
    print("✅ First successful match is used for verification")
    print("="*70)

def demo_verification_search():
    """Demonstrate how verification searches all part numbers"""
    print("\n" + "="*70)
    print("DEMO: Multi-Part-Number Verification Search")
    print("="*70)
    
    print("\nScenario: IC marking contains '52CXRZKE4 SN74HC595N'")
    print("\nOLD BEHAVIOR:")
    print("  1. Extract first part number: 52CXRZKE4")
    print("  2. Search for datasheet: 52CXRZKE4")
    print("  3. Not found → FAIL ❌")
    print("  4. Stop (SN74HC595N never searched)")
    
    print("\nNEW BEHAVIOR:")
    print("  1. Extract ALL part numbers: ['52CXRZKE4', 'SN74HC595N']")
    print("  2. Search for datasheet: 52CXRZKE4")
    print("  3. Not found → Try next...")
    print("  4. Search for datasheet: SN74HC595N")
    print("  5. Found! → SUCCESS ✅")
    print("  6. Use SN74HC595N for verification")
    
    print("\n" + "="*70)
    print("✅ System is now much more robust!")
    print("✅ Works even with lot codes, batch numbers, etc.")
    print("="*70)

def demo_code_example():
    """Show code example"""
    print("\n" + "="*70)
    print("DEMO: Code Example")
    print("="*70)
    
    code = '''
# In verification_engine.py (NEW CODE)

from ic_marking_extractor import ICMarkingExtractor
extractor = ICMarkingExtractor()

# Extract ALL possible part numbers
raw_text = "52CXRZKE4 SN74HC595N"
all_part_numbers = extractor.extract_all_part_numbers(raw_text)
# Returns: ['52CXRZKE4', 'SN74HC595N']

# Try each part number until we find official data
for part_num in all_part_numbers:
    print(f"🌐 Searching for: {part_num}")
    official_data = self.web_scraper.get_ic_official_data(part_num)
    
    if official_data and official_data.get('found'):
        print(f"✅ Found datasheet for: {part_num}")
        break  # Success!
'''
    
    print(code)
    print("="*70)

if __name__ == "__main__":
    demo_multi_part_extraction()
    demo_verification_search()
    demo_code_example()
    
    print("\n🎉 All demonstrations complete!")
    print("Run this demo anytime: python demo_multi_part_search.py")
