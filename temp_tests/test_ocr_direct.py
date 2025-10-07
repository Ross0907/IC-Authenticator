"""Quick test to see why OCR is returning empty strings"""
import cv2
import easyocr
import numpy as np
from pathlib import Path

# Test with a simple image
test_image_path = Path("test_images/type1.jpg")

if test_image_path.exists():
    print(f"Testing OCR on: {test_image_path}")
    image = cv2.imread(str(test_image_path))
    
    if image is not None:
        print(f"Image loaded: {image.shape}")
        
        # Test EasyOCR directly
        print("\n1. Testing EasyOCR directly...")
        try:
            reader = easyocr.Reader(['en'], verbose=False, gpu=False)
            results = reader.readtext(image)
            print(f"   EasyOCR found {len(results)} text regions")
            for result in results:
                bbox, text, conf = result
                print(f"   - '{text}' (confidence: {conf:.2f})")
        except Exception as e:
            print(f"   EasyOCR failed: {e}")
        
        # Test with grayscale
        print("\n2. Testing with grayscale preprocessing...")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        try:
            reader = easyocr.Reader(['en'], verbose=False, gpu=False)
            results = reader.readtext(gray)
            print(f"   EasyOCR found {len(results)} text regions")
            for result in results:
                bbox, text, conf = result
                print(f"   - '{text}' (confidence: {conf:.2f})")
        except Exception as e:
            print(f"   EasyOCR failed: {e}")
        
        # Test with enhanced contrast
        print("\n3. Testing with enhanced contrast...")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        try:
            reader = easyocr.Reader(['en'], verbose=False, gpu=False)
            results = reader.readtext(enhanced)
            print(f"   EasyOCR found {len(results)} text regions")
            for result in results:
                bbox, text, conf = result
                print(f"   - '{text}' (confidence: {conf:.2f})")
        except Exception as e:
            print(f"   EasyOCR failed: {e}")
    else:
        print("Failed to load image")
else:
    print(f"Test image not found: {test_image_path}")
    print("\nTrying first available image...")
    test_dir = Path("test_images")
    if test_dir.exists():
        images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
        if images:
            test_image_path = images[0]
            print(f"Using: {test_image_path}")
            image = cv2.imread(str(test_image_path))
            if image is not None:
                print(f"Image loaded: {image.shape}")
                reader = easyocr.Reader(['en'], verbose=False, gpu=False)
                results = reader.readtext(image)
                print(f"EasyOCR found {len(results)} text regions")
                for result in results:
                    bbox, text, conf = result
                    print(f"- '{text}' (confidence: {conf:.2f})")
