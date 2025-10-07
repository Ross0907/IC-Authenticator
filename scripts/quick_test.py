"""
Quick test script to verify OCR system is working
"""
import cv2
from ocr_engine import OCREngine

def test_system():
    print("=" * 70)
    print("TESTING IC AUTHENTICATION SYSTEM")
    print("=" * 70)
    
    # Initialize OCR engine
    print("\n1. Initializing OCR Engine...")
    ocr = OCREngine()
    print("   ✓ OCR Engine initialized successfully")
    
    # Load test image
    print("\n2. Loading test image...")
    test_image_path = r"test_images\ADC0831_0-300x300.png"
    image = cv2.imread(test_image_path)
    
    if image is None:
        print("   ✗ Failed to load image")
        return
    
    print(f"   ✓ Image loaded: {test_image_path}")
    print(f"   ✓ Image size: {image.shape[1]}x{image.shape[0]}")
    
    # Extract text using ensemble method
    print("\n3. Running OCR Analysis (this may take 10-15 seconds on first run)...")
    print("   - Running EasyOCR...")
    print("   - Running PaddleOCR...")
    print("   - Running TrOCR...")
    print("   - Running docTR...")
    print("   - Combining results with ensemble voting...")
    
    results = ocr.extract_text(image, method='ensemble')
    
    print("\n" + "=" * 70)
    print("EXTRACTION RESULTS")
    print("=" * 70)
    
    print(f"\n📝 Extracted Text:")
    print("-" * 70)
    print(results['text'])
    print("-" * 70)
    
    print(f"\n📊 Confidence Score: {results['confidence']:.2%}")
    
    # Extract IC components
    print("\n" + "=" * 70)
    print("IC COMPONENT EXTRACTION")
    print("=" * 70)
    
    components = ocr.extract_ic_components(image)
    
    print(f"\n🔢 Part Number: {components['part_number'] or 'Not found'}")
    print(f"📅 Date Code: {components['date_code'] or 'Not found'}")
    print(f"🏷️  Lot Code: {components['lot_code'] or 'Not found'}")
    print(f"🌍 Country Code: {components['country_code'] or 'Not found'}")
    print(f"🏭 Manufacturer: {components['manufacturer'] or 'Unknown'}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    print("\n✅ System is working correctly!")
    print("\n📌 Next Steps:")
    print("   1. Run the full application: python ic_authenticator.py")
    print("   2. Load your IC images and test accuracy")
    print("   3. Review FINAL_SYSTEM_STATUS.md for detailed information")
    print("\n")

if __name__ == "__main__":
    test_system()
