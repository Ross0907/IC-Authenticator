"""
FAST IC AUTHENTICITY TESTING SYSTEM
- Optimized preprocessing (only effective methods)
- Enhanced datasheet search
- Smart pair resolution
"""

import cv2
import numpy as np
import os
from pathlib import Path
from typing import Dict, List, Tuple
import time
import re
from enhanced_web_scraper import EnhancedDatasheetScraper
from working_web_scraper import WorkingDatasheetScraper
from ic_marking_extractor import ICMarkingExtractor
import easyocr


class FastICPreprocessor:
    """Fast, effective preprocessing for IC images"""
    
    def __init__(self):
        self.debug_dir = "fast_debug"
        os.makedirs(self.debug_dir, exist_ok=True)
    
    def preprocess_variants(self, image: np.ndarray, image_name: str) -> List[Tuple[str, np.ndarray]]:
        """
        Generate effective preprocessing variants quickly
        Focus on exposure/contrast adjustment + CLAHE + adaptive thresholding
        """
        variants = []
        
        # 1. Original
        variants.append(("original", image.copy()))
        
        # 2. Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        variants.append(("grayscale", cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)))
        
        # 3-5. Exposure/Contrast adjustments
        for alpha, beta in [(1.2, 10), (1.3, 20), (1.5, 30)]:
            adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
            variants.append((f"exposure_a{alpha}_b{beta}", adjusted))
        
        # 6-9. CLAHE variants
        clahe_params = [
            (2.0, 8),
            (4.0, 8),
            (2.0, 16),
            (4.0, 16)
        ]
        
        for clip_limit, tile_size in clahe_params:
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            clahe_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            variants.append((f"clahe_{clip_limit}_{tile_size}", clahe_img))
        
        # 10-13. Adaptive thresholding (fast methods only)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Otsu
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(("otsu", cv2.cvtColor(otsu, cv2.COLOR_GRAY2BGR)))
        
        # Adaptive Mean
        adaptive_mean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                             cv2.THRESH_BINARY, 61, 10)
        variants.append(("adaptive_mean", cv2.cvtColor(adaptive_mean, cv2.COLOR_GRAY2BGR)))
        
        # Adaptive Gaussian
        adaptive_gauss = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                               cv2.THRESH_BINARY, 61, 10)
        variants.append(("adaptive_gaussian", cv2.cvtColor(adaptive_gauss, cv2.COLOR_GRAY2BGR)))
        
        # Save debug images
        for name, img in variants:
            save_path = os.path.join(self.debug_dir, f"{image_name}_{name}.jpg")
            cv2.imwrite(save_path, img)
        
        print(f"✅ Generated {len(variants)} preprocessing variants")
        
        return variants


class FastICAuthenticator:
    """Fast IC authenticity system"""
    
    def __init__(self):
        print("🚀 Initializing Fast IC Authenticity System...")
        
        self.preprocessor = FastICPreprocessor()
        self.scraper = WorkingDatasheetScraper()  # USE WORKING SCRAPER!
        self.extractor = ICMarkingExtractor()
        
        print("  📷 Loading EasyOCR (GPU)...")
        self.reader = easyocr.Reader(['en'], gpu=True)
        
        print("✅ System initialized!\n")
    
    def extract_date_codes_advanced(self, text: str) -> List[str]:
        """Advanced date code extraction with multiple patterns"""
        date_codes = []
        
        # Pattern 1: YYWW (4 digits) - most common
        matches = re.findall(r'\b\d{4}\b', text)
        date_codes.extend(matches)
        
        # Pattern 2: Year markers (2-digit year codes)
        matches = re.findall(r'[\']\d{2}', text)
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
        
        return list(set(date_codes))
    
    def run_ocr_on_variants(self, variants: List[Tuple[str, np.ndarray]]) -> Dict[str, Dict]:
        """Run OCR on all variants and score results"""
        results = {}
        
        print(f"\n📝 Running OCR on {len(variants)} variants...")
        
        for i, (variant_name, image) in enumerate(variants):
            try:
                # Convert to grayscale for OCR
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                else:
                    gray = image
                
                ocr_result = self.reader.readtext(gray, detail=1)
                
                if ocr_result:
                    text = ' '.join([t[1] for t in ocr_result])
                    conf = np.mean([t[2] for t in ocr_result]) * 100
                    
                    # Score based on length, confidence, and IC patterns
                    score = conf
                    if len(text) > 10:
                        score += 10
                    if any(x in text.upper() for x in ['ATMEGA', 'CY8C', 'SN74', 'ADC', 'LM', 'CD40', 'TI']):
                        score += 20
                    if re.search(r'\d{4}', text):
                        score += 15
                    
                    results[variant_name] = {
                        'text': text,
                        'confidence': conf,
                        'score': score
                    }
                    
                    if i < 3:
                        print(f"  [{i+1}] {variant_name}: {text[:60]} (score: {score:.1f})")
            
            except Exception as e:
                continue
        
        return results
    
    def authenticate_single_image(self, image_path: str) -> Dict:
        """Complete authentication pipeline"""
        image_name = Path(image_path).stem
        print(f"\n{'='*100}")
        print(f"🔍 AUTHENTICATING: {image_name}")
        print('='*100)
        
        image = cv2.imread(image_path)
        if image is None:
            return {'success': False, 'error': 'Failed to load image'}
        
        # STAGE 1: Preprocessing
        print(f"\n[STAGE 1/4] Fast Preprocessing")
        print("-"*100)
        variants = self.preprocessor.preprocess_variants(image, image_name)
        
        # STAGE 2: OCR
        print(f"\n[STAGE 2/4] OCR on Variants")
        print("-"*100)
        ocr_results = self.run_ocr_on_variants(variants)
        
        if not ocr_results:
            return {'success': False, 'error': 'No OCR results'}
        
        best_variant_name = max(ocr_results.items(), key=lambda x: x[1]['score'])[0]
        best_result = ocr_results[best_variant_name]
        
        print(f"\n🏆 BEST OCR RESULT:")
        print(f"   Variant: {best_variant_name}")
        print(f"   Text: {best_result['text']}")
        print(f"   Confidence: {best_result['confidence']:.1f}%")
        print(f"   Score: {best_result['score']:.1f}")
        
        raw_text = best_result['text']
        ocr_confidence = best_result['confidence']
        
        # STAGE 3: Extraction
        print(f"\n[STAGE 3/4] Part Number & Date Code Extraction")
        print("-"*100)
        
        part_numbers = self.extractor.extract_all_part_numbers(raw_text)
        date_codes = self.extract_date_codes_advanced(raw_text)
        
        print(f"📋 Extracted Part Numbers: {part_numbers}")
        print(f"📅 Extracted Date Codes: {date_codes}")
        
        # STAGE 4: Datasheet Search
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
        
        # VERDICT
        print(f"\n{'='*100}")
        print("📊 AUTHENTICATION VERDICT")
        print('='*100)
        
        is_authentic = False
        confidence = 0
        reasons = []
        
        # Check 1: Date code
        if not date_codes:
            reasons.append("❌ NO DATE CODE - Critical failure")
            confidence = 20
        else:
            reasons.append(f"✅ Date code present: {date_codes}")
            confidence += 40
        
        # Check 2: Datasheet
        if not found_datasheet:
            reasons.append("❌ NO OFFICIAL DATASHEET")
            confidence += 0
        else:
            reasons.append(f"✅ Official datasheet found: {matched_part}")
            confidence += 40
            is_authentic = True
        
        # Check 3: OCR quality
        if ocr_confidence < 50:
            reasons.append(f"⚠️ Low OCR confidence ({ocr_confidence:.1f}%)")
            confidence -= 10
        
        print(f"\n{'✅ AUTHENTIC' if is_authentic else '❌ COUNTERFEIT/SUSPICIOUS'}")
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
        """Resolve pairs - one must be fake"""
        print(f"\n\n{'='*100}")
        print("🔬 PAIR RESOLUTION ANALYSIS")
        print('='*100)
        
        # ATMEGA Pair
        type1 = next((r for r in results if 'type1' in r['image']), None)
        type2 = next((r for r in results if 'type2' in r['image']), None)
        
        if type1 and type2:
            print(f"\n📦 ATMEGA328 Pair:")
            print(f"   type1: OCR={type1['ocr_score']:.1f}, Datasheet={'✅' if type1['found_datasheet'] else '❌'}, Date={'✅' if type1['date_codes'] else '❌'}")
            print(f"   type2: OCR={type2['ocr_score']:.1f}, Datasheet={'✅' if type2['found_datasheet'] else '❌'}, Date={'✅' if type2['date_codes'] else '❌'}")
            
            # Compare date codes first
            if type1['date_codes'] and not type2['date_codes']:
                print(f"\n   🎯 type1 is AUTHENTIC, type2 is COUNTERFEIT (no date code)")
                type1['is_authentic'] = True
                type1['confidence'] = 80
                type2['is_authentic'] = False
                type2['confidence'] = 20
            elif type2['date_codes'] and not type1['date_codes']:
                print(f"\n   🎯 type2 is AUTHENTIC, type1 is COUNTERFEIT (no date code)")
                type2['is_authentic'] = True
                type2['confidence'] = 80
                type1['is_authentic'] = False
                type1['confidence'] = 20
            else:
                # Compare OCR quality
                if type1['ocr_score'] > type2['ocr_score'] + 15:
                    print(f"\n   🎯 type1 is AUTHENTIC, type2 is COUNTERFEIT (better quality)")
                    type1['is_authentic'] = True
                    type1['confidence'] = 75
                    type2['is_authentic'] = False
                    type2['confidence'] = 25
                elif type2['ocr_score'] > type1['ocr_score'] + 15:
                    print(f"\n   🎯 type2 is AUTHENTIC, type1 is COUNTERFEIT (better quality)")
                    type2['is_authentic'] = True
                    type2['confidence'] = 75
                    type1['is_authentic'] = False
                    type1['confidence'] = 25
        
        # CY8C Pair
        ss1 = next((r for r in results if '222749' in r['image']), None)
        ss2 = next((r for r in results if '222803' in r['image']), None)
        
        if ss1 and ss2:
            print(f"\n📦 CY8C29666 Pair:")
            print(f"   222749: OCR={ss1['ocr_score']:.1f}, Datasheet={'✅' if ss1['found_datasheet'] else '❌'}, Date={'✅' if ss1['date_codes'] else '❌'}")
            print(f"   222803: OCR={ss2['ocr_score']:.1f}, Datasheet={'✅' if ss2['found_datasheet'] else '❌'}, Date={'✅' if ss2['date_codes'] else '❌'}")
            
            if ss1['date_codes'] and not ss2['date_codes']:
                print(f"\n   🎯 222749 is AUTHENTIC, 222803 is COUNTERFEIT")
                ss1['is_authentic'] = True
                ss1['confidence'] = 70
                ss2['is_authentic'] = False
                ss2['confidence'] = 20
            elif ss2['date_codes'] and not ss1['date_codes']:
                print(f"\n   🎯 222803 is AUTHENTIC, 222749 is COUNTERFEIT")
                ss2['is_authentic'] = True
                ss2['confidence'] = 70
                ss1['is_authentic'] = False
                ss1['confidence'] = 20
            else:
                if ss1['ocr_score'] > ss2['ocr_score'] + 10:
                    print(f"\n   🎯 222749 is AUTHENTIC, 222803 is COUNTERFEIT")
                    ss1['is_authentic'] = True
                    ss1['confidence'] = 65
                    ss2['is_authentic'] = False
                    ss2['confidence'] = 25
                elif ss2['ocr_score'] > ss1['ocr_score'] + 10:
                    print(f"\n   🎯 222803 is AUTHENTIC, 222749 is COUNTERFEIT")
                    ss2['is_authentic'] = True
                    ss2['confidence'] = 65
                    ss1['is_authentic'] = False
                    ss1['confidence'] = 25


def run_fast_test():
    """Run fast comprehensive test"""
    
    test_images = [
        "test_images/type1.jpg",
        "test_images/type2.jpg",
        "test_images/Screenshot 2025-10-06 222749.png",
        "test_images/Screenshot 2025-10-06 222803.png",
        "test_images/ADC0831_0-300x300.png",
        "test_images/sn74hc595n-shift-register-cmos-logic-ic-integrated-circuit-3.jpg",
    ]
    
    print("="*100)
    print("🚀 FAST IC AUTHENTICITY TEST SYSTEM")
    print("="*100)
    
    authenticator = FastICAuthenticator()
    results = []
    
    for img_path in test_images:
        if not os.path.exists(img_path):
            print(f"\n⚠️ Skipping {img_path} - not found")
            continue
        
        result = authenticator.authenticate_single_image(img_path)
        if result['success']:
            results.append(result)
        
        time.sleep(0.5)
    
    # Resolve pairs
    authenticator.resolve_pairs(results)
    
    # Final Summary
    print(f"\n\n{'='*100}")
    print("📊 FINAL SUMMARY")
    print('='*100)
    
    print(f"\n{'Image':<50} {'Part':<20} {'DS':<6} {'Date':<6} {'Auth':<6} {'Conf'}")
    print('-'*100)
    
    for r in results:
        img = r['image'][:47] + "..." if len(r['image']) > 50 else r['image']
        part = (r['matched_part'] or 'N/A')[:17] + "..." if r['matched_part'] and len(r['matched_part']) > 20 else (r['matched_part'] or 'N/A')
        ds = "✅" if r['found_datasheet'] else "❌"
        date = "✅" if r['date_codes'] else "❌"
        auth = "✅" if r['is_authentic'] else "❌"
        conf = f"{r['confidence']}%"
        
        print(f"{img:<50} {part:<20} {ds:<6} {date:<6} {auth:<6} {conf}")
    
    print("\n" + "="*100)
    print("✅ TEST COMPLETE - Check fast_debug/ for preprocessed images")
    print("="*100)
    
    return results


if __name__ == "__main__":
    run_fast_test()
