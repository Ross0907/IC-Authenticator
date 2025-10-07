"""
Final comprehensive test with all improvements
"""
import cv2
from ocr_engine import OCREngine
from ic_marking_extractor import ICMarkingExtractor
import os

def final_test():
    print("=" * 80)
    print("FINAL COMPREHENSIVE TEST - ALL IMPROVEMENTS APPLIED")
    print("=" * 80)
    print()
    
    ocr = OCREngine()
    extractor = ICMarkingExtractor()
    
    test_images = [
        ("type2.jpg", "Atmel ATmega328P", "ATMEGA328P-AU", "0723"),
        ("type1.jpg", "Atmel ATmega328P", "ATMEGA328P-AU", "1004"),
    ]
    
    for img_file, expected_mfg, expected_part, expected_date in test_images:
        img_path = os.path.join("test_images", img_file)
        if not os.path.exists(img_path):
            continue
        
        print("=" * 80)
        print(f"TEST: {img_file}")
        print("=" * 80)
        
        image = cv2.imread(img_path)
        if image is None:
            print("Failed to load")
            continue
        
        print(f"Size: {image.shape[1]}x{image.shape[0]}")
        
        # Extract
        marking_regions = [{'image': image}]
        ocr_result = ocr.extract_text(marking_regions, method='ensemble')
        
        print(f"\nRaw OCR: {repr(ocr_result['text'][:80])}")
        print(f"Confidence: {ocr_result['confidence']:.1%}")
        
        # Parse
        parsed = extractor.parse_ic_marking(ocr_result['text'])
        
        print("\nExtracted:")
        print(f"  Manufacturer: {parsed['manufacturer']}")
        print(f"  Part Number:  {parsed['part_number']}")
        print(f"  Date Code:    {parsed['date_code']}")
        
        print("\nExpected:")
        print(f"  Manufacturer: {expected_mfg}")
        print(f"  Part Number:  {expected_part}")
        print(f"  Date Code:    {expected_date}")
        
        print("\nResults:")
        mfg_ok = "✓" if parsed['manufacturer'] and expected_mfg.lower() in (parsed['manufacturer'] or '').lower() else "✗"
        part_ok = "✓" if parsed['part_number'] and expected_part[:8] in (parsed['part_number'] or '') else "✗"
        date_ok = "✓" if parsed['date_code'] == expected_date else "✗"
        
        print(f"  Manufacturer: {mfg_ok}")
        print(f"  Part Number:  {part_ok}")
        print(f"  Date Code:    {date_ok}")
        
        print()

if __name__ == "__main__":
    final_test()
