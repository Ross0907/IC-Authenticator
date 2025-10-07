"""Test OCR on the debug preprocessed images"""

import cv2
import easyocr

# Initialize EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

debug_images = [
    "debug_extreme_upscale_sharp.png",
    "debug_adaptive_thresh.png", 
    "debug_extreme_clahe.png",
    "debug_morph_gradient.png",
    "debug_combined.png"
]

print("=" * 80)
print("TESTING OCR ON DEBUG IMAGES")
print("Looking for: ATMEGA328P (currently reads as: ATMEGA3282)")
print("=" * 80)

for img_path in debug_images:
    print(f"\n{'=' * 80}")
    print(f"IMAGE: {img_path}")
    print("=" * 80)
    
    img = cv2.imread(img_path)
    if img is None:
        print("❌ Failed to load")
        continue
    
    # Run EasyOCR
    results = reader.readtext(img, detail=1)
    
    if results:
        # Combine all text
        texts = [text for (bbox, text, conf) in results if conf > 0.1]
        combined = ' '.join(texts)
        avg_conf = sum(conf for (_, _, conf) in results) / len(results)
        
        print(f"📝 OCR Result: {combined}")
        print(f"   Confidence: {avg_conf:.2f}")
        
        # Check for correct reading
        if "328P" in combined.upper():
            print("   ✅✅✅ CORRECT! Contains '328P' - THIS PREPROCESSING WORKS!")
        elif "3282" in combined.upper():
            print("   ❌ Still wrong: Contains '3282' instead of '328P'")
        elif "328" in combined.upper():
            print("   ⚠️ Partial: Has '328' but missing 'P' or wrong ending")
        else:
            print(f"   ⚠️ Different reading")
    else:
        print("❌ No text detected")

print("\n" + "=" * 80)
print("TEST COMPLETE - Identify which preprocessing method captured 'P' correctly")
print("=" * 80)
