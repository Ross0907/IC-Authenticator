"""
COMPREHENSIVE AUTHENTICITY TEST
Tests OCR → Part Number Extraction → Datasheet Search → Verification → Authenticity Flag
"""

import cv2
from dynamic_yolo_ocr import DynamicYOLOOCR
from ic_marking_extractor import ICMarkingExtractor
from verification_engine import VerificationEngine
from web_scraper import DatasheetScraper
import os

print("=" * 100)
print("COMPREHENSIVE AUTHENTICITY TEST - End-to-End Pipeline")
print("=" * 100)

# Initialize all components
print("\nInitializing system components...")
ocr_system = DynamicYOLOOCR()
extractor = ICMarkingExtractor()
verifier = VerificationEngine()
scraper = DatasheetScraper()
print("All components initialized!\n")

# Test cases with expected authenticity
test_cases = {
    "ADC0831_0-300x300.png": {
        "expected_part": "ADC0831",
        "expected_authentic": True,
        "notes": "Legitimate ADC chip"
    },
    "Screenshot 2025-10-06 222749.png": {
        "expected_part": "CY8C29666",
        "expected_authentic": None,  # One is fake, one is real
        "notes": "Cypress PSoC - Part of counterfeit/real pair"
    },
    "Screenshot 2025-10-06 222803.png": {
        "expected_part": "CY8C29666",
        "expected_authentic": None,  # One is fake, one is real
        "notes": "Cypress PSoC - Part of counterfeit/real pair"
    },
    "sn74hc595n-shift-register-cmos-logic-ic-integrated-circuit-3.jpg": {
        "expected_part": "SN74HC595",
        "expected_authentic": True,
        "notes": "Legitimate TI shift register"
    },
    "type1.jpg": {
        "expected_part": "ATMEGA328",
        "expected_authentic": None,  # One is fake, one is real
        "notes": "Atmel/Microchip AVR - Part of counterfeit/real pair"
    },
    "type2.jpg": {
        "expected_part": "ATMEGA328P",
        "expected_authentic": None,  # One is fake, one is real
        "notes": "Atmel/Microchip AVR - Part of counterfeit/real pair"
    }
}

results = []

for img_name, expected_info in test_cases.items():
    print("=" * 100)
    print(f"IMAGE: {img_name}")
    print(f"Expected: {expected_info['expected_part']}")
    print(f"Notes: {expected_info['notes']}")
    print("=" * 100)
    
    img_path = f"test_images/{img_name}"
    
    if not os.path.exists(img_path):
        print(f"[SKIP] File not found: {img_path}\n")
        continue
    
    # STEP 1: OCR Extraction
    print("\n[STEP 1] OCR Text Extraction")
    print("-" * 100)
    image = cv2.imread(img_path)
    ocr_result = ocr_system.extract_text_from_ic(image)
    
    raw_text = ocr_result.get('final_text', '')
    ocr_conf = ocr_result.get('confidence', 0)
    
    print(f"Raw OCR Text: {raw_text}")
    print(f"OCR Confidence: {ocr_conf:.2%}")
    
    if not raw_text:
        print("[FAIL] No text extracted")
        results.append({
            'image': img_name,
            'success': False,
            'error': 'No OCR text'
        })
        continue
    
    # STEP 2: Part Number Extraction
    print("\n[STEP 2] Part Number Extraction")
    print("-" * 100)
    part_numbers = extractor.extract_all_part_numbers(raw_text)
    print(f"Extracted Part Numbers: {part_numbers}")
    
    if not part_numbers:
        print("[FAIL] No part numbers extracted")
        results.append({
            'image': img_name,
            'success': False,
            'error': 'No part numbers'
        })
        continue
    
    # STEP 3: Datasheet Search (try each part number)
    print("\n[STEP 3] Datasheet Search")
    print("-" * 100)
    
    found_datasheet = False
    matched_part = None
    official_data = None
    
    for part_num in part_numbers:
        print(f"\nSearching for: {part_num}")
        temp_data = scraper.get_ic_official_data(part_num, manufacturer='')
        
        if temp_data and temp_data.get('found'):
            found_datasheet = True
            matched_part = part_num
            official_data = temp_data
            print(f"[OK] Found datasheet for: {part_num}")
            break
        else:
            print(f"[FAIL] No datasheet for: {part_num}")
    
    if not found_datasheet:
        print("\n[WARNING] No datasheets found for any extracted part number")
        print("This could indicate:")
        print("  1. OCR error (wrong part number)")
        print("  2. Counterfeit (non-existent part)")
        print("  3. Obscure/old part not in databases")
        # Use first extracted part as fallback
        if part_numbers:
            matched_part = part_numbers[0]
    
    # STEP 4: Prepare data for verification
    print("\n[STEP 4] Verification Analysis")
    print("-" * 100)
    
    # Extract date code from raw text (look for 4-digit year+week codes)
    import re
    date_codes = re.findall(r'\b\d{4}\b', raw_text)
    date_code = date_codes[0] if date_codes else None
    
    extracted_data = {
        'raw_text': raw_text,
        'part_number': matched_part if matched_part else part_numbers[0],
        'date_code': date_code,
        'confidence': ocr_conf,
        'manufacturer': ''
    }
    
    print(f"Part Number: {extracted_data['part_number']}")
    print(f"Date Code: {extracted_data['date_code']}")
    print(f"Has Official Data: {found_datasheet}")
    
    # STEP 5: Authenticity Verification
    print("\n[STEP 5] Authenticity Verification")
    print("-" * 100)
    
    verification_result = verifier.verify_component(
        extracted_data=extracted_data,
        official_data=official_data if official_data else {},
        images={}
    )
    
    is_authentic = verification_result.get('is_authentic', False)
    confidence = verification_result.get('confidence', 0)
    checks_passed = verification_result.get('checks_passed', [])
    checks_failed = verification_result.get('checks_failed', [])
    anomalies = verification_result.get('anomalies', [])
    
    print(f"\n{'='*100}")
    print(f"VERDICT: {'AUTHENTIC' if is_authentic else 'COUNTERFEIT/SUSPICIOUS'}")
    print(f"Confidence: {confidence:.1f}%")
    print(f"{'='*100}")
    
    if checks_passed:
        print(f"\n[OK] Checks Passed ({len(checks_passed)}):")
        for check in checks_passed:
            print(f"  - {check}")
    
    if checks_failed:
        print(f"\n[FAIL] Checks Failed ({len(checks_failed)}):")
        for check in checks_failed:
            print(f"  - {check}")
    
    if anomalies:
        print(f"\n[WARNING] Anomalies Detected:")
        for anomaly in anomalies:
            print(f"  - {anomaly}")
    
    # Store result
    results.append({
        'image': img_name,
        'success': True,
        'raw_text': raw_text,
        'part_numbers': part_numbers,
        'matched_part': matched_part,
        'found_datasheet': found_datasheet,
        'date_code': date_code,
        'is_authentic': is_authentic,
        'confidence': confidence,
        'checks_passed': len(checks_passed),
        'checks_failed': len(checks_failed),
        'anomalies': len(anomalies)
    })
    
    print("\n")

# FINAL SUMMARY
print("\n" + "=" * 100)
print("FINAL SUMMARY - ALL TEST IMAGES")
print("=" * 100)

print(f"\nTotal Images Tested: {len(results)}")
print(f"Successfully Processed: {sum(1 for r in results if r['success'])}")

print("\n" + "-" * 100)
print(f"{'Image':<50} {'Part':<20} {'Datasheet':<12} {'Authentic':<12} {'Conf'}")
print("-" * 100)

for result in results:
    if result['success']:
        img = result['image'][:47] + "..." if len(result['image']) > 50 else result['image']
        part = result.get('matched_part') or 'N/A'
        if part and part != 'N/A' and len(part) > 20:
            part = part[:17] + "..."
        datasheet = "YES" if result['found_datasheet'] else "NO"
        authentic = "YES" if result['is_authentic'] else "NO"
        conf = f"{result['confidence']:.0f}%"
        
        print(f"{img:<50} {part:<20} {datasheet:<12} {authentic:<12} {conf}")

print("\n" + "=" * 100)
print("COUNTERFEIT DETECTION ANALYSIS")
print("=" * 100)

# Identify likely counterfeits
counterfeits = [r for r in results if r['success'] and not r['is_authentic']]
authentic = [r for r in results if r['success'] and r['is_authentic']]

if counterfeits:
    print(f"\n[COUNTERFEIT] Detected {len(counterfeits)} suspicious/counterfeit ICs:")
    for r in counterfeits:
        print(f"  - {r['image']}")
        print(f"    Part: {r.get('matched_part', 'Unknown')}")
        print(f"    Reason: {r['checks_failed']} checks failed, {r['anomalies']} anomalies")

if authentic:
    print(f"\n[AUTHENTIC] Detected {len(authentic)} authentic ICs:")
    for r in authentic:
        print(f"  - {r['image']}")
        print(f"    Part: {r.get('matched_part', 'Unknown')}")
        print(f"    Confidence: {r['confidence']:.0f}%")

print("\n" + "=" * 100)
print("TEST COMPLETE")
print("=" * 100)
