"""
Test Script for IC Authentication System
Verifies that all components are working correctly
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    errors = []
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError as e:
        errors.append(f"✗ OpenCV import failed: {e}")
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except ImportError as e:
        errors.append(f"✗ NumPy import failed: {e}")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5 imported successfully")
    except ImportError as e:
        errors.append(f"✗ PyQt5 import failed: {e}")
    
    try:
        import easyocr
        print("✓ EasyOCR imported successfully")
    except ImportError as e:
        errors.append(f"⚠ EasyOCR import failed: {e} (optional)")
    
    try:
        import pytesseract
        print("✓ Tesseract imported successfully")
    except ImportError as e:
        errors.append(f"⚠ Tesseract import failed: {e} (optional)")
    
    try:
        from paddleocr import PaddleOCR
        print("✓ PaddleOCR imported successfully")
    except ImportError as e:
        errors.append(f"⚠ PaddleOCR import failed: {e} (optional)")
    
    try:
        import requests
        print("✓ Requests imported successfully")
    except ImportError as e:
        errors.append(f"✗ Requests import failed: {e}")
    
    try:
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup imported successfully")
    except ImportError as e:
        errors.append(f"✗ BeautifulSoup import failed: {e}")
    
    return errors

def test_modules():
    """Test if custom modules can be imported"""
    print("\nTesting custom modules...")
    errors = []
    
    try:
        from image_processor import ImageProcessor
        print("✓ ImageProcessor module loaded")
    except ImportError as e:
        errors.append(f"✗ ImageProcessor import failed: {e}")
    
    try:
        from ocr_engine import OCREngine
        print("✓ OCREngine module loaded")
    except ImportError as e:
        errors.append(f"✗ OCREngine import failed: {e}")
    
    try:
        from web_scraper import DatasheetScraper
        print("✓ DatasheetScraper module loaded")
    except ImportError as e:
        errors.append(f"✗ DatasheetScraper import failed: {e}")
    
    try:
        from verification_engine import VerificationEngine
        print("✓ VerificationEngine module loaded")
    except ImportError as e:
        errors.append(f"✗ VerificationEngine import failed: {e}")
    
    try:
        from database_manager import DatabaseManager
        print("✓ DatabaseManager module loaded")
    except ImportError as e:
        errors.append(f"✗ DatabaseManager import failed: {e}")
    
    return errors

def test_image_processing():
    """Test basic image processing"""
    print("\nTesting image processing...")
    try:
        import cv2
        import numpy as np
        from image_processor import ImageProcessor
        
        # Create a dummy image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[25:75, 25:75] = [255, 255, 255]
        
        processor = ImageProcessor()
        results = processor.process_image(test_image)
        
        if 'enhanced' in results:
            print("✓ Image processing working")
            return []
        else:
            return ["✗ Image processing failed to produce expected output"]
            
    except Exception as e:
        return [f"✗ Image processing test failed: {e}"]

def test_database():
    """Test database functionality"""
    print("\nTesting database...")
    try:
        from database_manager import DatabaseManager
        
        db = DatabaseManager('test_db.db')
        
        # Test saving
        test_result = {
            'timestamp': '2025-01-01T00:00:00',
            'image_path': 'test.jpg',
            'extracted_markings': {'part_number': 'TEST123'},
            'official_markings': {},
            'is_authentic': True,
            'confidence_score': 85.5,
            'verification': {},
            'recommendation': 'Test recommendation'
        }
        
        db.save_analysis(test_result)
        print("✓ Database write working")
        
        # Test reading
        history = db.get_history(limit=1)
        if history:
            print("✓ Database read working")
        
        # Clean up
        if os.path.exists('test_db.db'):
            os.remove('test_db.db')
        
        return []
        
    except Exception as e:
        return [f"✗ Database test failed: {e}"]

def test_test_images():
    """Check if test images are available"""
    print("\nChecking test images...")
    errors = []
    
    if not os.path.exists('test_images'):
        errors.append("✗ test_images folder not found")
    else:
        images = [f for f in os.listdir('test_images') 
                  if f.endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            print(f"✓ Found {len(images)} test image(s)")
            for img in images:
                print(f"  - {img}")
        else:
            errors.append("✗ No test images found in test_images folder")
    
    return errors

def main():
    """Run all tests"""
    print("=" * 60)
    print("IC Authentication System - System Test")
    print("=" * 60)
    print()
    
    all_errors = []
    
    # Run tests
    all_errors.extend(test_imports())
    all_errors.extend(test_modules())
    all_errors.extend(test_image_processing())
    all_errors.extend(test_database())
    all_errors.extend(test_test_images())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if not all_errors:
        print("✓ All tests passed!")
        print("\nThe system is ready to use.")
        print("Run 'python ic_authenticator.py' to start the application.")
    else:
        print(f"Found {len(all_errors)} issue(s):")
        for error in all_errors:
            print(f"  {error}")
        
        # Check if critical errors exist
        critical_errors = [e for e in all_errors if e.startswith('✗')]
        if critical_errors:
            print("\n⚠ Critical errors found. Please fix before running.")
            print("Run: pip install -r requirements.txt")
        else:
            print("\n⚠ Only optional components missing.")
            print("The system should still work with reduced functionality.")
    
    print()

if __name__ == '__main__':
    main()
