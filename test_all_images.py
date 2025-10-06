"""
Comprehensive test for all IC images in test_images folder
Tests OCR extraction and verification improvements
"""
import cv2
import os
from ocr_engine import OCREngine
from verification_engine import VerificationEngine
from datetime import datetime

def test_all_images():
    print("=" * 80)
    print("COMPREHENSIVE IC AUTHENTICATION TEST")
    print("=" * 80)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize engines
    print("Initializing OCR and Verification engines...")
    ocr = OCREngine()
    verifier = VerificationEngine()
    print("✓ Engines ready\n")
    
    # Get all images from test_images folder
    test_images_dir = "test_images"
    image_files = [f for f in os.listdir(test_images_dir) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
    if not image_files:
        print("❌ No images found in test_images folder")
        return
    
    print(f"Found {len(image_files)} test images\n")
    
    results_summary = []
    
    for idx, image_file in enumerate(image_files, 1):
        print("=" * 80)
        print(f"TEST {idx}/{len(image_files)}: {image_file}")
        print("=" * 80)
        
        # Load image
        image_path = os.path.join(test_images_dir, image_file)
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"❌ Failed to load: {image_path}\n")
            continue
        
        print(f"✓ Loaded image: {image.shape[1]}x{image.shape[0]}")
        
        # Run OCR
        print("\n📝 Running OCR extraction...")
        # Wrap image in expected format (list of regions)
        marking_regions = [{'image': image}]
        ocr_result = ocr.extract_text(marking_regions, method='ensemble')
        
        print(f"   Confidence: {ocr_result['confidence']:.2%}")
        print(f"   Raw text: {repr(ocr_result['text'][:100])}")
        
        # Parse components
        parsed = ocr.parse_marking_structure(ocr_result)
        
        print("\n🔍 Extracted Components:")
        print(f"   Manufacturer:  {parsed['manufacturer'] or 'None'}")
        print(f"   Part Number:   {parsed['part_number'] or 'None'}")
        print(f"   Date Code:     {parsed['date_code'] or 'None'}")
        print(f"   Lot Code:      {parsed['lot_code'] or 'None'}")
        print(f"   Country:       {parsed['country_of_origin'] or 'None'}")
        
        # Store result
        result = {
            'file': image_file,
            'manufacturer': parsed['manufacturer'],
            'part_number': parsed['part_number'],
            'date_code': parsed['date_code'],
            'confidence': ocr_result['confidence'],
            'raw_text': ocr_result['text']
        }
        results_summary.append(result)
        
        print()
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY OF ALL TESTS")
    print("=" * 80)
    print()
    
    print(f"{'File':<40} {'Manufacturer':<15} {'Part Number':<20} {'Confidence':<10}")
    print("-" * 90)
    
    for result in results_summary:
        mfg = result['manufacturer'] or 'None'
        part = result['part_number'] or 'None'
        conf = f"{result['confidence']:.1%}"
        
        # Truncate if needed
        file_name = result['file'][:38]
        mfg = mfg[:13]
        part = part[:18]
        
        print(f"{file_name:<40} {mfg:<15} {part:<20} {conf:<10}")
    
    print()
    
    # Statistics
    total = len(results_summary)
    with_manufacturer = sum(1 for r in results_summary if r['manufacturer'])
    with_part = sum(1 for r in results_summary if r['part_number'])
    avg_confidence = sum(r['confidence'] for r in results_summary) / total if total > 0 else 0
    
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total Images:           {total}")
    print(f"Manufacturer Detected:  {with_manufacturer}/{total} ({with_manufacturer/total*100:.1f}%)")
    print(f"Part Number Extracted:  {with_part}/{total} ({with_part/total*100:.1f}%)")
    print(f"Average Confidence:     {avg_confidence:.1%}")
    print()
    
    if avg_confidence >= 0.8:
        print("🎉 EXCELLENT! Average confidence >= 80%")
    elif avg_confidence >= 0.6:
        print("👍 GOOD! Average confidence >= 60%")
    else:
        print("⚠️  Needs improvement. Average confidence < 60%")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_all_images()
