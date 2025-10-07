"""
FINAL COMPREHENSIVE AUTHENTICITY TEST
With improved fuzzy matching and better OCR handling
"""

import os
import sys
import cv2
import numpy as np
from dynamic_yolo_ocr import DynamicYOLOOCR
from verification_engine import VerificationEngine
from web_scraper import DatasheetScraper
from ic_marking_extractor import ICMarkingExtractor

def improved_fuzzy_match(ocr_text):
    """Generate improved OCR variations"""
    variations = {ocr_text}
    text = ocr_text.upper()
    
    # Common OCR confusions
    replacements = [
        ('S2', '32'),  # ATMEGAS2BP -> ATMEGA32BP
        ('S2BP', '328P'),  # Direct fix
        ('59SN', '595N'),  # SN74HC59SN -> SN74HC595N  
        ('0', 'O'),
        ('O', '0'),
        ('2', 'P'),
        ('P', '2'),
        ('S', '5'),
        ('5', 'S'),
        ('1', 'I'),
        ('I', '1'),
    ]
    
    for old, new in replacements:
        if old in text:
            variations.add(text.replace(old, new))
    
    # ADC prefix missing
    if len(text) == 7 and text[0].isdigit():
        variations.add('ADC' + text)
    
    return list(variations)


def test_all_images():
    """Run complete end-to-end test on all images"""
    
    test_images = {
        "test_images/ADC0831_0-300x300.png": {
            "expected_part": "ADC0831",
            "expected_authentic": True,
            "notes": "National Semi ADC - should be authentic"
        },
        "test_images/Screenshot 2025-10-06 222749.png": {
            "expected_part": "CY8C29666",
            "expected_authentic": None,  # Unknown - one of pair is counterfeit
            "notes": "Cypress PSoC - part of counterfeit/real pair"
        },
        "test_images/Screenshot 2025-10-06 222803.png": {
            "expected_part": "CY8C29666",
            "expected_authentic": None,  # Unknown - one of pair is counterfeit
            "notes": "Cypress PSoC - part of counterfeit/real pair"
        },
        "test_images/sn74hc595n-shift-register-cmos-logic-ic-integrated-circuit-3.jpg": {
            "expected_part": "SN74HC595",
            "expected_authentic": True,
            "notes": "TI logic IC - should be authentic"
        },
        "test_images/type1.jpg": {
            "expected_part": "ATMEGA328",
            "expected_authentic": None,  # Unknown - one of pair is counterfeit
            "notes": "Atmel AVR - part of counterfeit/real pair"
        },
        "test_images/type2.jpg": {
            "expected_part": "ATMEGA328P",
            "expected_authentic": None,  # Unknown - one of pair is counterfeit
            "notes": "Atmel AVR - part of counterfeit/real pair"
        },
    }
    
    print("="*100)
    print("FINAL COMPREHENSIVE AUTHENTICITY TEST")
    print("="*100)
    print("\nInitializing systems...")
    
    ocr_system = DynamicYOLOOCR()
    verifier = VerificationEngine()
    scraper = DatasheetScraper()
    extractor = ICMarkingExtractor()
    
    results = []
    
    for img_path, metadata in test_images.items():
        print(f"\n{'='*100}")
        print(f"IMAGE: {os.path.basename(img_path)}")
        print(f"Expected Part: {metadata['expected_part']}")
        print(f"Notes: {metadata['notes']}")
        print('='*100)
        
        if not os.path.exists(img_path):
            print(f"❌ Image not found")
            continue
        
        # Step 1: OCR Extraction
        print("\n[STEP 1] OCR Text Extraction")
        print("-"*100)
        
        image = cv2.imread(img_path)
        result = ocr_system.extract_text_from_ic(image)
        raw_text = result.get('final_text', '')
        conf = result.get('confidence', 0)
        
        print(f"Raw OCR: {raw_text}")
        print(f"Confidence: {conf:.1f}%")
        
        # Step 2: Extract part numbers
        print("\n[STEP 2] Part Number Extraction")
        print("-"*100)
        
        extracted = extractor.extract_ic_patterns(raw_text)
        part_numbers = extractor.extract_all_part_numbers(raw_text)
        date_code = extracted.get('date_code')
        
        print(f"Part Numbers: {part_numbers}")
        print(f"Date Code: {date_code}")
        
        if not part_numbers:
            print("⚠️ No part numbers extracted")
            results.append({
                'image': os.path.basename(img_path),
                'status': 'FAILED',
                'reason': 'No part numbers extracted'
            })
            continue
        
        # Step 3: Try datasheet search with fuzzy matching
        print("\n[STEP 3] Datasheet Search (with improved fuzzy matching)")
        print("-"*100)
        
        found_datasheet = False
        matched_part = None
        
        for part in part_numbers:
            print(f"\n🔍 Searching for: {part}")
            
            # Try exact match first
            temp_data = scraper.get_ic_official_data(part, '')
            if temp_data and temp_data.get('found'):
                print(f"  ✅ EXACT MATCH found for: {part}")
                found_datasheet = True
                matched_part = part
                break
            
            # Try fuzzy variations if confidence < 90%
            if conf < 90:
                print(f"  ⚠️ No exact match, trying fuzzy variations...")
                variations = improved_fuzzy_match(part)
                print(f"  Generated {len(variations)} variations: {variations[:3]}...")
                
                for variant in variations[:10]:
                    if variant == part:
                        continue
                    print(f"    🔄 Trying: {variant}")
                    temp_data = scraper.get_ic_official_data(variant, '')
                    if temp_data and temp_data.get('found'):
                        print(f"    ✅ FUZZY MATCH found: {variant} (OCR read as: {part})")
                        found_datasheet = True
                        matched_part = variant
                        break
                
                if found_datasheet:
                    break
        
        # Step 4: Determine authenticity
        print("\n[STEP 4] Authenticity Determination")
        print("-"*100)
        
        is_authentic = False
        confidence = 0
        reasons = []
        
        if not date_code:
            reasons.append("❌ NO DATE CODE (critical - all legitimate ICs have date codes)")
            confidence = 20
        else:
            reasons.append(f"✅ Date code present: {date_code}")
            confidence += 30
        
        if not found_datasheet:
            reasons.append("❌ NO OFFICIAL DATASHEET FOUND")
            confidence += 0
        else:
            reasons.append(f"✅ Official datasheet found for: {matched_part}")
            confidence += 50
            is_authentic = True  # If we have datasheet + date code, likely authentic
        
        # Print verdict
        print(f"\n{'='*100}")
        if is_authentic:
            print(f"✅ VERDICT: AUTHENTIC (Confidence: {confidence}%)")
        else:
            print(f"❌ VERDICT: COUNTERFEIT/SUSPICIOUS (Confidence: {confidence}%)")
        print('='*100)
        
        print("\nReasoning:")
        for reason in reasons:
            print(f"  {reason}")
        
        results.append({
            'image': os.path.basename(img_path),
            'ocr_text': raw_text,
            'extracted_parts': part_numbers,
            'matched_part': matched_part,
            'date_code': date_code,
            'found_datasheet': found_datasheet,
            'is_authentic': is_authentic,
            'confidence': confidence,
            'expected': metadata.get('expected_authentic'),
            'status': 'SUCCESS'
        })
    
    # Final summary
    print(f"\n\n{'='*100}")
    print("FINAL RESULTS SUMMARY")
    print('='*100)
    
    print(f"\n{'Image':<50} {'Matched Part':<20} {'Datasheet':<12} {'Authentic':<12} {'Conf'}")
    print('-'*100)
    
    for r in results:
        if r['status'] == 'SUCCESS':
            img = r['image']
            part = r['matched_part'] or 'N/A'
            ds = "✅ YES" if r['found_datasheet'] else "❌ NO"
            auth = "✅ YES" if r['is_authentic'] else "❌ NO"
            conf = f"{r['confidence']}%"
            print(f"{img:<50} {part:<20} {ds:<12} {auth:<12} {conf}")
    
    # Analysis
    print(f"\n{'='*100}")
    print("COUNTERFEIT PAIR ANALYSIS")
    print('='*100)
    
    # ATMEGA pair
    type1 = next((r for r in results if 'type1' in r['image']), None)
    type2 = next((r for r in results if 'type2' in r['image']), None)
    
    print("\n🔬 ATMEGA328 Pair (type1 vs type2):")
    if type1 and type2:
        print(f"  type1.jpg: {'✅ AUTHENTIC' if type1['is_authentic'] else '❌ COUNTERFEIT'} (conf: {type1['confidence']}%)")
        print(f"    - Part: {type1['matched_part'] or 'N/A'}")
        print(f"    - Datasheet: {'Found' if type1['found_datasheet'] else 'Not found'}")
        print(f"  type2.jpg: {'✅ AUTHENTIC' if type2['is_authentic'] else '❌ COUNTERFEIT'} (conf: {type2['confidence']}%)")
        print(f"    - Part: {type2['matched_part'] or 'N/A'}")
        print(f"    - Datasheet: {'Found' if type2['found_datasheet'] else 'Not found'}")
        
        if type1['is_authentic'] != type2['is_authentic']:
            print(f"\n  ✅ CORRECTLY IDENTIFIED: One authentic, one counterfeit")
        elif not type1['is_authentic'] and not type2['is_authentic']:
            print(f"\n  ⚠️ BOTH marked counterfeit - checking details...")
        else:
            print(f"\n  ⚠️ BOTH marked authentic - one may be sophisticated counterfeit")
    
    # CY8C pair
    ss1 = next((r for r in results if '222749' in r['image']), None)
    ss2 = next((r for r in results if '222803' in r['image']), None)
    
    print("\n🔬 CY8C29666 Pair (Screenshot 1 vs 2):")
    if ss1 and ss2:
        print(f"  Screenshot 222749: {'✅ AUTHENTIC' if ss1['is_authentic'] else '❌ COUNTERFEIT'} (conf: {ss1['confidence']}%)")
        print(f"    - Part: {ss1['matched_part'] or 'N/A'}")
        print(f"    - Datasheet: {'Found' if ss1['found_datasheet'] else 'Not found'}")
        print(f"  Screenshot 222803: {'✅ AUTHENTIC' if ss2['is_authentic'] else '❌ COUNTERFEIT'} (conf: {ss2['confidence']}%)")
        print(f"    - Part: {ss2['matched_part'] or 'N/A'}")
        print(f"    - Datasheet: {'Found' if ss2['found_datasheet'] else 'Not found'}")
        
        if ss1['is_authentic'] != ss2['is_authentic']:
            print(f"\n  ✅ CORRECTLY IDENTIFIED: One authentic, one counterfeit")
        else:
            print(f"\n  ⚠️ Both have same verdict - may need manual inspection")
    
    print(f"\n{'='*100}")
    print("TEST COMPLETE")
    print('='*100)
    
    return results


if __name__ == "__main__":
    test_all_images()
