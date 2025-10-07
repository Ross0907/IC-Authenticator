"""Final verification test - Confirm type2.jpg captures 328P correctly and is FAST"""

import time
from dynamic_yolo_ocr import DynamicYOLOOCR
import cv2

print("=" * 80)
print("FINAL VERIFICATION TEST")
print("=" * 80)

# Initialize
start_init = time.time()
ocr_system = DynamicYOLOOCR()
init_time = time.time() - start_init
print(f"✅ System initialized in {init_time:.1f}s\n")

# Test on type2.jpg
img_path = "test_images/type2.jpg"
image = cv2.imread(img_path)

print(f"Testing: {img_path}")
print("Expected: ATMEGA328P (with 'P' at the end, not '2')")
print("-" * 80)

start = time.time()
result = ocr_system.extract_text_from_ic(image)
elapsed = time.time() - start

final_text = result.get('final_text', '')
confidence = result.get('confidence', 0)

print(f"\n📝 OCR Result: {final_text}")
print(f"⏱️  Processing Time: {elapsed:.2f} seconds")
print(f"🎯 Confidence: {confidence:.2%}")

# Check if it contains "328P"
if "328P" in final_text.upper():
    print("\n✅✅✅ SUCCESS! OCR correctly captured '328P'")
    print("     No fuzzy matching needed - preprocessing works!")
else:
    print(f"\n❌ FAILED: Does not contain '328P'")
    print(f"   Got: {final_text}")

# Speed check
if elapsed < 5.0:
    print(f"✅ FAST: Completed in {elapsed:.2f}s (target: <5s)")
else:
    print(f"⚠️  SLOW: Took {elapsed:.2f}s (target: <5s)")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
