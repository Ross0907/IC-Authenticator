"""
Test script specifically for the Cypress IC image
Tests enhanced preprocessing and OCR extraction
"""
import cv2
import numpy as np
from ocr_engine import OCREngine
from enhanced_preprocessing import visualize_preprocessing_steps, create_multiple_variants

def test_cypress_ic():
    print("=" * 80)
    print("TESTING CYPRESS IC MARKING EXTRACTION")
    print("=" * 80)
    
    # Expected values
    expected = {
        'part_number': 'CY8C29666-24PVXI',
        'batch': 'B',
        'week': '05',
        'country': 'PHI',
        'year': '2007',
        'lot_code': 'CYP 606541'
    }
    
    print("\n📋 Expected Markings:")
    print(f"   Part Number: {expected['part_number']}")
    print(f"   Date Code:   {expected['batch']} {expected['week']} {expected['country']} {expected['year']}")
    print(f"   Lot Code:    {expected['lot_code']}")
    
    # Load image (try multiple possible paths)
    image_paths = [
        r"test_images\cypress_ic.png",
        r"test_images\cy8c29666.png",
        r"cypress_ic.png",
    ]
    
    image = None
    image_path = None
    for path in image_paths:
        image = cv2.imread(path)
        if image is not None:
            image_path = path
            break
    
    if image is None:
        print("\n❌ Error: Could not load IC image")
        print("   Please save your IC image as 'test_images/cypress_ic.png'")
        return
    
    print(f"\n✓ Loaded image: {image_path}")
    print(f"  Size: {image.shape[1]}x{image.shape[0]}")
    
    # Generate preprocessing visualization
    print("\n🔧 Generating preprocessing visualizations...")
    try:
        visualize_preprocessing_steps(image, save_path='preprocessing_debug.png')
        print("   ✓ Saved: preprocessing_debug.png")
    except Exception as e:
        print(f"   ⚠ Could not save visualization: {e}")
    
    # Save preprocessing variants
    print("\n🔧 Creating preprocessing variants...")
    variants = create_multiple_variants(image)
    for name, variant in variants:
        output_path = f'variant_{name}.png'
        cv2.imwrite(output_path, variant)
        print(f"   ✓ Saved: {output_path}")
    
    # Initialize OCR engine
    print("\n🤖 Initializing OCR Engine...")
    ocr = OCREngine()
    print("   ✓ OCR Engine ready")
    
    # Test each OCR method individually
    print("\n" + "=" * 80)
    print("TESTING INDIVIDUAL OCR METHODS")
    print("=" * 80)
    
    methods = ['easyocr', 'paddle', 'trocr', 'doctr']
    results = {}
    
    for method in methods:
        print(f"\n📝 Testing {method.upper()}...")
        try:
            result = ocr.extract_text(image, method=method)
            results[method] = result
            
            print(f"   Confidence: {result['confidence']:.2%}")
            print(f"   Text extracted:")
            for line in result['text'].split('\n'):
                if line.strip():
                    print(f"      {line}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[method] = {'text': '', 'confidence': 0}
    
    # Test ensemble method
    print("\n" + "=" * 80)
    print("TESTING ENSEMBLE METHOD (All OCR combined)")
    print("=" * 80)
    
    print("\n🎯 Running ensemble OCR (this may take 15-20 seconds)...")
    ensemble_result = ocr.extract_text(image, method='ensemble')
    
    print(f"\n✓ Ensemble complete!")
    print(f"  Overall Confidence: {ensemble_result['confidence']:.2%}")
    print(f"\n📝 Extracted Text:")
    print("-" * 80)
    print(ensemble_result['text'])
    print("-" * 80)
    
    # Parse structured data
    print("\n" + "=" * 80)
    print("PARSING STRUCTURED IC MARKINGS")
    print("=" * 80)
    
    parsed = ocr.parse_marking_structure(ensemble_result)
    
    print(f"\n🏭 Manufacturer:  {parsed['manufacturer'] or 'Unknown'}")
    print(f"🔢 Part Number:   {parsed['part_number'] or 'Not found'}")
    print(f"📅 Date Code:     {parsed['date_code'] or 'Not found'}")
    print(f"🏷️  Lot Code:      {parsed['lot_code'] or 'Not found'}")
    print(f"🌍 Country:       {parsed['country_of_origin'] or 'Not found'}")
    
    # Compare with expected
    print("\n" + "=" * 80)
    print("ACCURACY COMPARISON")
    print("=" * 80)
    
    def compare_field(field_name, expected_val, extracted_val):
        if extracted_val and expected_val:
            # Fuzzy match
            from fuzzywuzzy import fuzz
            similarity = fuzz.ratio(str(expected_val).upper(), str(extracted_val).upper())
            if similarity >= 80:
                print(f"✓ {field_name:15} : {extracted_val:25} (Match: {similarity}%)")
                return True
            else:
                print(f"✗ {field_name:15} : {extracted_val:25} (Expected: {expected_val}, Match: {similarity}%)")
                return False
        else:
            print(f"✗ {field_name:15} : Not extracted (Expected: {expected_val})")
            return False
    
    print()
    results_summary = []
    results_summary.append(compare_field("Part Number", expected['part_number'], parsed['part_number']))
    
    # Check if date code contains expected components
    date_match = False
    if parsed['date_code']:
        date_str = str(parsed['date_code'])
        date_match = (expected['year'] in date_str or 
                     expected['week'] in date_str or
                     expected['country'] in date_str)
    results_summary.append(compare_field("Date Code", f"{expected['batch']} {expected['week']} {expected['country']} {expected['year']}", 
                                        parsed['date_code']))
    
    results_summary.append(compare_field("Lot Code", expected['lot_code'], parsed['lot_code']))
    
    # Overall accuracy
    accuracy = sum(results_summary) / len(results_summary) * 100
    
    print("\n" + "=" * 80)
    print(f"OVERALL ACCURACY: {accuracy:.1f}%")
    print("=" * 80)
    
    if accuracy >= 90:
        print("\n🎉 EXCELLENT! OCR accuracy is 90%+ for this IC")
    elif accuracy >= 70:
        print("\n👍 GOOD! OCR accuracy is 70%+, minor improvements possible")
    elif accuracy >= 50:
        print("\n⚠️  FAIR. OCR accuracy is 50%+, needs improvement")
    else:
        print("\n❌ POOR. OCR accuracy is below 50%, significant improvement needed")
    
    print("\n💡 Tips for improvement:")
    print("   - Ensure image is in focus and well-lit")
    print("   - Clean IC surface (no dust, oil, fingerprints)")
    print("   - Take image straight-on (not at an angle)")
    print("   - Higher resolution helps (300+ DPI)")
    print("   - Try multiple preprocessing variants")
    
    # Save results
    print("\n📄 Saving analysis results...")
    output_file = "cypress_ic_analysis.txt"
    with open(output_file, 'w') as f:
        f.write("CYPRESS IC MARKING ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Expected Part Number: {expected['part_number']}\n")
        f.write(f"Extracted Part Number: {parsed['part_number']}\n\n")
        f.write(f"Expected Date: {expected['batch']} {expected['week']} {expected['country']} {expected['year']}\n")
        f.write(f"Extracted Date: {parsed['date_code']}\n\n")
        f.write(f"Expected Lot: {expected['lot_code']}\n")
        f.write(f"Extracted Lot: {parsed['lot_code']}\n\n")
        f.write(f"Overall Accuracy: {accuracy:.1f}%\n\n")
        f.write("\nRAW OCR TEXT:\n")
        f.write("-" * 80 + "\n")
        f.write(ensemble_result['text'])
        f.write("\n" + "-" * 80 + "\n")
    
    print(f"   ✓ Saved: {output_file}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("   - preprocessing_debug.png (preprocessing steps visualization)")
    print("   - variant_*.png (5 preprocessing variants)")
    print("   - cypress_ic_analysis.txt (detailed results)")
    print("\n")


if __name__ == "__main__":
    test_cypress_ic()
