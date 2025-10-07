"""
Debug part number extraction
"""
import re
from ic_marking_extractor import ICMarkingExtractor

def test_extraction():
    extractor = ICMarkingExtractor()
    
    test_texts = [
        "4il143 AImEl ATMEGAS28P 20AU 0723",
        "244434 Gi 'AtMee3328P ZOAU 0723 0 0",
        "'AtMee3328P",
        "AtMee3328P",
        "ATMEGA328P",
        "ATMEGAS28P",
    ]
    
    for text in test_texts:
        print(f"\nText: {repr(text)}")
        result = extractor.extract_part_number(text)
        print(f"Result: {result}")
        
        # Also test the regex pattern directly
        pattern = r'(?i)[a@4\']?t\s*m[e3][e3gl][a@4el]\s*\d{2,4}[a-z]{0,3}'
        match = re.search(pattern, text)
        if match:
            print(f"Regex match: {repr(match.group())}")

if __name__ == "__main__":
    test_extraction()
