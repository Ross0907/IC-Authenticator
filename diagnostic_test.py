"""
Diagnostic test to understand OCR performance on test images
Shows preprocessing results and individual OCR engine outputs
"""
import cv2
import os
from ocr_engine import OCREngine
from enhanced_preprocessing import preprocess_engraved_text, preprocess_for_trocr
import numpy as np

def test_single_image(image_path):
    print("=" * 80)
    print(f"DIAGNOSTIC TEST: {os.path.basename(image_path)}")
    print("=" * 80)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load: {image_path}")
        return
    
    print(f"✓ Loaded image: {image.shape[1]}x{image.shape[0]}, channels: {image.shape[2] if len(image.shape) > 2 else 1}")
    print()
    
    # Show preprocessing
    print("📸 Preprocessing Results:")
    preprocessed = preprocess_engraved_text(image)
    print(f"   Preprocessed shape: {preprocessed.shape}")
    print(f"   Preprocessed dtype: {preprocessed.dtype}")
    print(f"   Preprocessed range: {preprocessed.min()} to {preprocessed.max()}")
    print()
    
    # Initialize OCR engine
    print("Initializing OCR engines...")
    ocr = OCREngine()
    print()
    
    # Test individual OCR methods
    print("🔍 Individual OCR Engine Results:")
    print("-" * 80)
    
    # EasyOCR
    print("\n1. EasyOCR:")
    result = ocr._extract_easyocr(image)
    print(f"   Confidence: {result['confidence']:.2%}")
    print(f"   Text: {repr(result['text'][:100])}")
    
    # PaddleOCR
    print("\n2. PaddleOCR:")
    result = ocr._extract_paddle(image)
    print(f"   Confidence: {result['confidence']:.2%}")
    print(f"   Text: {repr(result['text'][:100])}")
    
    # Tesseract
    print("\n3. Tesseract:")
    result = ocr._extract_tesseract(image)
    print(f"   Confidence: {result['confidence']:.2%}")
    print(f"   Text: {repr(result['text'][:100])}")
    
    # TrOCR
    print("\n4. TrOCR:")
    result = ocr._extract_trocr(image)
    print(f"   Confidence: {result['confidence']:.2%}")
    print(f"   Text: {repr(result['text'][:100])}")
    
    # docTR
    print("\n5. docTR:")
    result = ocr._extract_doctr(image)
    print(f"   Confidence: {result['confidence']:.2%}")
    print(f"   Text: {repr(result['text'][:100])}")
    
    print()
    print("-" * 80)
    print("\n📝 Ensemble Result:")
    marking_regions = [{'image': image}]
    ensemble_result = ocr.extract_text(marking_regions, method='ensemble')
    print(f"   Confidence: {ensemble_result['confidence']:.2%}")
    print(f"   Text: {repr(ensemble_result['text'][:100])}")
    print()
    
    print("=" * 80)
    print()


def main():
    test_images_dir = "test_images"
    
    # Test type1.jpg and type2.jpg specifically
    print("\n" + "=" * 80)
    print("TESTING ATMEL ATMEGA328P IMAGES")
    print("=" * 80)
    print()
    
    for filename in ['type1.jpg', 'type2.jpg']:
        path = os.path.join(test_images_dir, filename)
        if os.path.exists(path):
            test_single_image(path)
        else:
            print(f"❌ File not found: {path}\n")
    
    # Also test one screenshot
    print("\n" + "=" * 80)
    print("TESTING SCREENSHOT IMAGE")
    print("=" * 80)
    print()
    
    screenshot_path = os.path.join(test_images_dir, "Screenshot 2025-10-06 222749.png")
    if os.path.exists(screenshot_path):
        test_single_image(screenshot_path)


if __name__ == "__main__":
    main()
