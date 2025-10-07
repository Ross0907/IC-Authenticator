"""Test individual preprocessing variants to see which captures 'P' best"""

import cv2
import numpy as np
from dynamic_yolo_ocr import DynamicYOLOOCR
import os

# Initialize
ocr_system = DynamicYOLOOCR()

# Test on type2.jpg (the problem image)
img_path = "test_images/type2.jpg"
image = cv2.imread(img_path)

print("=" * 80)
print("TESTING INDIVIDUAL PREPROCESSING VARIANTS")
print(f"Image: {img_path}")
print("Expected: ATMEGA328P (OCR often reads as: ATMEGA3282)")
print("=" * 80)

# Generate variants
variants = ocr_system._generate_variants(image)

print(f"\n✅ Generated {len(variants)} preprocessing variants")
print("\nTesting each variant with EasyOCR...\n")

for i, variant in enumerate(variants, 1):
    print(f"{'=' * 80}")
    print(f"VARIANT {i}/{len(variants)}")
    print("=" * 80)
    
    # Run OCR on this variant only
    try:
        # Ensure variant is in correct format
        if len(variant.shape) == 2:
            variant_color = cv2.cvtColor(variant, cv2.COLOR_GRAY2BGR)
        else:
            variant_color = variant
        
        # Run EasyOCR
        results = ocr_system.easyocr_reader.readtext(variant_color, detail=1)
        
        if results:
            # Combine all text
            texts = [text for (bbox, text, conf) in results if conf > 0.15]
            combined = ' '.join(texts)
            avg_conf = sum(conf for (_, _, conf) in results) / len(results)
            
            print(f"Text: {combined}")
            print(f"Confidence: {avg_conf:.2f}")
            
            # Check if it contains "328P" or "3282"
            if "328P" in combined.upper():
                print("✅ CORRECT! Contains '328P'")
            elif "3282" in combined.upper():
                print("❌ Wrong: Contains '3282' instead of '328P'")
            else:
                print(f"⚠️ Different result")
        else:
            print("No text detected")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
