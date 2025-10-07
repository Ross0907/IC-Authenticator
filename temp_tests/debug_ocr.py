import cv2
import easyocr
import numpy as np
from pathlib import Path

def test_image(img_path):
    print(f"\n{'='*70}")
    print(f"Testing: {img_path.name}")
    print('='*70)
    
    img = cv2.imread(str(img_path))
    if img is None:
        print("Failed to load")
        return
    
    print(f"Image shape: {img.shape}")
    
    # Initialize EasyOCR
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    
    # Test 1: Original image
    print("\n1. ORIGINAL IMAGE:")
    results = reader.readtext(img, detail=1)
    for r in results:
        print(f"   '{r[1]}' (conf: {r[2]:.3f})")
    
    # Test 2: Grayscale
    print("\n2. GRAYSCALE:")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    results = reader.readtext(gray, detail=1)
    for r in results:
        print(f"   '{r[1]}' (conf: {r[2]:.3f})")
    
    # Test 3: Binary threshold
    print("\n3. BINARY THRESHOLD:")
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results = reader.readtext(binary, detail=1)
    for r in results:
        print(f"   '{r[1]}' (conf: {r[2]:.3f})")
    
    # Test 4: Adaptive threshold
    print("\n4. ADAPTIVE THRESHOLD:")
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    results = reader.readtext(adaptive, detail=1)
    for r in results:
        print(f"   '{r[1]}' (conf: {r[2]:.3f})")
    
    # Test 5: Enhanced contrast
    print("\n5. ENHANCED CONTRAST (CLAHE):")
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    results = reader.readtext(enhanced, detail=1)
    for r in results:
        print(f"   '{r[1]}' (conf: {r[2]:.3f})")
    
    # Test 6: Upscaled image
    print("\n6. UPSCALED 2x:")
    upscaled = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    results = reader.readtext(upscaled, detail=1)
    for r in results:
        print(f"   '{r[1]}' (conf: {r[2]:.3f})")
    
    # Test 7: Denoised
    print("\n7. DENOISED:")
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    results = reader.readtext(denoised, detail=1)
    for r in results:
        print(f"   '{r[1]}' (conf: {r[2]:.3f})")

# Test all images
test_dir = Path('test_images')
images = sorted(list(test_dir.glob('*.jpg')) + list(test_dir.glob('*.png')))

for img_path in images[:3]:  # Test first 3
    test_image(img_path)
