"""Test complete system with improved OCR and fuzzy matching"""

from dynamic_yolo_ocr import DynamicYOLOOCR
from verification_engine import VerificationEngine
import os
import cv2

# Initialize
ocr_system = DynamicYOLOOCR()
ve = VerificationEngine()

test_images = [
    "test_images/type2.jpg",  # The problem case
    "test_images/ADC0831_0-300x300.png",
    "test_images/sn74hc595n-shift-register-cmos-logic-ic-integrated-circuit-3.jpg"
]

print("=" * 80)
print("TESTING FULL SYSTEM: OCR + FUZZY MATCHING + VERIFICATION")
print("=" * 80)

for img_path in test_images:
    if not os.path.exists(img_path):
        print(f"\n❌ File not found: {img_path}")
        continue
    
    print(f"\n{'=' * 80}")
    print(f"IMAGE: {os.path.basename(img_path)}")
    print("=" * 80)
    
    # Load image
    image = cv2.imread(img_path)
    if image is None:
        print(f"❌ Failed to load image")
        continue
    
    # Extract text with improved OCR
    result = ocr_system.extract_text_from_ic(image)
    
    if result and result.get('final_text'):
        raw_text = result.get('final_text', '')
        conf = result.get('confidence', 0)
        
        print(f"📝 OCR Extracted: {raw_text}")
        print(f"   Confidence: {conf:.2f}")
        
        # Prepare data for verification
        test_data = {
            'raw_text': raw_text,
            'part_number': '',  # Will be filled by verification
            'date_code': '0723'  # Placeholder
        }
        
        # Run verification with fuzzy matching
        print("\n🔍 Verifying with fuzzy matching...")
        verify_result = ve.verify_component(test_data, {}, {})
        
        print(f"\n✅ RESULT:")
        print(f"   Is Authentic: {verify_result.get('is_authentic', False)}")
        print(f"   Confidence: {verify_result.get('confidence', 0):.1f}%")
        print(f"   Matched Part: {test_data.get('part_number', 'None')}")
        
        if verify_result.get('checks_passed'):
            print(f"   Passed: {len(verify_result['checks_passed'])} checks")
        if verify_result.get('checks_failed'):
            print(f"   Failed: {len(verify_result['checks_failed'])} checks")
    else:
        print(f"❌ OCR Failed: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
