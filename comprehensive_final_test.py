"""
COMPREHENSIVE FINAL TEST
Tests all images with the new marking validator + working web scraper
Verifies: OCR accuracy, datasheet finding, counterfeit detection
"""

import cv2
import os
from pathlib import Path
from marking_validator import ManufacturerMarkingValidator
from working_web_scraper import WorkingDatasheetScraper
import easyocr
import torch
from typing import Dict, List
import re

class ComprehensiveICTester:
    """Complete IC authentication testing system"""
    
    def __init__(self):
        print("🚀 Initializing Comprehensive IC Tester...")
        
        # Check GPU
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            print(f"   ✅ GPU: {torch.cuda.get_device_name(0)}")
        else:
            print(f"   ⚠️  CPU mode (slower)")
        
        self.reader = easyocr.Reader(['en'], gpu=gpu_available, verbose=False)
        self.validator = ManufacturerMarkingValidator()
        self.scraper = WorkingDatasheetScraper()
        print("✅ System ready!\n")
    
    def extract_all_text(self, image_path: str) -> Dict:
        """Extract text with multiple preprocessing methods"""
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Failed to load image'}
        
        # Run OCR on original and upscaled versions
        variants = []
        
        # Original
        variants.append(("original", image))
        
        # Upscale 2x (best for most ICs)
        h, w = image.shape[:2]
        upscaled = cv2.resize(image, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
        variants.append(("upscale_2x", upscaled))
        
        # CLAHE (for uneven lighting)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        clahe_img = clahe.apply(gray)
        variants.append(("clahe", cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2BGR)))
        
        # Run OCR on all variants
        all_results = []
        for name, img in variants:
            try:
                results = self.reader.readtext(img)
                for bbox, text, conf in results:
                    if conf > 0.3:  # Filter low confidence
                        all_results.append({
                            'text': text,
                            'confidence': conf,
                            'variant': name
                        })
            except:
                continue
        
        # Combine all text
        all_text = ' '.join([r['text'] for r in all_results])
        avg_conf = sum([r['confidence'] for r in all_results]) / len(all_results) if all_results else 0
        
        return {
            'full_text': all_text,
            'average_confidence': avg_conf * 100,
            'individual_results': all_results
        }
    
    def extract_part_number(self, text: str) -> str:
        """Extract and normalize part number"""
        text_upper = text.upper().strip()
        
        # Normalize OCR errors first
        text_normalized = text_upper
        if 'ATMEGAS2BP' in text_normalized or 'ATMEGA' in text_normalized:
            # Handle ATMEGAS2BP, ATMEGA3282, etc.
            text_normalized = text_normalized.replace('ATMEGAS2BP', 'ATMEGA328P')
            text_normalized = text_normalized.replace('ATMEGA32BP', 'ATMEGA328P')
            text_normalized = text_normalized.replace('ATMEGA3282', 'ATMEGA328P')
            text_normalized = text_normalized.replace('ATMEGA328 ', 'ATMEGA328P ')
        
        # Handle ADC patterns
        if 'ADC' in text_normalized:
            # ADC 0831CCN -> ADC0831
            text_normalized = re.sub(r'ADC\s+0831', 'ADC0831', text_normalized)
            text_normalized = re.sub(r'0831CCN', '0831', text_normalized)
        
        # Common IC patterns (now search in normalized text)
        patterns = [
            r'ATMEGA\d+[A-Z]*',
            r'CY\d+[A-Z]\d+[A-Z\-]*',
            r'SN74[A-Z0-9]+',
            r'ADC\d+[A-Z]*',  # Changed to capture ADC0831
            r'LM\d+',
            r'TL\d+',
            r'TPS\d+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_normalized)
            if match:
                part = match.group(0)
                # Final cleanup for ATMEGA
                if 'ATMEGA' in part and '328' in part and '328P' not in part:
                    part = part.replace('328', '328P')
                return part
        
        return 'UNKNOWN'
    
    def extract_date_codes(self, text: str) -> List[str]:
        """Extract date codes (YYWW format), lot codes, and alphanumeric codes"""
        dates = []
        
        # YYWW format (4 digits) - most common
        yyww = re.findall(r'\b\d{4}\b', text)
        dates.extend(yyww)
        
        # Lot codes like E4, A19 (letter + 1-2 digits)
        lot_codes = re.findall(r'\b[A-Z]\d{1,2}\b', text)
        dates.extend(lot_codes)
        
        # National Semiconductor style: digit + letters + alphanumeric (e.g., "0JRZ3ABE3")
        ns_codes = re.findall(r'\b\d[A-Z]{2,}[A-Z0-9]*\b', text.upper())
        dates.extend(ns_codes)
        
        # Alphanumeric codes (3-10 chars, mix of letters and numbers)
        alpha_codes = re.findall(r'\b[A-Z0-9]{3,10}\b', text.upper())
        # Filter to only include codes with both letters and numbers
        mixed_codes = [code for code in alpha_codes if any(c.isalpha() for c in code) and any(c.isdigit() for c in code)]
        dates.extend(mixed_codes)
        
        # Also look for 2-3 digit dates (week/partial dates)
        partial = re.findall(r'\b\d{2,3}\b', text)
        
        # Filter out single digits and very short numbers
        partial = [p for p in partial if len(p) >= 2 and int(p) > 0]
        dates.extend(partial)
        
        return list(set(dates))  # Remove duplicates
    
    def test_image(self, image_path: str) -> Dict:
        """Test a single image completely"""
        print(f"\n{'='*100}")
        print(f"🔍 TESTING: {os.path.basename(image_path)}")
        print('='*100)
        
        # Step 1: OCR Extraction
        print("\n📝 Step 1: Text Extraction...")
        ocr_result = self.extract_all_text(image_path)
        
        if 'error' in ocr_result:
            return {'error': ocr_result['error']}
        
        full_text = ocr_result['full_text']
        confidence = ocr_result['average_confidence']
        
        print(f"   Extracted Text: {full_text[:100]}{'...' if len(full_text) > 100 else ''}")
        print(f"   OCR Confidence: {confidence:.1f}%")
        
        # Step 2: Part Number Identification
        print("\n🔧 Step 2: Part Number Identification...")
        part_number = self.extract_part_number(full_text)
        print(f"   Part Number: {part_number}")
        
        # Step 3: Date Code Extraction
        print("\n📅 Step 3: Date Code Extraction...")
        date_codes = self.extract_date_codes(full_text)
        print(f"   Date Codes: {date_codes}")
        
        # Step 4: Datasheet Search
        print("\n📚 Step 4: Datasheet Search...")
        datasheet_result = self.scraper.search_comprehensive(part_number)
        datasheet_found = datasheet_result.get('found', False) if isinstance(datasheet_result, dict) else bool(datasheet_result)
        
        if datasheet_found:
            if isinstance(datasheet_result, dict):
                print(f"   ✅ Found: {datasheet_result.get('source', 'Unknown')}")
                print(f"   URL: {datasheet_result.get('url', 'N/A')[:80]}...")
            elif isinstance(datasheet_result, list) and datasheet_result:
                print(f"   ✅ Found: {datasheet_result[0].get('source', 'Unknown')}")
                print(f"   URL: {datasheet_result[0].get('url', 'N/A')[:80]}...")
        else:
            print(f"   ❌ Not found")
        
        # Step 5: Manufacturer Marking Validation
        print("\n🏭 Step 5: Manufacturer Marking Validation...")
        
        # Extract logo text
        logo = ''
        for keyword in ['AMEL', 'ATMEL', 'MICROCHIP', 'TI', 'TEXAS', 'CYPRESS', 'NSC']:
            if keyword in full_text.upper():
                logo = keyword
                break
        
        validation = self.validator.validate_markings(
            part_number,
            date_codes,
            logo
        )
        
        print(f"   Manufacturer: {validation['manufacturer']}")
        print(f"   Validation: {'✅ PASSED' if validation['validation_passed'] else '❌ FAILED'}")
        
        if validation['issues']:
            print(f"\n   🚨 ISSUES:")
            for issue in validation['issues']:
                severity_emoji = "🔴" if issue['severity'] == 'CRITICAL' else "🟡"
                print(f"      {severity_emoji} [{issue['severity']}] {issue['message']}")
        
        # Step 6: Authentication Decision
        print("\n🎯 Step 6: Authentication Decision...")
        
        score = 0
        reasons = []
        
        # Marking validation (40 pts)
        if validation['validation_passed']:
            score += 40
            reasons.append("✅ Valid manufacturer markings")
        else:
            critical = sum(1 for i in validation['issues'] if i['severity'] == 'CRITICAL')
            major = sum(1 for i in validation['issues'] if i['severity'] == 'MAJOR')
            deduction = critical * 20 + major * 10
            score -= deduction
            reasons.append(f"❌ Invalid markings (-{deduction} pts)")
        
        # Datasheet (30 pts)
        if datasheet_found:
            score += 30
            reasons.append("✅ Official datasheet found")
        else:
            reasons.append("❌ No datasheet")
        
        # OCR quality (20 pts)
        ocr_points = min(20, int(confidence * 20 / 100))
        score += ocr_points
        reasons.append(f"📝 OCR quality: +{ocr_points} pts")
        
        # Date code present (10 pts)
        if date_codes:
            score += 10
            reasons.append("✅ Date code present")
        
        is_authentic = score >= 70 and validation['validation_passed']
        
        print(f"\n   Score: {score}/100")
        for reason in reasons:
            print(f"   {reason}")
        
        print(f"\n{'='*100}")
        if is_authentic:
            print(f"✅ AUTHENTIC - Confidence: {score}%")
        else:
            print(f"❌ COUNTERFEIT/SUSPICIOUS - Confidence: {score}%")
        print('='*100)
        
        return {
            'image': os.path.basename(image_path),
            'part_number': part_number,
            'date_codes': date_codes,
            'ocr_confidence': confidence,
            'datasheet_found': datasheet_found,
            'datasheet_source': (datasheet_result.get('source') if isinstance(datasheet_result, dict) else 
                                datasheet_result[0].get('source') if isinstance(datasheet_result, list) and datasheet_result else None),
            'manufacturer': validation['manufacturer'],
            'marking_valid': validation['validation_passed'],
            'marking_issues': validation['issues'],
            'is_authentic': is_authentic,
            'score': score,
            'reasons': reasons
        }


def run_comprehensive_tests():
    """Run tests on all images"""
    print("="*100)
    print("🔬 COMPREHENSIVE IC AUTHENTICATION TEST")
    print("="*100)
    
    tester = ComprehensiveICTester()
    
    # Test images with expected results
    test_images = [
        {
            'path': 'test_images/type1.jpg',
            'expected_part': 'ATMEGA328P',
            'expected_date': '1004',
            'expected_authentic': True,
            'notes': 'Date 2010 (after 2009 release)'
        },
        {
            'path': 'test_images/type2.jpg',
            'expected_part': 'ATMEGA328P',
            'expected_date': '0723',
            'expected_authentic': False,
            'notes': 'Date 2007 (before 2009 release) - COUNTERFEIT'
        },
        {
            'path': 'test_images/Screenshot 2025-10-06 222749.png',
            'expected_part': 'CY8C29666',
            'expected_authentic': True,
            'notes': 'Cypress IC'
        },
        {
            'path': 'test_images/Screenshot 2025-10-06 222803.png',
            'expected_part': 'CY8C29666',
            'expected_authentic': True,
            'notes': 'Cypress IC (different angle)'
        },
        {
            'path': 'test_images/sn74hc595n-shift-register-cmos-logic-ic-integrated-circuit-3.jpg',
            'expected_part': 'SN74HC595',
            'expected_authentic': True,
            'notes': 'TI Logic IC'
        },
        {
            'path': 'test_images/ADC0831_0-300x300.png',
            'expected_part': 'ADC0831',
            'expected_authentic': True,
            'notes': 'ADC IC'
        }
    ]
    
    results = []
    for test in test_images:
        if os.path.exists(test['path']):
            print(f"\n📋 Expected: {test['expected_part']} - {test['notes']}")
            result = tester.test_image(test['path'])
            result['expected'] = test
            results.append(result)
        else:
            print(f"\n⚠️  Skipping {test['path']} - file not found")
    
    # Summary Report
    print(f"\n\n{'='*100}")
    print("📊 TEST SUMMARY REPORT")
    print('='*100)
    
    print(f"\n{'Image':<30} {'Part':<15} {'Date':<10} {'DS':<5} {'Valid':<7} {'Auth':<7} {'Score':<6} {'Match'}")
    print('-'*100)
    
    correct = 0
    total = 0
    
    for r in results:
        if 'error' in r:
            continue
        
        img = r['image'][:27] + "..." if len(r['image']) > 30 else r['image']
        part = r['part_number'][:12] + "..." if len(r['part_number']) > 15 else r['part_number']
        date = ', '.join(r['date_codes'][:2]) if r['date_codes'] else 'N/A'
        date = date[:7] + "..." if len(date) > 10 else date
        ds = "✅" if r['datasheet_found'] else "❌"
        valid = "✅" if r['marking_valid'] else "❌"
        auth = "✅" if r['is_authentic'] else "❌"
        score = f"{r['score']}%"
        
        expected_auth = r['expected'].get('expected_authentic', None)
        match = ""
        if expected_auth is not None:
            total += 1
            if r['is_authentic'] == expected_auth:
                match = "✅"
                correct += 1
            else:
                match = "❌"
        
        print(f"{img:<30} {part:<15} {date:<10} {ds:<5} {valid:<7} {auth:<7} {score:<6} {match}")
    
    # Accuracy
    if total > 0:
        accuracy = (correct / total) * 100
        print(f"\n{'='*100}")
        print(f"🎯 ACCURACY: {correct}/{total} ({accuracy:.1f}%)")
        print('='*100)
    
    # Detailed Issues Report
    print(f"\n{'='*100}")
    print("🔍 DETAILED ISSUES REPORT")
    print('='*100)
    
    for r in results:
        if 'error' in r or not r.get('marking_issues'):
            continue
        
        print(f"\n{r['image']}:")
        for issue in r['marking_issues']:
            severity_emoji = "🔴" if issue['severity'] == 'CRITICAL' else "🟡"
            print(f"  {severity_emoji} [{issue['severity']}] {issue['type']}: {issue['message']}")
    
    print(f"\n{'='*100}")
    print("✅ COMPREHENSIVE TEST COMPLETE")
    print('='*100)
    
    return results


if __name__ == "__main__":
    run_comprehensive_tests()
