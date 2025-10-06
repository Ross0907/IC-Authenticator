#!/usr/bin/env python3
"""
Comprehensive test of the fixed IC authentication system
Tests both YOLO-OCR improvements and authentication logic fixes
"""

import os
import sys
from ocr_engine import OCREngine
from verification_engine import VerificationEngine
from web_scraper import DatasheetScraper
import cv2
import numpy as np

def test_complete_system():
    """Test the complete IC authentication system with fixes"""
    print("Testing Complete IC Authentication System")
    print("=" * 60)
    
    # Initialize components
    ocr_engine = OCREngine()
    verifier = VerificationEngine()
    scraper = DatasheetScraper()
    
    # Test images from the UI
    test_images = [
        "test_images/ADC0831_0-300x300.png",
        "test_images/Screenshot 2025-10-06 222749.png", 
        "test_images/Screenshot 2025-10-06 222803.png"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\\nTesting: {image_path}")
            print("-" * 40)
            
            try:
                # Test both YOLO and ensemble methods
                for method in ['yolo', 'ensemble']:
                    print(f"\\n📊 Method: {method.upper()}")
                    
                    # Extract text
                    result = ocr_engine.extract_text_from_file(image_path, method=method)
                    
                    extracted_text = result.get('text', '')
                    confidence = result.get('confidence', 0)
                    
                    print(f"📝 Extracted: '{extracted_text}'")
                    print(f"🎯 OCR Confidence: {confidence:.2f}")
                    
                    if extracted_text:
                        # Parse the extracted text (simulate marking structure)
                        parsed_data = {
                            'manufacturer': 'Unknown',
                            'part_number': extracted_text.split()[0] if extracted_text.split() else None,
                            'date_code': None,
                            'lot_code': None,
                            'package_type': None,
                            'confidence': confidence,
                            'raw_text': extracted_text
                        }
                        
                        # Try to identify manufacturer from text
                        text_upper = extracted_text.upper()
                        if 'ATMEL' in text_upper or 'ATMEGA' in text_upper:
                            parsed_data['manufacturer'] = 'Atmel'
                            if 'ATMEGA328P' in text_upper or 'ATMEGA32' in text_upper:
                                parsed_data['part_number'] = 'ATMEGA328P' if '328' in text_upper else 'ATMEGA32'
                        elif 'CY8C' in text_upper or 'CYPRESS' in text_upper:
                            parsed_data['manufacturer'] = 'Cypress'
                            if 'CY8C29666' in text_upper:
                                parsed_data['part_number'] = 'CY8C29666'
                        
                        # Get official data (with fallback)
                        print(f"🔍 Looking up official data...")
                        official_data = scraper.search_component_datasheet(
                            parsed_data.get('part_number', ''),
                            parsed_data.get('manufacturer', '')
                        )
                        
                        # Verify component
                        verification_result = verifier.verify_component(
                            parsed_data,
                            official_data,
                            {}  # No datasheet info for this test
                        )
                        
                        # Display results
                        print(f"✅ Authentic: {verification_result.get('is_authentic', False)}")
                        print(f"📊 Confidence: {verification_result.get('confidence', 0):.1f}%")
                        print(f"🔍 Checks Passed: {len(verification_result.get('checks_passed', []))}")
                        print(f"❌ Checks Failed: {len(verification_result.get('checks_failed', []))}")
                        
                        if verification_result.get('anomalies'):
                            print(f"⚠️  Anomalies: {len(verification_result['anomalies'])}")
                            for anomaly in verification_result['anomalies'][:3]:  # Show first 3
                                print(f"   • {anomaly}")
                    
                    else:
                        print("❌ No text extracted")
                
            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
    
    print("\\n" + "=" * 60)
    print("🎯 System Test Complete!")
    print("\\nExpected improvements:")
    print("✅ PaddleOCR should initialize without 'show_log' error")
    print("✅ Network errors should fallback to local database")
    print("✅ Authentication should be less strict with missing data")
    print("✅ YOLO channel errors should be fixed")

if __name__ == "__main__":
    test_complete_system()