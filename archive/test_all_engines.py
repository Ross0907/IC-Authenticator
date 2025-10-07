"""Test ALL OCR engines and ALL preprocessing variants to find best combination"""

import cv2
import numpy as np
import easyocr
import sys

# Test specifically on type2.jpg
img_path = "test_images/type2.jpg"
image = cv2.imread(img_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
color = image.copy()

print("=" * 80)
print("COMPREHENSIVE OCR ENGINE TEST")
print(f"Image: {img_path}")
print("Target: ATMEGA328P (looking for '328P', not '3282')")
print("=" * 80)

# Initialize OCR engines
print("\nInitializing OCR engines...")
easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
print("[OK] EasyOCR ready")

try:
    from paddleocr import PaddleOCR
    paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    print("[OK] PaddleOCR ready")
    has_paddle = True
except:
    has_paddle = False
    print("[SKIP] PaddleOCR not available")

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    from PIL import Image as PILImage
    processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
    model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
    print("[OK] TrOCR ready")
    has_trocr = True
except:
    has_trocr = False
    print("[SKIP] TrOCR not available")

# Generate preprocessing variants
print("\n" + "=" * 80)
print("GENERATING PREPROCESSING VARIANTS")
print("=" * 80)

variants = []

# Variant 1: Original color
variants.append(("Original Color", color))

# Variant 2: Upscaled 3x color
upscaled_color_3x = cv2.resize(color, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
variants.append(("Upscaled 3x Color", upscaled_color_3x))

# Variant 3: Moderate CLAHE
clahe_moderate = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
moderate_enhanced = clahe_moderate.apply(gray)
variants.append(("Moderate CLAHE", moderate_enhanced))

# Variant 4: Upscaled 4x + Moderate CLAHE
upscaled_4x = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
upscaled_enhanced = clahe_moderate.apply(upscaled_4x)
variants.append(("4x Upscale + Moderate CLAHE", upscaled_enhanced))

# Variant 5: Bilateral + CLAHE
bilateral = cv2.bilateralFilter(upscaled_4x, 9, 75, 75)
bilateral_enhanced = clahe_moderate.apply(bilateral)
variants.append(("Bilateral + CLAHE", bilateral_enhanced))

# Variant 6: Strong CLAHE (for difficult text)
clahe_strong = cv2.createCLAHE(clipLimit=6.0, tileGridSize=(4, 4))
strong_enhanced = clahe_strong.apply(upscaled_4x)
variants.append(("4x + Strong CLAHE", strong_enhanced))

# Variant 7: EXTREME CLAHE (known to capture 328P)
clahe_extreme = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(2, 2))
extreme_enhanced = clahe_extreme.apply(gray)
variants.append(("Extreme CLAHE", extreme_enhanced))

# Variant 8: Extreme CLAHE + 4x upscale
extreme_upscaled = clahe_extreme.apply(upscaled_4x)
variants.append(("4x + Extreme CLAHE", extreme_upscaled))

print(f"[OK] Generated {len(variants)} preprocessing variants\n")

# Test each combination
results = []

for variant_name, variant_img in variants:
    print("=" * 80)
    print(f"VARIANT: {variant_name}")
    print("=" * 80)
    
    # Ensure image is in correct format for each engine
    if len(variant_img.shape) == 2:
        variant_color = cv2.cvtColor(variant_img, cv2.COLOR_GRAY2BGR)
        variant_gray = variant_img
    else:
        variant_color = variant_img
        variant_gray = cv2.cvtColor(variant_img, cv2.COLOR_BGR2GRAY)
    
    # EasyOCR
    try:
        easy_results = easyocr_reader.readtext(variant_color, detail=1)
        if easy_results:
            easy_texts = [text for (bbox, text, conf) in easy_results if conf > 0.1]
            easy_combined = ' '.join(easy_texts)
            print(f"  EasyOCR: {easy_combined}")
            
            if "328P" in easy_combined.upper():
                print(f"    [CORRECT!] Has '328P'")
                results.append((variant_name, "EasyOCR", easy_combined, True))
            elif "3282" in easy_combined.upper():
                print(f"    [WRONG] Has '3282'")
                results.append((variant_name, "EasyOCR", easy_combined, False))
            else:
                print(f"    [DIFF] Different")
                results.append((variant_name, "EasyOCR", easy_combined, False))
        else:
            print("  EasyOCR: No text detected")
    except Exception as e:
        print(f"  EasyOCR: Error - {e}")
    
    # PaddleOCR
    if has_paddle:
        try:
            paddle_result = paddle_ocr.ocr(variant_color, cls=True)
            if paddle_result and paddle_result[0]:
                paddle_texts = [line[1][0] for line in paddle_result[0]]
                paddle_combined = ' '.join(paddle_texts)
                print(f"  PaddleOCR: {paddle_combined}")
                
                if "328P" in paddle_combined.upper():
                    print(f"    [CORRECT!] Has '328P'")
                    results.append((variant_name, "PaddleOCR", paddle_combined, True))
                elif "3282" in paddle_combined.upper():
                    print(f"    [WRONG] Has '3282'")
                    results.append((variant_name, "PaddleOCR", paddle_combined, False))
                else:
                    print(f"    [DIFF] Different")
                    results.append((variant_name, "PaddleOCR", paddle_combined, False))
            else:
                print("  PaddleOCR: No text detected")
        except Exception as e:
            print(f"  PaddleOCR: Error - {e}")
    
    print()

# Summary
print("\n" + "=" * 80)
print("SUMMARY: Combinations that captured '328P' correctly")
print("=" * 80)

correct_results = [r for r in results if r[3]]
if correct_results:
    for variant_name, engine, text, _ in correct_results:
        print(f"[OK] {variant_name} + {engine}: {text}")
else:
    print("[FAIL] No combination captured '328P' correctly")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)

if correct_results:
    best = correct_results[0]
    print(f"Use: {best[0]} with {best[1]}")
    print(f"Result: {best[2]}")
else:
    print("Need to try additional preprocessing methods or OCR engines")
