"""
Example Usage Script
Demonstrates how to use the IC Authentication System programmatically
"""

import cv2
import os
from image_processor import ImageProcessor
from ocr_engine import OCREngine
from web_scraper import DatasheetScraper
from verification_engine import VerificationEngine


def analyze_ic_image(image_path):
    """
    Complete analysis pipeline for an IC image
    """
    print("=" * 70)
    print(f"Analyzing: {os.path.basename(image_path)}")
    print("=" * 70)
    
    # Step 1: Load image
    print("\n[1/7] Loading image...")
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return None
    print(f"✓ Image loaded: {image.shape[1]}x{image.shape[0]} pixels")
    
    # Step 2: Process image
    print("\n[2/7] Processing image...")
    processor = ImageProcessor()
    processed_images = processor.process_image(image)
    print(f"✓ Generated {len(processed_images)} processing layers")
    
    # Step 3: Detect IC regions
    print("\n[3/7] Detecting IC regions...")
    ic_regions = processor.detect_ic_regions(processed_images['enhanced'])
    print(f"✓ Found {len(ic_regions)} IC region(s)")
    
    # Step 4: Extract markings
    print("\n[4/7] Extracting marking regions...")
    marking_regions = processor.extract_marking_regions(ic_regions)
    print(f"✓ Extracted {len(marking_regions)} marking region(s)")
    
    # Step 5: OCR
    print("\n[5/7] Performing OCR...")
    ocr_engine = OCREngine()
    extracted_text = ocr_engine.extract_text(marking_regions, method='ensemble')
    print(f"✓ OCR completed with {extracted_text['confidence']:.1f}% confidence")
    print(f"\nExtracted text:\n{extracted_text['text']}")
    
    # Parse structure
    print("\n[6/7] Parsing marking structure...")
    parsed_data = ocr_engine.parse_marking_structure(extracted_text)
    print("✓ Parsed marking data:")
    for key, value in parsed_data.items():
        if value and key != 'raw_text' and key != 'lines':
            print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    # Step 6: Search datasheet
    print("\n[7/7] Searching for datasheet...")
    scraper = DatasheetScraper()
    datasheet_info = scraper.search_component_datasheet(
        parsed_data.get('part_number', ''),
        parsed_data.get('manufacturer', '')
    )
    
    if datasheet_info.get('found'):
        print(f"✓ Datasheet information found")
    else:
        print("⚠ Datasheet not found - using simulated data")
    
    # Extract marking specs
    official_markings = scraper.extract_marking_specifications(datasheet_info)
    
    # Step 7: Verify authenticity
    print("\n" + "=" * 70)
    print("VERIFICATION ANALYSIS")
    print("=" * 70)
    
    verifier = VerificationEngine()
    verification_result = verifier.verify_component(
        parsed_data,
        official_markings,
        processed_images
    )
    
    # Display results
    print(f"\nAuthenticity: {'AUTHENTIC ✓' if verification_result['is_authentic'] else 'SUSPECT ✗'}")
    print(f"Confidence: {verification_result['confidence']:.1f}%")
    
    print(f"\nChecks Passed ({len(verification_result['checks_passed'])}):")
    for check in verification_result['checks_passed']:
        print(f"  ✓ {check}")
    
    if verification_result['checks_failed']:
        print(f"\nChecks Failed ({len(verification_result['checks_failed'])}):")
        for check in verification_result['checks_failed']:
            print(f"  ✗ {check}")
    
    if verification_result['anomalies']:
        print(f"\nAnomalies Detected:")
        for anomaly in verification_result['anomalies']:
            print(f"  • {anomaly}")
    
    print(f"\n{'-' * 70}")
    print("RECOMMENDATION:")
    print(f"{'-' * 70}")
    print(verification_result['recommendation'])
    
    print("\n" + "=" * 70)
    
    return {
        'extracted': parsed_data,
        'official': official_markings,
        'verification': verification_result
    }


def batch_analyze(image_folder):
    """
    Analyze multiple images in a folder
    """
    print("\n" + "=" * 70)
    print("BATCH ANALYSIS MODE")
    print("=" * 70)
    
    # Find all images
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    image_files = [
        os.path.join(image_folder, f)
        for f in os.listdir(image_folder)
        if f.lower().endswith(image_extensions)
    ]
    
    if not image_files:
        print(f"No images found in {image_folder}")
        return
    
    print(f"\nFound {len(image_files)} image(s) to analyze\n")
    
    results = []
    for i, image_path in enumerate(image_files, 1):
        print(f"\n{'=' * 70}")
        print(f"Image {i}/{len(image_files)}")
        print(f"{'=' * 70}")
        
        try:
            result = analyze_ic_image(image_path)
            if result:
                results.append({
                    'image': os.path.basename(image_path),
                    'result': result
                })
        except Exception as e:
            print(f"✗ Error analyzing {image_path}: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("BATCH ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"\nTotal images analyzed: {len(results)}")
    
    authentic_count = sum(
        1 for r in results 
        if r['result']['verification']['is_authentic']
    )
    
    print(f"Authentic: {authentic_count}")
    print(f"Suspect: {len(results) - authentic_count}")
    
    if results:
        avg_confidence = sum(
            r['result']['verification']['confidence'] 
            for r in results
        ) / len(results)
        print(f"Average confidence: {avg_confidence:.1f}%")
    
    print("\nDetailed Results:")
    for r in results:
        status = "✓ AUTHENTIC" if r['result']['verification']['is_authentic'] else "✗ SUSPECT"
        conf = r['result']['verification']['confidence']
        print(f"  {r['image']}: {status} ({conf:.1f}%)")


def main():
    """Main example function"""
    print("\n" + "=" * 70)
    print("IC Authentication System - Example Usage")
    print("=" * 70)
    
    # Check if test images exist
    test_folder = 'test_images'
    
    if not os.path.exists(test_folder):
        print(f"\nError: Test images folder '{test_folder}' not found")
        print("Please create the folder and add IC images to test.")
        return
    
    # Get list of test images
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    test_images = [
        os.path.join(test_folder, f)
        for f in os.listdir(test_folder)
        if f.lower().endswith(image_extensions)
    ]
    
    if not test_images:
        print(f"\nNo images found in '{test_folder}' folder")
        print("Please add IC images to test.")
        return
    
    print(f"\nFound {len(test_images)} test image(s)")
    print("\nOptions:")
    print("1. Analyze single image")
    print("2. Batch analyze all images")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == '1':
        if len(test_images) == 1:
            analyze_ic_image(test_images[0])
        else:
            print("\nAvailable images:")
            for i, img in enumerate(test_images, 1):
                print(f"{i}. {os.path.basename(img)}")
            
            img_choice = input(f"\nSelect image (1-{len(test_images)}): ").strip()
            try:
                idx = int(img_choice) - 1
                if 0 <= idx < len(test_images):
                    analyze_ic_image(test_images[idx])
                else:
                    print("Invalid choice")
            except ValueError:
                print("Invalid input")
    
    elif choice == '2':
        batch_analyze(test_folder)
    
    else:
        print("Invalid choice")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
