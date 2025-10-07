"""
Focused test on type2.jpg which showed ATMEGA328P detection
"""
import cv2
from ocr_engine import OCREngine
from ic_marking_extractor import ICMarkingExtractor
from advanced_ic_preprocessing import ICMarkingPreprocessor

def test_type2():
    print("=" * 80)
    print("FOCUSED TEST: type2.jpg (Atmel ATmega328P)")
    print("=" * 80)
    print()
    
    # Load image
    image = cv2.imread("test_images/type2.jpg")
    if image is None:
        print("❌ Failed to load image")
        return
    
    print(f"✓ Loaded: {image.shape[1]}x{image.shape[0]}")
    print()
    
    # Initialize
    ocr = OCREngine()
    extractor = ICMarkingExtractor()
    preprocessor = ICMarkingPreprocessor()
    
    print("🔍 Testing Each OCR Method Individually:")
    print("=" * 80)
    
    # Test EasyOCR with each preprocessing variant
    print("\n📌 EasyOCR with all preprocessing variants:")
    print("-" * 80)
    variants = preprocessor.create_preprocessing_variants(image)
    
    for i, (variant_name, preprocessed) in enumerate(variants, 1):
        try:
            results = ocr.easyocr_reader.readtext(preprocessed)
            if results:
                texts = [text for _, text, conf in results]
                combined = ' '.join(texts)
                avg_conf = sum(conf for _, _, conf in results) / len(results)
                print(f"\n{i}. {variant_name}:")
                print(f"   Raw: {combined}")
                print(f"   Conf: {avg_conf:.2%}")
                
                # Try to extract components
                parsed = extractor.parse_ic_marking(combined)
                if any(parsed.values()):
                    print(f"   → Manufacturer: {parsed['manufacturer']}")
                    print(f"   → Part Number: {parsed['part_number']}")
                    print(f"   → Date Code: {parsed['date_code']}")
        except Exception as e:
            print(f"\n{i}. {variant_name}: Error - {e}")
    
    print("\n" + "=" * 80)
    print("\n📌 PaddleOCR with all preprocessing variants:")
    print("-" * 80)
    
    for i, (variant_name, preprocessed) in enumerate(variants, 1):
        try:
            results = ocr.paddle_ocr.ocr(preprocessed, cls=True)
            if results and results[0]:
                texts = [line[1][0] for line in results[0]]
                combined = ' '.join(texts)
                confs = [line[1][1] for line in results[0]]
                avg_conf = sum(confs) / len(confs) if confs else 0
                print(f"\n{i}. {variant_name}:")
                print(f"   Raw: {combined}")
                print(f"   Conf: {avg_conf:.2%}")
                
                # Try to extract components
                parsed = extractor.parse_ic_marking(combined)
                if any(parsed.values()):
                    print(f"   → Manufacturer: {parsed['manufacturer']}")
                    print(f"   → Part Number: {parsed['part_number']}")
                    print(f"   → Date Code: {parsed['date_code']}")
        except Exception as e:
            print(f"\n{i}. {variant_name}: Error - {e}")
    
    print("\n" + "=" * 80)
    print("\n📝 FINAL ENSEMBLE RESULT:")
    print("=" * 80)
    
    marking_regions = [{'image': image}]
    ocr_result = ocr.extract_text(marking_regions, method='ensemble')
    
    print(f"\nRaw OCR Text:")
    print(repr(ocr_result['text']))
    print(f"\nConfidence: {ocr_result['confidence']:.2%}")
    
    print(f"\n🎯 Extracted Components (Enhanced):")
    parsed = extractor.parse_ic_marking(ocr_result['text'])
    print(f"   Manufacturer:  {parsed['manufacturer'] or '❌ Not found'}")
    print(f"   Part Number:   {parsed['part_number'] or '❌ Not found'}")
    print(f"   Date Code:     {parsed['date_code'] or '❌ Not found'}")
    print(f"   Lot Code:      {parsed['lot_code'] or '❌ Not found'}")
    
    print()
    print("=" * 80)
    print("EXPECTED VALUES (from image):")
    print("   Manufacturer:  Atmel (now Microchip)")
    print("   Part Number:   ATMEGA328P-AU")
    print("   Date Code:     0723 (2007, week 23)")
    print("=" * 80)


if __name__ == "__main__":
    test_type2()
