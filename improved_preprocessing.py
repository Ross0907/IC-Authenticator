"""
Improved Preprocessing Module
High-quality upscaling variants optimized for sharp text extraction
"""

import cv2
import numpy as np
from typing import List

def generate_high_quality_variants(image: np.ndarray) -> List[np.ndarray]:
    """Generate HIGH-QUALITY preprocessing variants optimized for sharp text extraction"""
    variants = []
    
    try:
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            color = image.copy()
        else:
            gray = image.copy()
            color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # Variant 1: High upscaling (6x) for ultra-sharp text - BEST FOR SMALL TEXT
        upscaled_6x_color = cv2.resize(color, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
        variants.append(("6x_upscale_color", upscaled_6x_color))
        
        # Variant 2: Ultra upscaling (8x) for extremely small text
        upscaled_8x_color = cv2.resize(color, None, fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
        variants.append(("8x_upscale_color", upscaled_8x_color))
        
        # Variant 3: Upscaled 5x - balance between quality and speed
        upscaled_5x_color = cv2.resize(color, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
        variants.append(("5x_upscale_color", upscaled_5x_color))
        
        # Variant 4: Upscaled 4x + sharpening
        upscaled_4x = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        kernel_sharpen = np.array([[-1,-1,-1],
                                    [-1, 9,-1],
                                    [-1,-1,-1]])
        sharpened_4x = cv2.filter2D(upscaled_4x, -1, kernel_sharpen)
        variants.append(("4x_upscale_sharpened", sharpened_4x))
        
        # Variant 5: Upscaled 3x color (proven winner for type2.jpg)
        upscaled_color_3x = cv2.resize(color, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        variants.append(("3x_upscale_color", upscaled_color_3x))
        
        # Variant 6: Upscaled 6x + Moderate CLAHE for contrast enhancement
        upscaled_6x_gray = cv2.resize(gray, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
        clahe_moderate = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced_6x = clahe_moderate.apply(upscaled_6x_gray)
        variants.append(("6x_upscale_clahe", enhanced_6x))
        
        # Variant 7: Upscaled 5x + Denoising for noisy images
        upscaled_5x_gray = cv2.resize(gray, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
        denoised_5x = cv2.fastNlMeansDenoising(upscaled_5x_gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        variants.append(("5x_upscale_denoised", denoised_5x))
        
    except Exception as e:
        print(f"Preprocessing error: {e}")
        # Fallback - return original
        variants = [("original", image)]
    
    return variants


def test_preprocessing_on_images():
    """Test new preprocessing on all test images"""
    import os
    import easyocr
    
    test_images = [
        "test_images/ADC0831_0-300x300.png",
        "test_images/Screenshot 2025-10-06 222749.png", 
        "test_images/Screenshot 2025-10-06 222803.png",
        "test_images/sn74hc595n-shift-register-cmos-logic-ic-integrated-circuit-3.jpg",
        "test_images/type1.jpg",
        "test_images/type2.jpg"
    ]
    
    reader = easyocr.Reader(['en'], gpu=True)
    
    results = {}
    
    for img_path in test_images:
        if not os.path.exists(img_path):
            print(f"Skipping {img_path} - file not found")
            continue
            
        print(f"\n{'='*100}")
        print(f"Testing: {os.path.basename(img_path)}")
        print('='*100)
        
        image = cv2.imread(img_path)
        variants = generate_high_quality_variants(image)
        
        best_text = ""
        best_conf = 0
        best_variant = ""
        
        for variant_name, variant_img in variants:
            try:
                result = reader.readtext(variant_img, detail=1)
                if result:
                    full_text = ' '.join([text for (_, text, conf) in result])
                    avg_conf = sum([conf for (_, _, conf) in result]) / len(result) * 100
                    
                    print(f"\n{variant_name}: {full_text[:80]}")
                    print(f"  Confidence: {avg_conf:.1f}%")
                    
                    if avg_conf > best_conf:
                        best_conf = avg_conf
                        best_text = full_text
                        best_variant = variant_name
                        
            except Exception as e:
                print(f"\n{variant_name}: ERROR - {e}")
        
        print(f"\n>>> BEST: {best_variant} ({best_conf:.1f}%): {best_text}")
        results[os.path.basename(img_path)] = {
            'best_variant': best_variant,
            'confidence': best_conf,
            'text': best_text
        }
    
    print(f"\n\n{'='*100}")
    print("SUMMARY - BEST VARIANTS PER IMAGE")
    print('='*100)
    for img, data in results.items():
        print(f"\n{img}")
        print(f"  Best: {data['best_variant']} ({data['confidence']:.1f}%)")
        print(f"  Text: {data['text']}")
    
    return results


if __name__ == "__main__":
    test_preprocessing_on_images()
