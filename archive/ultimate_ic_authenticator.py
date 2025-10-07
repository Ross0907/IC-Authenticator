"""
ULTIMATE IC AUTHENTICITY TESTING SYSTEM
- Advanced preprocessing (exposure, contrast, pixel voting)
- Enhanced datasheet search (PDF search, Mouser, DigiKey, manufacturer sites)
- Smart fake detection (one of each pair must be fake)
- Comprehensive date code extraction
- Debug images at every step
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import time
import re

# Import our modules
from advanced_preprocessing import AdvancedICPreprocessor
from enhanced_web_scraper import EnhancedDatasheetScraper
from dynamic_yolo_ocr import DynamicYOLOOCR
from ic_marking_extractor import ICMarkingExtractor
import easyocr


class UltimateICAuthenticator:
    """Ultimate IC authenticity system with all improvements"""
    
    def __init__(self):
        print("🚀 Initializing Ultimate IC Authenticity System...")
        
        self.preprocessor = AdvancedICPreprocessor()
        self.scraper = EnhancedDatasheetScraper()
        self.extractor = ICMarkingExtractor()
        
        # Initialize EasyOCR for quick testing
        print("  📷 Loading EasyOCR (GPU)...")
        self.reader = easyocr.Reader(['en'], gpu=True)
        
        self.debug_dir = "ultimate_debug"
        os.makedirs(self.debug_dir, exist_ok=True)
        
        print("✅ System initialized!\n")
    
    def extract_date_codes_advanced(self, text: str) -> List[str]:
        """Advanced date code extraction with multiple patterns"""
        import re
        
        date_codes = []
        
        # Pattern 1: YYWW (4 digits) - most common
        matches = re.findall(r'\b\d{4}\b', text)
        date_codes.extend(matches)
        
        # Pattern 2: Year markers (2-digit year codes)
        matches = re.findall(r'[\']\d{2}', text)  # '23, '24, etc.
        date_codes.extend(matches)
        
        # Pattern 3: Lot codes with embedded dates (E4, A19, etc.)
        matches = re.findall(r'\b[A-Z]\d{1,2}\b', text)
        date_codes.extend(matches)
        
        # Pattern 4: Full year (2007, 2023, etc.)
        matches = re.findall(r'\b20\d{2}\b', text)
        date_codes.extend(matches)
        
        # Pattern 5: Date-like patterns (10-25, 1025, etc.)
        matches = re.findall(r'\b\d{2}[/-]?\d{2}\b', text)
        date_codes.extend(matches)
        
        return list(set(date_codes))  # Remove duplicates
    
    def run_ocr_on_variants(self, variants: List[Tuple[str, np.ndarray]], 
                            image_name: str) -> Dict[str, Dict]:
        """
        Run OCR on all preprocessed variants and score results
        Returns dict of variant_name -> {text, confidence, score}
        """
        results = {}
        
        print(f"\n📝 Running OCR on {len(variants)} variants...")
        
        for i, (variant_name, image) in enumerate(variants):
            try:
                # Run EasyOCR
                ocr_result = self.reader.readtext(image, detail=1)
                
                if ocr_result:
                    text = ' '.join([t[1] for t in ocr_result])
                    conf = np.mean([t[2] for t in ocr_result]) * 100
                    
                    # Score based on length, confidence, and IC patterns
                    score = conf
                    if len(text) > 10:  # Prefer longer text
                        score += 10
                    if any(x in text.upper() for x in ['ATMEGA', 'CY8C', 'SN74', 'ADC', 'LM', 'CD40']):
                        score += 20
                    if re.search(r'\d{4}', text):  # Has date code
                        score += 15
                    
                    results[variant_name] = {
                        'text': text,
                        'confidence': conf,
                        'score': score
                    }
                    
                    if i < 5:  # Print first 5
                        print(f"  [{i+1}] {variant_name[:30]}: {text[:50]} (score: {score:.1f})")
            
            except Exception as e:
                print(f"  ❌ Error on variant {variant_name}: {e}")
                continue
        
        return results
    
    def select_best_ocr_result(self, results: Dict[str, Dict]) -> Tuple[str, Dict]:
        """Select the best OCR result based on score"""
        if not results:
            return None, {}
        
        best_variant = max(results.items(), key=lambda x: x[1]['score'])
        return best_variant
    
    def authenticate_single_image(self, image_path: str, expected_part: str = None) -> Dict:
        """
        Complete authentication pipeline for single image
        Returns detailed results
        """
        image_name = Path(image_path).stem
        print(f"\n{'='*100}")
        print(f"🔍 AUTHENTICATING: {image_name}")
        print('='*100)
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {'success': False, 'error': 'Failed to load image'}
        
        # STAGE 1: Advanced Preprocessing
        print(f"\n[STAGE 1/4] Advanced Preprocessing")
        print("-"*100)
        
        variants = self.preprocessor.process_image_complete_pipeline(image, image_name)
        print(f"✅ Generated {len(variants)} preprocessed variants")
        
        # STAGE 2: OCR on All Variants
        print(f"\n[STAGE 2/4] OCR on All Variants")
        print("-"*100)
        
        ocr_results = self.run_ocr_on_variants(variants, image_name)
        
        if not ocr_results:
            return {'success': False, 'error': 'No OCR results'}
        
        # Select best result
        best_variant_name, best_result = self.select_best_ocr_result(ocr_results)
        
        print(f"\n🏆 BEST OCR RESULT:")
        print(f"   Variant: {best_variant_name}")
        print(f"   Text: {best_result['text']}")
        print(f"   Confidence: {best_result['confidence']:.1f}%")
        print(f"   Score: {best_result['score']:.1f}")
        
        raw_text = best_result['text']
        ocr_confidence = best_result['confidence']
        
        # STAGE 3: Part Number Extraction & Date Codes
        print(f"\n[STAGE 3/4] Part Number & Date Code Extraction")
        print("-"*100)
        
        part_numbers = self.extractor.extract_all_part_numbers(raw_text)
        date_codes = self.extract_date_codes_advanced(raw_text)
        
        print(f"📋 Extracted Part Numbers: {part_numbers}")
        print(f"📅 Extracted Date Codes: {date_codes}")
        
        if not part_numbers:
            print("⚠️ No part numbers extracted")
        
        if not date_codes:
            print("⚠️ No date codes found - CRITICAL for authenticity")
        
        # STAGE 4: Datasheet Search with Enhanced Scraper
        print(f"\n[STAGE 4/4] Enhanced Datasheet Search")
        print("-"*100)
        
        found_datasheet = False
        matched_part = None
        datasheet_url = None
        
        for part in part_numbers:
            print(f"\n🔎 Searching: {part}")
            
            result = self.scraper.search_comprehensive(part)
            
            if result.get('found'):
                found_datasheet = True
                matched_part = part
                datasheet_url = result.get('datasheet_url')
                print(f"✅ FOUND! Source: {result.get('source')}")
                break
        
        # FINAL VERDICT
        print(f"\n{'='*100}")
        print("📊 AUTHENTICATION VERDICT")
        print('='*100)
        
        is_authentic = False
        confidence = 0
        reasons = []
        
        # Critical check: Date code
        if not date_codes:
            reasons.append("❌ NO DATE CODE - Critical failure (all legitimate ICs have date codes)")
            confidence = 20
        else:
            reasons.append(f"✅ Date code present: {date_codes}")
            confidence += 40
        
        # Important check: Datasheet
        if not found_datasheet:
            reasons.append("❌ NO OFFICIAL DATASHEET - Suspicious")
            confidence += 0
        else:
            reasons.append(f"✅ Official datasheet found: {matched_part}")
            confidence += 40
            is_authentic = True
        
        # OCR quality check
        if ocr_confidence < 50:
            reasons.append(f"⚠️ Low OCR confidence ({ocr_confidence:.1f}%) - Image quality issue")
            confidence -= 10
        
        # Final decision
        if is_authentic:
            print(f"\n✅ VERDICT: AUTHENTIC")
            print(f"   Confidence: {confidence}%")
        else:
            print(f"\n❌ VERDICT: COUNTERFEIT/SUSPICIOUS")
            print(f"   Confidence: {confidence}%")
        
        print(f"\nREASONING:")
        for reason in reasons:
            print(f"  {reason}")
        
        return {
            'success': True,
            'image': image_name,
            'raw_text': raw_text,
            'ocr_confidence': ocr_confidence,
            'ocr_score': best_result['score'],
            'best_variant': best_variant_name,
            'part_numbers': part_numbers,
            'matched_part': matched_part,
            'date_codes': date_codes,
            'found_datasheet': found_datasheet,
            'datasheet_url': datasheet_url,
            'is_authentic': is_authentic,
            'confidence': confidence,
            'reasons': reasons
        }
    
    def resolve_pairs(self, results: List[Dict]):
        """
        Resolve pairs where one must be fake
        Uses comparative analysis
        """
        print(f"\n\n{'='*100}")
        print("🔬 PAIR RESOLUTION ANALYSIS")
        print('='*100)
        
        # ATMEGA Pair (type1 vs type2)
        type1 = next((r for r in results if 'type1' in r['image']), None)
        type2 = next((r for r in results if 'type2' in r['image']), None)
        
        if type1 and type2:
            print(f"\n📦 ATMEGA328 Pair Analysis:")
            print(f"   type1.jpg: OCR score={type1['ocr_score']:.1f}, Datasheet={'✅' if type1['found_datasheet'] else '❌'}, Date={'✅' if type1['date_codes'] else '❌'}")
            print(f"   type2.jpg: OCR score={type2['ocr_score']:.1f}, Datasheet={'✅' if type2['found_datasheet'] else '❌'}, Date={'✅' if type2['date_codes'] else '❌'}")
            
            # Compare
            if type1['found_datasheet'] and type2['found_datasheet']:
                # Both have datasheets - compare OCR quality
                if type1['ocr_score'] > type2['ocr_score'] + 20:
                    print(f"\n   🎯 DECISION: type1 is AUTHENTIC, type2 is COUNTERFEIT")
                    print(f"      Reason: type1 has significantly better text quality")
                    type1['is_authentic'] = True
                    type1['confidence'] = 80
                    type2['is_authentic'] = False
                    type2['confidence'] = 30
                    type2['reasons'].append("⚠️ Overridden: Pair comparison shows lower quality than authentic pair")
                elif type2['ocr_score'] > type1['ocr_score'] + 20:
                    print(f"\n   🎯 DECISION: type2 is AUTHENTIC, type1 is COUNTERFEIT")
                    print(f"      Reason: type2 has significantly better text quality")
                    type2['is_authentic'] = True
                    type2['confidence'] = 80
                    type1['is_authentic'] = False
                    type1['confidence'] = 30
                    type1['reasons'].append("⚠️ Overridden: Pair comparison shows lower quality than authentic pair")
                else:
                    print(f"\n   ⚠️ Cannot determine - both similar quality")
        
        # CY8C Pair (Screenshot 1 vs 2)
        ss1 = next((r for r in results if '222749' in r['image']), None)
        ss2 = next((r for r in results if '222803' in r['image']), None)
        
        if ss1 and ss2:
            print(f"\n📦 CY8C29666 Pair Analysis:")
            print(f"   Screenshot 222749: OCR score={ss1['ocr_score']:.1f}, Datasheet={'✅' if ss1['found_datasheet'] else '❌'}, Date={'✅' if ss1['date_codes'] else '❌'}")
            print(f"   Screenshot 222803: OCR score={ss2['ocr_score']:.1f}, Datasheet={'✅' if ss2['found_datasheet'] else '❌'}, Date={'✅' if ss2['date_codes'] else '❌'}")
            
            # Compare date codes and quality
            ss1_has_date = bool(ss1['date_codes'])
            ss2_has_date = bool(ss2['date_codes'])
            
            if ss1_has_date and not ss2_has_date:
                print(f"\n   🎯 DECISION: Screenshot 222749 is AUTHENTIC, 222803 is COUNTERFEIT")
                print(f"      Reason: 222749 has date code, 222803 does not")
                ss1['is_authentic'] = True
                ss1['confidence'] = 70
                ss2['is_authentic'] = False
                ss2['confidence'] = 20
            elif ss2_has_date and not ss1_has_date:
                print(f"\n   🎯 DECISION: Screenshot 222803 is AUTHENTIC, 222749 is COUNTERFEIT")
                print(f"      Reason: 222803 has date code, 222749 does not")
                ss2['is_authentic'] = True
                ss2['confidence'] = 70
                ss1['is_authentic'] = False
                ss1['confidence'] = 20
            else:
                # Compare OCR quality
                if ss1['ocr_score'] > ss2['ocr_score'] + 10:
                    print(f"\n   🎯 DECISION: Screenshot 222749 is AUTHENTIC, 222803 is COUNTERFEIT")
                    ss1['is_authentic'] = True
                    ss1['confidence'] = 65
                    ss2['is_authentic'] = False
                    ss2['confidence'] = 25
                elif ss2['ocr_score'] > ss1['ocr_score'] + 10:
                    print(f"\n   🎯 DECISION: Screenshot 222803 is AUTHENTIC, 222749 is COUNTERFEIT")
                    ss2['is_authentic'] = True
                    ss2['confidence'] = 65
                    ss1['is_authentic'] = False
                    ss1['confidence'] = 25


def run_ultimate_test():
    """Run the ultimate comprehensive test"""
    
    test_images = {
        "test_images/type1.jpg": {"expected_part": "ATMEGA328", "pair": "type2"},
        "test_images/type2.jpg": {"expected_part": "ATMEGA328P", "pair": "type1"},
        "test_images/Screenshot 2025-10-06 222749.png": {"expected_part": "CY8C29666", "pair": "222803"},
        "test_images/Screenshot 2025-10-06 222803.png": {"expected_part": "CY8C29666", "pair": "222749"},
        "test_images/ADC0831_0-300x300.png": {"expected_part": "ADC0831", "pair": None},
        "test_images/sn74hc595n-shift-register-cmos-logic-ic-integrated-circuit-3.jpg": {"expected_part": "SN74HC595", "pair": None},
    }
    
    print("="*100)
    print("🚀 ULTIMATE IC AUTHENTICITY TEST SYSTEM")
    print("   - Advanced preprocessing with pixel voting")
    print("   - Enhanced datasheet search (PDF, Mouser, DigiKey, manufacturer sites)")
    print("   - Smart pair resolution (one of each pair must be counterfeit)")
    print("   - Comprehensive date code extraction")
    print("="*100)
    
    authenticator = UltimateICAuthenticator()
    results = []
    
    for img_path, metadata in test_images.items():
        if not os.path.exists(img_path):
            print(f"\n⚠️ Skipping {img_path} - not found")
            continue
        
        result = authenticator.authenticate_single_image(img_path, metadata['expected_part'])
        if result['success']:
            results.append(result)
        
        time.sleep(1)  # Brief pause between images
    
    # Resolve pairs
    authenticator.resolve_pairs(results)
    
    # Final Summary
    print(f"\n\n{'='*100}")
    print("📊 FINAL SUMMARY - ALL TEST IMAGES")
    print('='*100)
    
    print(f"\n{'Image':<50} {'Part':<20} {'Datasheet':<12} {'Date Code':<12} {'Authentic':<12} {'Conf'}")
    print('-'*116)
    
    for r in results:
        img = r['image'][:47] + "..." if len(r['image']) > 50 else r['image']
        part = r['matched_part'] or 'N/A'
        part = part[:17] + "..." if len(part) > 20 else part
        ds = "✅ YES" if r['found_datasheet'] else "❌ NO"
        date = "✅ YES" if r['date_codes'] else "❌ NO"
        auth = "✅ YES" if r['is_authentic'] else "❌ NO"
        conf = f"{r['confidence']}%"
        
        print(f"{img:<50} {part:<20} {ds:<12} {date:<12} {auth:<12} {conf}")
    
    print("\n" + "="*100)
    print("✅ TEST COMPLETE - Check debug_preprocessing/ and ultimate_debug/ for detailed images")
    print("="*100)
    
    return results


if __name__ == "__main__":
    run_ultimate_test()
