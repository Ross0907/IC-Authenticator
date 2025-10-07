"""
Test the new advanced preprocessing on all test images
Specifically focusing on the new IC images added
"""
import cv2
import os
from ocr_engine import OCREngine
from advanced_ic_preprocessing import ICMarkingPreprocessor
import numpy as np

def test_new_images():
    print("=" * 80)
    print("TESTING NEW ADVANCED IC PREPROCESSING")
    print("=" * 80)
    print()
    
    # Initialize engines
    print("Initializing OCR engine...")
    ocr = OCREngine()
    preprocessor = ICMarkingPreprocessor()
    print("✓ Ready\n")
    
    # Test images
    test_images_dir = "test_images"
    
    # Focus on the new real IC images
    target_images = [
        "sn74hc595n-shift-register-cmos-logic-ic-integrated-circuit-3.jpg",
        "Soic-8-Integrated-Circuit-Chips-Interface-IC-Transceiver-Sn65hvd3082EDR.avif",
        "type1.jpg",
        "type2.jpg"
    ]
    
    for img_file in target_images:
        img_path = os.path.join(test_images_dir, img_file)
        
        if not os.path.exists(img_path):
            print(f"⚠️  File not found: {img_file}")
            continue
        
        print("=" * 80)
        print(f"TEST: {img_file}")
        print("=" * 80)
        
        # Load image
        image = cv2.imread(img_path)
        if image is None:
            print(f"❌ Failed to load image")
            continue
        
        print(f"✓ Loaded: {image.shape[1]}x{image.shape[0]}")
        print()
        
        # Show preprocessing variants
        print("📸 Testing Preprocessing Variants:")
        print("-" * 80)
        variants = preprocessor.create_preprocessing_variants(image)
        for i, (variant_name, preprocessed) in enumerate(variants, 1):
            print(f"{i}. {variant_name}: {preprocessed.shape}, range [{preprocessed.min()}-{preprocessed.max()}]")
        print()
        
        # Test individual OCR methods
        print("🔍 OCR Results by Method:")
        print("-" * 80)
        
        marking_regions = [{'image': image}]
        
        # EasyOCR
        print("\n1. EasyOCR:")
        result = ocr._extract_easyocr(image)
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Variant: {result.get('variant', 'N/A')}")
        print(f"   Text: {repr(result['text'][:150])}")
        
        # PaddleOCR
        print("\n2. PaddleOCR:")
        result = ocr._extract_paddle(image)
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Variant: {result.get('variant', 'N/A')}")
        print(f"   Text: {repr(result['text'][:150])}")
        
        # TrOCR
        print("\n3. TrOCR:")
        result = ocr._extract_trocr(image)
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Text: {repr(result['text'][:150])}")
        
        # docTR
        print("\n4. docTR:")
        result = ocr._extract_doctr(image)
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Text: {repr(result['text'][:150])}")
        
        # Tesseract
        print("\n5. Tesseract:")
        result = ocr._extract_tesseract(image)
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Text: {repr(result['text'][:150])}")
        
        print()
        print("-" * 80)
        
        # Ensemble
        print("\n📝 ENSEMBLE Result:")
        ocr_result = ocr.extract_text(marking_regions, method='ensemble')
        print(f"   Overall Confidence: {ocr_result['confidence']:.2%}")
        print(f"   Extracted Text:")
        print(f"   {repr(ocr_result['text'][:200])}")
        
        # Parse components using enhanced extractor
        from ic_marking_extractor import ICMarkingExtractor
        extractor = ICMarkingExtractor()
        parsed = extractor.parse_ic_marking(ocr_result['text'])
        
        print()
        print("🔍 Parsed Components:")
        print(f"   Manufacturer:  {parsed['manufacturer'] or 'None'}")
        print(f"   Part Number:   {parsed['part_number'] or 'None'}")
        print(f"   Date Code:     {parsed['date_code'] or 'None'}")
        print(f"   Lot Code:      {parsed['lot_code'] or 'None'}")
        
        print()
        print()


if __name__ == "__main__":
    test_new_images()
