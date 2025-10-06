"""
Dynamic YOLO-OCR Test Script
Tests the new system with IC images of any resolution and type

This script demonstrates:
1. Dynamic text detection using YOLO + fallback methods
2. Multi-scale preprocessing adaptation  
3. Multi-engine OCR recognition
4. Quality-based result selection
5. Pattern extraction for IC markings
"""

import cv2
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List
import sys

# Import our dynamic YOLO-OCR system
from dynamic_yolo_ocr import DynamicYOLOOCR
from ic_marking_extractor import ICMarkingExtractor

class YOLOICAuthenticator:
    """
    IC Authentication system using Dynamic YOLO-OCR
    Combines YOLO detection with pattern extraction
    """
    
    def __init__(self):
        self.yolo_ocr = DynamicYOLOOCR()
        self.pattern_extractor = ICMarkingExtractor()
        
        print("🔍 YOLO-IC Authentication System Ready")
        print("✓ YOLO text detection enabled")
        print("✓ Multi-engine OCR enabled") 
        print("✓ Dynamic preprocessing enabled")
        print("✓ Pattern extraction enabled")
    
    def authenticate_ic(self, image_path: str, method: str = 'adaptive') -> Dict:
        """
        Authenticate IC image with dynamic YOLO-OCR approach
        
        Args:
            image_path: Path to IC image
            method: 'adaptive', 'laser', 'printed', 'embossed', 'all'
        
        Returns:
            Comprehensive authentication results
        """
        print(f"\n🔍 Authenticating IC: {os.path.basename(image_path)}")
        print(f"📋 Preprocessing method: {method}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {'error': f'Could not load image: {image_path}'}
        
        print(f"📐 Image dimensions: {image.shape}")
        
        # Step 1: YOLO-OCR text extraction
        print("\n🎯 Step 1: YOLO Text Detection & OCR")
        yolo_results = self.yolo_ocr.extract_text_from_ic(image, preprocessing_method=method)
        
        # Display detection results
        num_regions = yolo_results['metadata']['num_regions']
        print(f"✓ Detected {num_regions} text regions")
        
        for i, (region_key, region_data) in enumerate(yolo_results['ocr_results'].items()):
            bbox = region_data['bbox']
            detection_conf = region_data['detection_confidence']
            best_text = region_data['best_text']
            print(f"  Region {i+1}: bbox{bbox}, conf={detection_conf:.3f}, text='{best_text}'")
        
        extracted_text = yolo_results['final_text']
        overall_confidence = yolo_results['confidence']
        
        print(f"\n📝 Raw extracted text:")
        print(f"'{extracted_text}'")
        print(f"🎯 Overall confidence: {overall_confidence:.3f}")
        
        # Step 2: Pattern extraction and IC identification
        print(f"\n🔍 Step 2: IC Pattern Analysis")
        
        if extracted_text:
            pattern_results = self.pattern_extractor.extract_ic_patterns(extracted_text)
        else:
            pattern_results = {
                'manufacturer': 'Unknown',
                'part_number': 'Unknown', 
                'date_code': 'Unknown',
                'confidence': 0.0,
                'raw_text': extracted_text
            }
        
        # Step 3: Combine results
        final_results = {
            'image_path': image_path,
            'timestamp': datetime.now().isoformat(),
            'yolo_detection': {
                'num_regions': num_regions,
                'detection_confidence': overall_confidence,
                'raw_text': extracted_text,
                'regions': yolo_results['ocr_results']
            },
            'ic_identification': pattern_results,
            'authentication': {
                'success': pattern_results['confidence'] > 0.5,
                'manufacturer': pattern_results['manufacturer'],
                'part_number': pattern_results['part_number'],
                'date_code': pattern_results['date_code'],
                'overall_confidence': (overall_confidence + pattern_results['confidence']) / 2
            },
            'metadata': {
                'image_size': image.shape,
                'preprocessing_method': method,
                'yolo_enabled': True
            }
        }
        
        return final_results
    
    def test_multiple_methods(self, image_path: str) -> Dict:
        """Test image with multiple preprocessing methods"""
        print(f"\n🧪 Testing multiple methods on: {os.path.basename(image_path)}")
        
        methods = ['adaptive', 'laser', 'printed', 'embossed']
        results = {}
        
        for method in methods:
            print(f"\n--- Testing method: {method} ---")
            result = self.authenticate_ic(image_path, method)
            results[method] = result
            
            if 'authentication' in result:
                success = result['authentication']['success']
                confidence = result['authentication']['overall_confidence']
                print(f"✓ Method {method}: Success={success}, Confidence={confidence:.3f}")
        
        # Find best method
        best_method = 'adaptive'
        best_confidence = 0.0
        
        for method, result in results.items():
            if 'authentication' in result:
                conf = result['authentication']['overall_confidence']
                if conf > best_confidence:
                    best_confidence = conf
                    best_method = method
        
        print(f"\n🏆 Best method: {best_method} (confidence: {best_confidence:.3f})")
        
        return {
            'best_method': best_method,
            'best_confidence': best_confidence,
            'all_results': results
        }


def test_dynamic_system():
    """Test the dynamic YOLO-OCR system"""
    print("🚀 Testing Dynamic YOLO-OCR IC Authentication System")
    print("=" * 60)
    
    # Initialize system
    authenticator = YOLOICAuthenticator()
    
    # Test images
    test_images = []
    test_dir = "test_images"
    
    if os.path.exists(test_dir):
        for file in os.listdir(test_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                test_images.append(os.path.join(test_dir, file))
    
    if not test_images:
        print("❌ No test images found in test_images/ directory")
        return
    
    print(f"📁 Found {len(test_images)} test images")
    
    all_results = {}
    
    for image_path in test_images:
        print(f"\n{'='*60}")
        print(f"🖼️  TESTING: {os.path.basename(image_path)}")
        print(f"{'='*60}")
        
        try:
            # Test with adaptive method first
            result = authenticator.authenticate_ic(image_path, 'adaptive')
            
            # Print results
            if 'authentication' in result:
                auth = result['authentication']
                print(f"\n📊 AUTHENTICATION RESULTS:")
                print(f"✓ Success: {auth['success']}")
                print(f"🏭 Manufacturer: {auth['manufacturer']}")
                print(f"🔧 Part Number: {auth['part_number']}")
                print(f"📅 Date Code: {auth['date_code']}")
                print(f"🎯 Confidence: {auth['overall_confidence']:.3f}")
                
                # Test multiple methods if first attempt has low confidence
                if auth['overall_confidence'] < 0.7:
                    print(f"\n🔄 Low confidence, testing multiple methods...")
                    multi_result = authenticator.test_multiple_methods(image_path)
                    result['multi_method_test'] = multi_result
                
            else:
                print(f"❌ Authentication failed: {result.get('error', 'Unknown error')}")
            
            all_results[image_path] = result
            
        except Exception as e:
            print(f"❌ Error processing {image_path}: {str(e)}")
            all_results[image_path] = {'error': str(e)}
    
    # Summary
    print(f"\n{'='*60}")
    print("📈 SUMMARY RESULTS")
    print(f"{'='*60}")
    
    successful = 0
    total_confidence = 0.0
    
    for image_path, result in all_results.items():
        filename = os.path.basename(image_path)
        
        if 'authentication' in result:
            auth = result['authentication']
            success = auth['success']
            confidence = auth['overall_confidence']
            
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{filename:30} | {status} | Confidence: {confidence:.3f}")
            
            if success:
                successful += 1
                total_confidence += confidence
        else:
            print(f"{filename:30} | ❌ ERROR | {result.get('error', 'Unknown')}")
    
    # Overall statistics
    total_images = len(test_images)
    success_rate = (successful / total_images) * 100 if total_images > 0 else 0
    avg_confidence = total_confidence / successful if successful > 0 else 0
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"✓ Success Rate: {successful}/{total_images} ({success_rate:.1f}%)")
    print(f"🎯 Average Confidence: {avg_confidence:.3f}")
    
    # Save detailed results
    results_file = f"yolo_ocr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Convert numpy arrays to lists for JSON serialization
    def convert_for_json(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_json(item) for item in obj]
        else:
            return obj
    
    json_results = convert_for_json(all_results)
    
    try:
        with open(results_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        print(f"💾 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")
    
    return all_results


def test_specific_image(image_path: str):
    """Test specific image with detailed output"""
    print(f"🔍 Testing specific image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    authenticator = YOLOICAuthenticator()
    
    # Test with all methods
    print("\n🧪 Testing all preprocessing methods...")
    result = authenticator.test_multiple_methods(image_path)
    
    # Display best result
    best_method = result['best_method']
    best_result = result['all_results'][best_method]
    
    print(f"\n🏆 BEST RESULT (Method: {best_method}):")
    if 'authentication' in best_result:
        auth = best_result['authentication']
        print(f"🏭 Manufacturer: {auth['manufacturer']}")
        print(f"🔧 Part Number: {auth['part_number']}")
        print(f"📅 Date Code: {auth['date_code']}")
        print(f"🎯 Confidence: {auth['overall_confidence']:.3f}")
        print(f"✓ Success: {auth['success']}")


if __name__ == "__main__":
    print("🤖 Dynamic YOLO-OCR IC Authentication System")
    print("⚡ Supports any IC type and resolution")
    print("🎯 Uses YOLO detection + Multi-engine OCR")
    
    if len(sys.argv) > 1:
        # Test specific image
        image_path = sys.argv[1]
        test_specific_image(image_path)
    else:
        # Test all images in test_images directory
        test_dynamic_system()