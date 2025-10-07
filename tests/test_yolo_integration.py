#!/usr/bin/env python3
"""
Test script to verify YOLO-OCR integration is working properly
This script tests the new OCR engine to ensure it produces accurate results
instead of garbled text.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ocr_engine import OCREngine

def test_yolo_ocr():
    """Test the YOLO-OCR integration with sample images"""
    print("Testing YOLO-OCR Integration...")
    print("=" * 50)
    
    # Initialize OCR engine
    ocr_engine = OCREngine()
    
    # Test images
    test_images = [
        "test_images/ADC0831_0-300x300.png",
        "test_images/Screenshot 2025-10-06 222749.png", 
        "test_images/Screenshot 2025-10-06 222803.png"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\nTesting: {image_path}")
            print("-" * 30)
            
            try:
                # Test YOLO-OCR method
                result = ocr_engine.extract_text_from_file(image_path, method='yolo')
                
                print(f"Method: YOLO-OCR")
                print(f"Text: {result.get('text', 'No text found')}")
                print(f"Confidence: {result.get('confidence', 0):.2f}")
                print(f"Regions detected: {result.get('regions_detected', 0)}")
                
                # Test with fallback methods for comparison
                fallback_result = ocr_engine.extract_text_from_file(image_path, method='easyocr')
                print(f"\nFallback (EasyOCR): {fallback_result.get('text', 'No text found')}")
                
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
        else:
            print(f"Image not found: {image_path}")
    
    print("\n" + "=" * 50)
    print("YOLO-OCR Integration Test Complete!")

if __name__ == "__main__":
    test_yolo_ocr()