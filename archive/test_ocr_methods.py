"""
Test Advanced OCR Installation
Quick verification of available OCR methods
"""

def test_ocr_availability():
    """Test which OCR methods are available"""
    print("\n" + "="*70)
    print("TESTING OCR ENGINE AVAILABILITY")
    print("="*70 + "\n")
    
    available = []
    unavailable = []
    
    # Test EasyOCR
    try:
        import easyocr
        print("✓ EasyOCR: Available")
        available.append("EasyOCR")
    except Exception as e:
        print(f"✗ EasyOCR: Not available - {str(e)[:40]}")
        unavailable.append("EasyOCR")
    
    # Test PaddleOCR
    try:
        from paddleocr import PaddleOCR
        print("✓ PaddleOCR: Available")
        available.append("PaddleOCR")
    except Exception as e:
        print(f"✗ PaddleOCR: Not available - {str(e)[:40]}")
        unavailable.append("PaddleOCR")
    
    # Test Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✓ Tesseract: Available")
        available.append("Tesseract")
    except Exception as e:
        print(f"✗ Tesseract: Not available - {str(e)[:40]}")
        unavailable.append("Tesseract")
    
    print("\n" + "-"*70)
    print("ADVANCED OCR METHODS")
    print("-"*70 + "\n")
    
    # Test TrOCR
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        print("✓ TrOCR: Available (Transformer-based, High Accuracy)")
        available.append("TrOCR")
    except Exception as e:
        print(f"✗ TrOCR: Not available - {str(e)[:40]}")
        print("  Install with: pip install transformers torch")
        unavailable.append("TrOCR")
    
    # Test docTR
    try:
        from doctr.models import ocr_predictor
        print("✓ docTR: Available (Fast Document OCR)")
        available.append("docTR")
    except Exception as e:
        print(f"✗ docTR: Not available - {str(e)[:40]}")
        print("  Install with: pip install python-doctr[torch]")
        unavailable.append("docTR")
    
    # Test Keras-OCR
    try:
        import keras_ocr
        print("✓ Keras-OCR: Available (Balanced Performance)")
        available.append("Keras-OCR")
    except Exception as e:
        print(f"✗ Keras-OCR: Not available - {str(e)[:40]}")
        print("  Install with: pip install keras-ocr tensorflow")
        unavailable.append("Keras-OCR")
    
    # Test CRAFT
    try:
        from craft_text_detector import Craft
        print("✓ CRAFT: Available (Text Detection)")
        available.append("CRAFT")
    except Exception as e:
        print(f"✗ CRAFT: Not available - {str(e)[:40]}")
        print("  Install with: pip install craft-text-detector")
        unavailable.append("CRAFT")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n✓ Available Methods ({len(available)}): {', '.join(available)}")
    print(f"✗ Unavailable Methods ({len(unavailable)}): {', '.join(unavailable)}")
    
    if len(available) >= 3:
        print("\n✓ System is ready! You have enough OCR methods for good accuracy.")
    else:
        print("\n⚠ Warning: Only {len(available)} OCR methods available.")
        print("  Consider installing more methods for better accuracy.")
        print("  See ADVANCED_OCR_INSTALL.md for installation instructions.")
    
    print("\n" + "="*70 + "\n")
    
    return available, unavailable


def test_ocr_on_image():
    """Test OCR extraction on sample image"""
    import cv2
    import os
    
    print("\n" + "="*70)
    print("TESTING OCR ON SAMPLE IMAGE")
    print("="*70 + "\n")
    
    # Check for test image
    test_paths = [
        'test_images/ADC0831_0-300x300.png',
        'test_images/Screenshot 2025-10-06 222749.png',
        'test_images/Screenshot 2025-10-06 222803.png'
    ]
    
    test_image = None
    for path in test_paths:
        if os.path.exists(path):
            test_image = path
            break
    
    if test_image is None:
        print("✗ No test images found in test_images/ folder")
        print("  Place an IC image in test_images/ folder to test OCR")
        return
    
    print(f"Testing with image: {test_image}\n")
    
    # Load image
    image = cv2.imread(test_image)
    if image is None:
        print(f"✗ Failed to load image: {test_image}")
        return
    
    # Try each available OCR method
    from ocr_engine import OCREngine
    
    engine = OCREngine()
    
    print("Running OCR methods...\n")
    print("-"*70)
    
    # EasyOCR
    try:
        result = engine._extract_easyocr(image)
        print(f"EasyOCR Result:")
        print(f"  Text: {result['text'][:80]}...")
        print(f"  Confidence: {result['confidence']:.2f}\n")
    except Exception as e:
        print(f"EasyOCR failed: {e}\n")
    
    # PaddleOCR
    try:
        result = engine._extract_paddle(image)
        print(f"PaddleOCR Result:")
        print(f"  Text: {result['text'][:80]}...")
        print(f"  Confidence: {result['confidence']:.2f}\n")
    except Exception as e:
        print(f"PaddleOCR failed: {e}\n")
    
    # TrOCR (if available)
    try:
        result = engine._extract_trocr(image)
        if result['confidence'] > 0:
            print(f"TrOCR Result:")
            print(f"  Text: {result['text'][:80]}...")
            print(f"  Confidence: {result['confidence']:.2f}\n")
    except Exception as e:
        pass
    
    # docTR (if available)
    try:
        result = engine._extract_doctr(image)
        if result['confidence'] > 0:
            print(f"docTR Result:")
            print(f"  Text: {result['text'][:80]}...")
            print(f"  Confidence: {result['confidence']:.2f}\n")
    except Exception as e:
        pass
    
    print("-"*70)
    print("\nTest complete!\n")


if __name__ == '__main__':
    # Test availability
    available, unavailable = test_ocr_availability()
    
    # Test on image if available
    if available:
        test_ocr_on_image()
    
    print("\nFor more information on installing advanced OCR methods,")
    print("see ADVANCED_OCR_INSTALL.md\n")
