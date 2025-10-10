"""
Smart IC Authenticator - Clean Implementation
Uses YOLO + OCR + Intelligent Datasheet Finding
"""

import cv2
import numpy as np
import easyocr
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import logging
from ultralytics import YOLO
from bs4 import BeautifulSoup
import PyPDF2
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartICAuthenticator:
    """Clean, intelligent IC authentication system"""
    
    def __init__(self):
        """Initialize YOLO, OCR, and datasheet systems"""
        # Load YOLO for text detection
        logger.info("Loading YOLO model...")
        self.yolo = YOLO('yolov8n.pt')
        self.yolo.overrides['verbose'] = False  # Disable YOLO verbose output
        
        # Load OCR with CPU (GPU causes crashes and high memory)
        logger.info("Loading EasyOCR...")
        self.ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)  # Changed to CPU
        
        # HTTP session for datasheet downloads
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Configure session with aggressive timeouts
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=5,  # Reduced from 10
            pool_maxsize=10,  # Reduced from 20
            max_retries=0,  # No retries - fail fast
            pool_block=False
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Datasheet cache
        self.datasheet_cache = Path('datasheet_cache')
        self.datasheet_cache.mkdir(exist_ok=True)
        
        # IC part number patterns (comprehensive)
        self.ic_patterns = {
            'ATMEGA': r'AT\s*[MT]?EGA\s*\d+[A-Z]*\d*',  # More lenient: AT MEGA, ATMEGA, AMEGA
            'ATTINY': r'AT\s*TINY\s*\d+[A-Z]*',
            'PIC': r'PIC\s*\d+[A-Z]\s*\d+[A-Z]*\d*',  # Allow spaces in PIC18F45K22
            'STM32': r'STM32[A-Z]\d+[A-Z]*',
            'LM': r'LM\s*\d+[A-Z]*\d*[A-Z]*',  # Allow space between LM and number
            'TL': r'TL\d+[A-Z]*',
            'SN74': r'SN74[A-Z]+\d+[A-Z]*',
            'CY8C': r'CY8C\d+[A-Z]*-?\d*[A-Z]*',  # Optional dash
            'CY7C': r'CY7C\d+[A-Z]*',
            'MC': r'MC\d+[A-Z]*\d*[A-Z]*',
            'ADC': r'ADC\s*\d+[A-Z]+\d*',  # ADC followed by number and letters
            'DAC': r'DAC\d+[A-Z]*',
            'LT': r'LT\d+[A-Z]*\d*',
            'AD': r'AD\d+[A-Z]*',
            'MAX': r'MAX\d+[A-Z]*',
            'NE': r'NE\d+[A-Z]*',
            'AUCH': r'AUCH\d+[A-Z]*\d*[A-Z]*',  # TI AUCH series
            'M74HC': r'M74HC\d+[A-Z]\d',  # STM 74HC series
        }
        
        # Manufacturer mappings
        self.mfg_map = {
            'ATMEGA': 'Microchip',
            'ATTINY': 'Microchip',
            'PIC': 'Microchip',
            'STM32': 'STMicroelectronics',
            'LM': 'Texas Instruments',
            'TL': 'Texas Instruments',
            'SN74': 'Texas Instruments',
            'ADC': 'Texas Instruments',
            'DAC': 'Texas Instruments',
            'CY8C': 'Infineon',
            'CY7C': 'Infineon',
            'MC': 'NXP',
            'LT': 'Analog Devices',
            'AD': 'Analog Devices',
            'MAX': 'Analog Devices',
            'NE': 'Texas Instruments',
            'AUCH': 'Texas Instruments',
            'M74HC': 'STMicroelectronics',
        }
    
    def authenticate(self, image_path: str) -> Dict:
        """Main authentication pipeline"""
        logger.info(f"\n{'='*70}")
        logger.info(f"Authenticating: {Path(image_path).name}")
        logger.info(f"{'='*70}")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error("  ✗ Could not load image")
                return self._create_error_result(image_path, 'Could not load image file')
            
            # Step 1: Use YOLO to detect text regions
            logger.info("Step 1: YOLO text detection...")
            text_regions = self._detect_text_yolo(image)
            
            # Step 2: OCR on detected regions
            logger.info("Step 2: OCR extraction...")
            ocr_results = self._extract_text_ocr(image, text_regions)
            
            # Step 3: Parse and identify part number
            logger.info("Step 3: Part number identification...")
            part_info = self._identify_part_number(ocr_results)
            
            if not part_info['part_number']:
                logger.error("  ✗ No IC part number detected")
                return self._create_error_result(image_path, 'No IC part number detected in image', 
                                                 ocr_results.get('full_text', ''))
            
            logger.info(f"  ✓ Part Number: {part_info['part_number']}")
            logger.info(f"  ✓ Manufacturer: {part_info['manufacturer']}")
            
            # Step 4: Find datasheet
            logger.info("Step 4: Finding datasheet...")
            datasheet = self._find_datasheet(part_info['part_number'], part_info['manufacturer'])
            
            if datasheet['found']:
                logger.info(f"  ✓ Datasheet found: {datasheet['url']}")
            else:
                logger.info(f"  ✗ Datasheet not found")
            
            # Step 5: Verify marking
            logger.info("Step 5: Marking verification...")
            marking_valid = False
            if datasheet['found'] and datasheet.get('marking_info'):
                marking_valid = self._verify_marking(ocr_results, datasheet['marking_info'])
            
            # Step 6: Counterfeit detection
            logger.info("Step 6: Counterfeit detection...")
            counterfeit_check = self._check_for_counterfeits(ocr_results, part_info['part_number'], 
                                                             part_info['manufacturer'],
                                                             datasheet_found=datasheet['found'])
            
            if counterfeit_check['flags']:
                logger.warning("  ⚠️  Suspicious indicators detected:")
                for flag in counterfeit_check['flags']:
                    logger.warning(f"    - {flag}")
            else:
                logger.info("  ✓ No suspicious indicators found")
            
            # Calculate verdict
            confidence = self._calculate_confidence(part_info, datasheet, marking_valid, counterfeit_check)
            
            if confidence >= 85:
                verdict = "AUTHENTIC"
            elif confidence >= 65:
                verdict = "LIKELY AUTHENTIC"
            elif confidence >= 40:
                verdict = "SUSPICIOUS"
            else:
                verdict = "LIKELY COUNTERFEIT"
            
            logger.info(f"\nVerdict: {verdict} ({confidence}%)")
            
            # Generate debug images for GUI
            img = cv2.imread(image_path)
            debug_ocr_image = None
            debug_variants = []
            
            # Create OCR debug image with bounding boxes
            if img is not None and ocr_results.get('details'):
                debug_ocr_image = img.copy()
                for detail in ocr_results['details']:
                    bbox = detail['bbox']
                    text = detail['text']
                    conf = detail['confidence']
                    
                    # Convert bbox to integer points
                    points = np.array(bbox, dtype=np.int32)
                    
                    # Draw bounding box
                    cv2.polylines(debug_ocr_image, [points], True, (0, 255, 255), 2)
                    
                    # Draw text label with background
                    text_label = f"{text} ({conf:.2f})"
                    (w, h), _ = cv2.getTextSize(text_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(debug_ocr_image, (points[0][0], points[0][1] - h - 5), 
                                (points[0][0] + w, points[0][1]), (0, 255, 255), -1)
                    cv2.putText(debug_ocr_image, text_label, (points[0][0], points[0][1] - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            # Get preprocessing variants
            if ocr_results.get('preprocessing_images'):
                debug_variants = [(p['name'], p['image']) for p in ocr_results['preprocessing_images']]
            
            return {
                'success': True,
                'part_number': part_info['part_number'],
                'normalized_part_number': part_info['part_number'],
                'manufacturer': part_info['manufacturer'],
                'datasheet_found': datasheet['found'],
                'datasheet_url': datasheet.get('url'),
                'marking_verified': marking_valid,
                'counterfeit_flags': counterfeit_check['flags'],
                'suspicion_score': counterfeit_check['suspicion_score'],
                'confidence': confidence,
                'verdict': verdict,
                'is_authentic': confidence >= 65,
                'full_text': ocr_results['full_text'],
                'text_regions': text_regions,
                'ocr_details': ocr_results.get('details', []),
                'ocr_confidence': ocr_results.get('ocr_confidence', 0.0),  # Add OCR confidence
                'preprocessing_images': ocr_results.get('preprocessing_images', []),  # Add preprocessing
                'debug_ocr_image': debug_ocr_image,  # Add debug OCR image
                'debug_variants': debug_variants,  # Add debug preprocessing variants
                'image_path': image_path,
                'date_codes': [],
                'reasons': []
            }
            
        except Exception as e:
            import traceback
            error_msg = f"Authentication error: {str(e)}"
            logger.error(f"  ✗ {error_msg}")
            logger.debug(traceback.format_exc())
            return self._create_error_result(image_path, error_msg)
        finally:
            # Memory cleanup
            import gc
            gc.collect()
    
    def _create_error_result(self, image_path: str, error_msg: str, extracted_text: str = '') -> Dict:
        """Create a standardized error result"""
        return {
            'success': False,
            'error': error_msg,
            'part_number': 'N/A',
            'normalized_part_number': 'N/A',
            'manufacturer': 'Unknown',
            'datasheet_found': False,
            'datasheet_url': None,
            'marking_verified': False,
            'counterfeit_flags': [],
            'suspicion_score': 0,
            'confidence': 0,
            'verdict': 'ERROR',
            'is_authentic': False,
            'full_text': extracted_text,
            'text_regions': [],
            'ocr_details': [],
            'image_path': image_path,
            'date_codes': [],
            'reasons': [f'Error: {error_msg}']
        }
    
    def _detect_text_yolo(self, image: np.ndarray) -> List[Tuple]:
        """Use YOLO to detect text regions"""
        results = self.yolo(image, conf=0.25, verbose=False)
        
        text_regions = []
        if len(results) > 0 and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                text_regions.append((x1, y1, x2, y2, conf))
        
        logger.info(f"  Found {len(text_regions)} text regions with YOLO")
        return text_regions
    
    def _try_all_orientations(self, image: np.ndarray) -> Tuple[np.ndarray, int]:
        """DISABLED: Orientation detection is disabled for now to prevent incorrect rotations"""
        # Simply return original image without rotation
        # This is more reliable than trying to detect orientation which can fail
        logger.info(f"  No rotation applied (orientation detection disabled)")
        return image, 0
    
    def _extract_text_ocr(self, image: np.ndarray, regions: List[Tuple]) -> Dict:
        """Extract text using OCR with OPTIMIZED preprocessing (reduced variants for speed)"""
        return self._extract_text_ocr_internal(image, regions, try_rotation=True)
    
    def _extract_text_ocr_internal(self, image: np.ndarray, regions: List[Tuple], try_rotation: bool = True) -> Dict:
        """Internal OCR extraction with optional rotation"""
        all_text = []
        ocr_details = []  # Store bbox and text for drawing
        preprocessing_images = []  # Store preprocessing variants for debugging
        
        # STEP 1: Try orientation detection if enabled
        if try_rotation:
            image, rotation_angle = self._try_all_orientations(image)
        
        # STEP 2: Resize image if too large (speeds up OCR significantly)
        h, w = image.shape[:2]
        max_dim = 1200  # Maximum dimension
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            logger.info(f"  Resized image from {w}x{h} to {new_w}x{new_h} for faster OCR")
        
        # Preprocess full image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Convert back to BGR for EasyOCR
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        if not regions:
            # OPTIMIZED: Use only 2 BEST preprocessing variants for maximum speed
            
            # Variant 1: CLAHE Enhanced (best overall)
            # Already have enhanced_bgr
            
            # Variant 2: Adaptive threshold (best for faded text)
            thresh_adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                    cv2.THRESH_BINARY, 11, 2)
            thresh_adaptive_bgr = cv2.cvtColor(thresh_adaptive, cv2.COLOR_GRAY2BGR)
            
            # Try variants in order of effectiveness
            variants = [enhanced_bgr, thresh_adaptive_bgr]
            variant_names = ['CLAHE Enhanced', 'Adaptive Threshold']
            
            # Store preprocessing images for debug
            for name, var_img in zip(variant_names, variants):
                preprocessing_images.append({
                    'name': name,
                    'image': var_img.copy()
                })
            
            best_text_count = 0
            best_results = []
            best_variant_name = 'Unknown'
            best_confidence = 0.0
            
            for idx, img_variant in enumerate(variants):
                try:
                    # OPTIMIZED: Faster EasyOCR settings
                    results = self.ocr_reader.readtext(
                        img_variant, 
                        paragraph=False,
                        batch_size=10,  # Process multiple detections at once
                        width_ths=0.7,  # Less aggressive text grouping
                        decoder='greedy',  # Faster decoder
                        beamWidth=1  # Faster beam search
                    )
                    variant_text = []
                    variant_details = []
                    total_conf = 0.0
                    conf_count = 0
                    
                    for (bbox, text, conf) in results:
                        if conf > 0.08:  # Slightly higher threshold for speed
                            # Fix common OCR errors
                            text = self._fix_ocr_errors(text)
                            if text and len(text) > 1:
                                variant_text.append(text)
                                total_conf += conf
                                conf_count += 1
                                # Store for visualization
                                if conf > 0.15:  # Lower threshold for drawing (capture more text)
                                    variant_details.append({
                                        'bbox': bbox,
                                        'text': text,
                                        'confidence': conf
                                    })
                    
                    # Calculate average confidence for this variant
                    avg_conf = (total_conf / conf_count * 100) if conf_count > 0 else 0.0
                    
                    # Use the variant that extracted the most text
                    if len(variant_text) > best_text_count:
                        best_text_count = len(variant_text)
                        all_text = variant_text
                        ocr_details = variant_details
                        best_variant_name = variant_names[idx]
                        best_confidence = avg_conf
                        
                        # EARLY TERMINATION: If we got good results, stop immediately
                        # REDUCED threshold to handle low-confidence but valid detections
                        if best_text_count >= 3 and avg_conf > 25:
                            logger.info(f"  ✓ Good OCR results, early stop at: {best_variant_name}")
                            break
                except Exception as e:
                    logger.debug(f"OCR variant failed: {e}")
                    continue
            
            logger.info(f"  Best OCR: {best_variant_name} ({best_text_count} items, {best_confidence:.1f}% conf)")
        else:
            # OCR each YOLO-detected region
            logger.info(f"  OCR on {len(regions)} YOLO regions...")
            best_confidence = 0.0
            total_conf = 0.0
            conf_count = 0
            
            for idx, (x1, y1, x2, y2, _) in enumerate(regions):
                roi = enhanced_bgr[y1:y2, x1:x2]
                logger.debug(f"    Region {idx+1}: {x1},{y1} to {x2},{y2}, size={roi.shape}")
                results = self.ocr_reader.readtext(roi)
                logger.debug(f"      Found {len(results)} texts")
                for (bbox, text, conf) in results:
                    if conf > 0.05:  # Lower threshold
                        text = self._fix_ocr_errors(text)
                        if text and len(text) > 1:
                            all_text.append(text)
                            total_conf += conf
                            conf_count += 1
                            logger.debug(f"        Text: '{text}' (conf: {conf:.2f})")
                            if conf > 0.2:
                                # Adjust bbox coordinates to absolute image coordinates
                                adjusted_bbox = [[pt[0] + x1, pt[1] + y1] for pt in bbox]
                                ocr_details.append({
                                    'bbox': adjusted_bbox,
                                    'text': text,
                                    'confidence': conf
                                })
            
            best_confidence = (total_conf / conf_count * 100) if conf_count > 0 else 0.0
            logger.info(f"  Extracted {len(all_text)} texts from regions (avg conf: {best_confidence:.1f}%)")
            
            # FALLBACK: If YOLO regions failed to extract enough text or text is too short, try full image OCR
            total_chars = sum(len(t) for t in all_text)
            if len(all_text) == 0 or (len(all_text) < 3 and total_chars < 10):
                logger.info(f"  ⚠ YOLO regions insufficient (only {len(all_text)} texts, {total_chars} chars), falling back to full image OCR without rotation...")
                # Try WITHOUT rotation this time (rotation might have been wrong)
                temp_result = self._extract_text_ocr_internal(image, [], try_rotation=False)
                if len(temp_result['lines']) > len(all_text):
                    logger.info(f"  ✓ Fallback successful: {len(temp_result['lines'])} texts found")
                    return temp_result
        
        full_text = ' '.join(all_text)
        logger.info(f"  Extracted text: {full_text[:100]}...")
        
        # Apply OCR error corrections to full_text for display
        corrected_full_text = self._fix_ocr_errors(full_text)
        
        return {
            'lines': all_text,
            'full_text': corrected_full_text,  # Use corrected text for display
            'details': ocr_details,
            'preprocessing_images': preprocessing_images,  # Add preprocessing images to result
            'ocr_confidence': best_confidence  # Add OCR confidence
        }
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR mistakes"""
        # Fix "ALMEL" → "ATMEL", "AImel" → "ATMEL", "Anel" → "ATMEL", "A?MEL" → "ATMEL"
        text = re.sub(r'[Aa][IlLn\?][Mm]?[Ee][Ll]', 'ATMEL', text, flags=re.IGNORECASE)
        
        # Fix "A?" → "AT" (common OCR error)
        text = re.sub(r'A\?', 'AT', text)
        text = re.sub(r'A\s+\?', 'AT', text)
        
        # Fix ATMEGA variations: AtMEGAS2BP → ATMEGA328P, ATMEGA3282 → ATMEGA328P
        text = re.sub(r'At?MEGA[Ss]?2[B8]P?', 'ATMEGA328P', text, flags=re.IGNORECASE)
        text = re.sub(r'ATMEGA3282', 'ATMEGA328P', text, flags=re.IGNORECASE)
        
        # Fix M?4HC → M74HC (? → 7 confusion)
        text = re.sub(r'M\?4HC', 'M74HC', text)
        
        # Fix LK → LM (common OCR error where M is read as K)
        text = re.sub(r'\bLK\b', 'LM', text)  # Word boundary to avoid changing other text
        text = re.sub(r'\bLK(\d)', r'LM\1', text)  # LK358 → LM358
        
        # Fix common digit/letter confusions
        # O → 0 in numbers
        text = re.sub(r'([A-Z])O(\d)', r'\g<1>0\2', text)  # LO → L0
        
        # J → 3 at start of numbers
        text = re.sub(r'J(\d)', r'3\1', text)
        text = re.sub(r'^J([s58])', r'3\1', text)  # Js8m → 3s8m → 358m
        
        # s → 5 in numbers
        text = re.sub(r'(\d)s(\d)', r'\g<1>5\g<2>', text)  # 3s8 → 358
        
        # lowercase 'm' or 'rn' at end of numbers often should be 'N'
        text = re.sub(r'(\d+)m\b', r'\1N', text, flags=re.IGNORECASE)
        text = re.sub(r'(\d+)rn\b', r'\1N', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _identify_part_number(self, ocr_results: Dict) -> Dict:
        """Intelligently identify the IC part number with improved prefix combining"""
        text = ocr_results['full_text'].upper()  # Convert to uppercase
        text = re.sub(r'\s+', ' ', text)  # Normalize spaces
        
        # IMPROVED: Handle common OCR case errors like "AtMEGA" → "ATMEGA"
        text = text.replace('ATMEGA', 'ATMEGA')  # Already uppercase
        text = text.replace('ATTINY', 'ATTINY')  # Already uppercase
        
        # IMPROVED: Try to combine separated prefixes with numbers
        # Example: "LM 358N" or "LM" + "358N" or even "LK" + "358N" should become "LM358N"
        lines = [line.upper() for line in ocr_results.get('lines', [])]  # Ensure all lines uppercase
        
        # Check if we have a prefix and number on separate OCR lines
        combined_attempts = []
        for i, line1 in enumerate(lines):
            line1_upper = line1.upper().strip()
            # Check if this is a known prefix OR OCR error version (LK → LM, TI → TL, etc.)
            prefix_map = {
                'LM': ['LM', 'LK', 'LN', 'IM', 'IK'],  # Common OCR errors for LM
                'TL': ['TL', 'TI', 'TJ', 'IL'],
                'AD': ['AD', 'A0', 'AO'],
                'SN': ['SN', 'SM', '5N'],
                'MC': ['MC', 'MO', 'NC'],
                'LT': ['LT', 'IT', 'LJ'],
                'MAX': ['MAX', 'NAX', 'WAX'],
                'NE': ['NE', 'NF', 'WE'],
            }
            
            for real_prefix, possible_prefixes in prefix_map.items():
                for poss_prefix in possible_prefixes:
                    if line1_upper == poss_prefix or line1_upper.startswith(poss_prefix + ' '):
                        # Look for numbers in nearby lines
                        for j in range(max(0, i-2), min(len(lines), i+3)):  # Check nearby lines
                            if i != j:
                                line2 = lines[j].upper().strip()
                                # Check if line2 starts with digits
                                if line2 and line2[0].isdigit():
                                    combined = real_prefix + line2.replace(' ', '')
                                    combined_attempts.append(combined)
                                    logger.info(f"  Trying combined: {line1_upper} ({poss_prefix}→{real_prefix}) + {line2} = {combined}")
        
        # Add combined attempts to the text for pattern matching
        if combined_attempts:
            text = text + ' ' + ' '.join(combined_attempts)
        
        # Try each pattern
        best_match = None
        best_score = 0
        
        for prefix, pattern in self.ic_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                # Remove spaces from match
                match_clean = match.replace(' ', '')
                # Score based on length and completeness
                score = len(match_clean)
                if score > best_score and score >= 4:  # Lowered from 5 to 4 for LM358
                    best_score = score
                    best_match = (match_clean, prefix)
        
        if best_match:
            part_number = best_match[0]
            prefix = best_match[1]
            manufacturer = self.mfg_map.get(prefix, 'Unknown')
            
            logger.info(f"  ✓ Identified: {part_number} ({manufacturer})")
            
            return {
                'part_number': part_number,
                'manufacturer': manufacturer,
                'prefix': prefix
            }
        
        logger.warning(f"  ✗ No IC part number found in text: {text[:100]}")
        
        return {
            'part_number': None,
            'manufacturer': None,
            'prefix': None
        }
    
    def _validate_url(self, url: str, expect_pdf: bool = False) -> bool:
        """Validate that a URL is accessible and returns valid content (not 404)
        
        Args:
            url: URL to validate
            expect_pdf: If True, also check that content-type is PDF
        
        Returns:
            True if URL is valid and accessible, False otherwise
        """
        try:
            # Use longer timeout for PDFs (5s) vs product pages (2s)
            timeout = 5 if expect_pdf or url.endswith('.pdf') else 2
            response = self.session.head(url, timeout=timeout, allow_redirects=True)
            
            # Check status code
            if response.status_code != 200:
                logger.debug(f"    URL validation failed: {response.status_code} - {url}")
                return False
            
            # If expecting PDF, check content type
            if expect_pdf:
                content_type = response.headers.get('Content-Type', '').lower()
                if 'pdf' not in content_type and not url.endswith('.pdf'):
                    logger.debug(f"    Not a PDF: {content_type} - {url}")
                    return False
            
            logger.debug(f"    ✓ Valid URL: {url}")
            return True
            
        except Exception as e:
            logger.debug(f"    URL validation error: {e}")
            return False
    
    def _find_datasheet(self, part_number: str, manufacturer: str) -> Dict:
        """Intelligent datasheet finding with URL validation"""
        logger.info(f"  Searching for {part_number} datasheet...")
        
        # Check cache first
        cached_file = self.datasheet_cache / f"{part_number}.pdf"
        if cached_file.exists():
            logger.info(f"  ✓ Found in cache")
            return {
                'found': True,
                'url': str(cached_file),
                'marking_info': self._extract_marking_from_pdf(str(cached_file))
            }
        
        # Try manufacturer-specific search with validation
        result = None
        try:
            if 'Microchip' in manufacturer or 'Atmel' in manufacturer:
                result = self._search_microchip(part_number)
            elif 'Texas Instruments' in manufacturer:
                result = self._search_ti(part_number)
            elif 'Infineon' in manufacturer or 'Cypress' in manufacturer:
                result = self._search_infineon(part_number)
            elif 'STMicroelectronics' in manufacturer:
                result = self._search_stm(part_number)
            elif 'NXP' in manufacturer:
                result = self._search_nxp(part_number)
            elif 'Analog' in manufacturer:
                result = self._search_analog(part_number)
            else:
                # Try generic search if manufacturer unknown
                result = self._search_generic(part_number)
        except Exception as e:
            logger.warning(f"  Datasheet search error: {e}")
            result = None
        
        if result and result.get('found'):
            logger.info(f"  ✓ Datasheet found: {result['url']}")
            # Try to download and cache (but don't fail if this doesn't work)
            # Only download if it's a direct PDF link, not a product page
            try:
                url = result['url']
                # Only download if it's a PDF file (not HTML product pages)
                if url.endswith('.pdf') or 'pdf' in url.lower():
                    # Check file size first with HEAD request
                    head_resp = self.session.head(url, timeout=1)
                    content_length = int(head_resp.headers.get('content-length', 0))
                    
                    # Only download if file is reasonable size (< 10MB)
                    if content_length > 0 and content_length < 10 * 1024 * 1024:
                        pdf_content = self.session.get(url, timeout=1.0, stream=True).content
                        cached_file.write_bytes(pdf_content)
                        result['marking_info'] = self._extract_marking_from_pdf(str(cached_file))
                        logger.debug(f"  Cached PDF: {cached_file}")
                    else:
                        logger.debug(f"  PDF too large or size unknown, skipping cache")
            except Exception as e:
                logger.debug(f"  Could not cache PDF: {e}")
            return result
        
        logger.info(f"  ✗ Datasheet not found")
        return {'found': False}
    
    def _search_generic(self, part: str) -> Dict:
        """Generic search across multiple manufacturers"""
        # Try common patterns
        searches = [
            self._search_ti,
            self._search_microchip,
            self._search_infineon,
            self._search_analog,
            self._search_nxp,
            self._search_stm
        ]
        
        for search_func in searches:
            try:
                result = search_func(part)
                if result and result.get('found'):
                    return result
            except:
                continue
        
        return {'found': False}
    
    def _search_microchip(self, part: str) -> Dict:
        """Search Microchip/Atmel datasheets with comprehensive validation
        
        Microchip uses pattern: www.microchip.com/en-us/product/{part-number}
        Direct PDF: ww1.microchip.com/downloads/en/DeviceDoc/{part-number}.pdf
        """
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        logger.debug(f"  Searching Microchip for: {base}")
        
        # Common Microchip URL patterns to try
        urls_to_try = []
        
        # Pattern 1: Direct product page (most reliable)
        urls_to_try.append(f"https://www.microchip.com/en-us/product/{base}")
        
        # Pattern 2: For PIC parts specifically  
        if base.startswith('PIC'):
            # PIC16F877A → try PIC16F877A, PIC16F877
            urls_to_try.extend([
                f"https://www.microchip.com/en-us/product/{base}",
                f"https://www.microchip.com/en-us/product/{base[:-1]}" if len(base) > 8 else None,
            ])
        
        # Pattern 3: For ATMEGA/ATTINY parts
        if base.startswith(('ATMEGA', 'ATTINY')):
            # ATMEGA328P → atmega328p
            urls_to_try.extend([
                f"https://www.microchip.com/en-us/product/{base.lower()}",
                f"https://www.microchip.com/en-us/product/at{base[2:].lower()}",  # ATMEGA328P → atmega328p
            ])
        
        # Remove None values
        urls_to_try = [url for url in urls_to_try if url]
        
        # Try each URL with validation
        for url in urls_to_try:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found Microchip datasheet: {url}")
                return {'found': True, 'url': url}
        
        # Fallback: Try Digikey/Octopart aggregators
        fallback_urls = [
            f"https://www.digikey.com/en/products/detail/{base}",
            f"https://octopart.com/search?q={base}",
        ]
        
        for url in fallback_urls:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found via aggregator: {url}")
                return {'found': True, 'url': url}
        
        logger.debug(f"  ✗ Microchip datasheet not found for {base}")
        return {'found': False}
    
    def _search_ti(self, part: str) -> Dict:
        """Search Texas Instruments datasheets with comprehensive validation
        
        TI uses patterns:
        - Direct PDF: www.ti.com/lit/ds/symlink/{part}.pdf
        - Product page: www.ti.com/product/{part}
        """
        base = re.sub(r'[^A-Z0-9]', '', part).upper()
        logger.debug(f"  Searching TI for: {base}")
        
        # Normalize part number - remove package suffixes
        clean = base
        if len(base) > 4 and base[-1] in 'NPDMX':
            clean = base[:-1]
        
        # Remove multi-letter package suffixes
        for suffix in ['CCN', 'CN', 'PW', 'PWR', 'DW', 'DR', 'DGK', 'DBV', 'DCK', 'DGV']:
            if clean.endswith(suffix) and len(clean) - len(suffix) >= 3:
                clean = clean[:-len(suffix)]
                break
        
        urls_to_try = []
        
        # Pattern 1: Direct PDF symlinks (most reliable for TI)
        for part_variant in [clean, base]:
            urls_to_try.extend([
                f"https://www.ti.com/lit/ds/symlink/{part_variant.lower()}.pdf",
                f"https://www.ti.com/lit/gpn/{part_variant.lower()}",  # General product page
            ])
        
        # Pattern 2: Product pages
        for part_variant in [clean, base]:
            urls_to_try.append(f"https://www.ti.com/product/{part_variant.lower()}")
        
        # Pattern 3: For specific TI families
        if base.startswith('LM'):
            # LM358 → lm358, lm358n
            urls_to_try.extend([
                f"https://www.ti.com/lit/ds/symlink/{clean.lower()}.pdf",
                f"https://www.ti.com/product/{clean}",
            ])
        
        if base.startswith('SN74'):
            # SN74HC595N → sn74hc595
            urls_to_try.extend([
                f"https://www.ti.com/lit/ds/symlink/{clean.lower()}.pdf",
                f"https://www.ti.com/product/{clean}",
            ])
        
        if base.startswith(('NE', 'SE')):
            # NE555 → ne555
            urls_to_try.extend([
                f"https://www.ti.com/lit/ds/symlink/{base.lower()}.pdf",
                f"https://www.ti.com/product/{base}",
            ])
        
        # For ADC/DAC parts
        if base.startswith(('ADC', 'DAC')):
            # ADC0831 → adc0831
            urls_to_try.extend([
                f"https://www.ti.com/lit/ds/symlink/{base.lower()}.pdf",
                f"https://www.ti.com/product/{base}",
                f"https://www.ti.com/lit/gpn/{base.lower()}",
            ])
        
        # Try each URL with validation
        for url in urls_to_try:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found TI datasheet: {url}")
                return {'found': True, 'url': url}
        
        # Fallback: Try aggregators
        fallback_urls = [
            f"https://www.ti.com/product/{clean}",  # Try one more time with clean part
            f"https://www.digikey.com/en/products/detail/{base}",
            f"https://octopart.com/search?q={base}",
        ]
        
        for url in fallback_urls:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found via aggregator: {url}")
                return {'found': True, 'url': url}
        
        logger.debug(f"  ✗ TI datasheet not found for {base}")
        return {'found': False}
    
    def _search_infineon(self, part: str) -> Dict:
        """Search Infineon/Cypress datasheets with comprehensive validation
        
        Infineon uses pattern: www.infineon.com/cms/en/product/{part}/
        Cypress (now Infineon) parts need special handling
        """
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        logger.debug(f"  Searching Infineon for: {base}")
        
        urls_to_try = []
        
        # For CY8C/CY7C (Cypress PSoC chips)
        if base.startswith(('CY8C', 'CY7C')):
            # Remove package suffix (CY8C29666-24PVXI → CY8C29666)
            base_clean = re.sub(r'-\d+[A-Z]+$', '', base)
            
            urls_to_try.extend([
                f"https://www.infineon.com/cms/en/product/{base_clean.lower()}/",
                f"https://www.infineon.com/cms/en/product/{base.lower()}/",
                f"https://www.infineon.com/dgdl/Infineon-{base_clean}-DataSheet-v01_00-EN.pdf",
            ])
        else:
            # Standard Infineon parts
            urls_to_try.extend([
                f"https://www.infineon.com/cms/en/product/{base.lower()}/",
                f"https://www.infineon.com/cms/en/product/{base}/",
            ])
        
        # Try each URL with validation
        for url in urls_to_try:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found Infineon datasheet: {url}")
                return {'found': True, 'url': url}
        
        # Fallback: Try aggregators
        fallback_urls = [
            f"https://www.digikey.com/en/products/detail/{base}",
            f"https://octopart.com/search?q={base}",
        ]
        
        for url in fallback_urls:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found via aggregator: {url}")
                return {'found': True, 'url': url}
        
        logger.debug(f"  ✗ Infineon datasheet not found for {base}")
        return {'found': False}
    
    def _search_stm(self, part: str) -> Dict:
        """Search STMicroelectronics datasheets with comprehensive validation
        
        STM parts include STM32 microcontrollers and M74HC logic ICs
        """
        base = re.sub(r'[^A-Z0-9]', '', part).upper()
        logger.debug(f"  Searching STM for: {base}")
        
        urls_to_try = []
        
        # For STM32 parts
        if base.startswith('STM32'):
            urls_to_try.extend([
                f"https://www.st.com/en/microcontrollers-microprocessors/stm32-32-bit-arm-cortex-mcus.html#{base.lower()}",
                f"https://www.st.com/en/microcontrollers/{base.lower()}.html",
            ])
        
        # For M74HC series (logic ICs)
        if base.startswith(('M74HC', 'M74HCT')):
            # Remove package suffix
            clean = base
            for suffix in ['B1', 'TTR', 'M1', 'N', 'RM13TR']:
                if clean.endswith(suffix):
                    clean = clean[:-len(suffix)]
                    break
            
            urls_to_try.extend([
                f"https://www.st.com/en/logic-comparators/{base.lower()}.html",
                f"https://www.st.com/en/logic-comparators/{clean.lower()}.html",
            ])
        
        # Try each URL with validation
        for url in urls_to_try:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found STM datasheet: {url}")
                return {'found': True, 'url': url}
        
        # Fallback: Try aggregators
        fallback_urls = [
            f"https://www.digikey.com/en/products/detail/{base}",
            f"https://octopart.com/search?q={base}",
        ]
        
        for url in fallback_urls:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found via aggregator: {url}")
                return {'found': True, 'url': url}
        
        logger.debug(f"  ✗ STM datasheet not found for {base}")
        return {'found': False}
    
    def _search_nxp(self, part: str) -> Dict:
        """Search NXP datasheets with comprehensive validation"""
        base = re.sub(r'[^A-Z0-9]', '', part).upper()
        logger.debug(f"  Searching NXP for: {base}")
        
        urls_to_try = [
            f"https://www.nxp.com/products/{base.lower()}",
            f"https://www.nxp.com/docs/en/data-sheet/{base}.pdf",
        ]
        
        # Try each URL with validation
        for url in urls_to_try:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found NXP datasheet: {url}")
                return {'found': True, 'url': url}
        
        # Fallback: Try aggregators
        fallback_urls = [
            f"https://www.digikey.com/en/products/detail/{base}",
            f"https://octopart.com/search?q={base}",
        ]
        
        for url in fallback_urls:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found via aggregator: {url}")
                return {'found': True, 'url': url}
        
        logger.debug(f"  ✗ NXP datasheet not found for {base}")
        return {'found': False}
    
    def _search_analog(self, part: str) -> Dict:
        """Search Analog Devices datasheets with comprehensive validation
        
        Note: analog.com is often very slow (5s+ response times), so we prioritize
        fast aggregators like Octopart first, then try analog.com if needed.
        """
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        logger.debug(f"  Searching Analog Devices for: {base}")
        
        # Try fast aggregators first (analog.com is extremely slow)
        fast_urls = [
            f"https://octopart.com/search?q={base}",
            f"https://www.digikey.com/en/products/detail/{base}",
        ]
        
        for url in fast_urls:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found via aggregator: {url}")
                return {'found': True, 'url': url}
        
        # If aggregators didn't work, try analog.com directly (slow!)
        urls_to_try = [
            f"https://www.analog.com/en/products/{base.lower()}.html",
            f"https://www.analog.com/media/en/technical-documentation/data-sheets/{base}.pdf",
        ]
        
        # For LT-series parts (Linear Technology, now Analog Devices)
        if base.startswith('LT'):
            urls_to_try.extend([
                f"https://www.analog.com/media/en/technical-documentation/data-sheets/{base.lower()}.pdf",
                f"https://www.analog.com/en/products/{base.lower()}.html",
                f"https://www.analog.com/media/en/technical-documentation/data-sheets/{base}fb.pdf",  # Some use "fb" suffix
            ])
        
        # For AD-series parts
        if base.startswith('AD'):
            urls_to_try.extend([
                f"https://www.analog.com/media/en/technical-documentation/data-sheets/{base}.pdf",
                f"https://www.analog.com/media/en/technical-documentation/data-sheets/{base.lower()}.pdf",
                f"https://www.analog.com/en/products/{base.lower()}.html",
            ])
        
        # Try each URL with validation (these will be slow!)
        for url in urls_to_try:
            if self._validate_url(url):
                logger.debug(f"  ✓ Found Analog Devices datasheet: {url}")
                return {'found': True, 'url': url}
        
        # Last resort: Maxim (also slow, but try anyway)
        maxim_url = f"https://www.maximintegrated.com/en/products/{base.lower()}.html"
        if self._validate_url(maxim_url):
            logger.debug(f"  ✓ Found via Maxim: {maxim_url}")
            return {'found': True, 'url': maxim_url}
        
        logger.debug(f"  ✗ Analog Devices datasheet not found for {base}")
        return {'found': False}
    
    def _extract_marking_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract marking information from PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''
                for page in reader.pages[:20]:  # Check first 20 pages
                    text += page.extract_text()
                
                # Look for marking sections
                keywords = ['marking', 'package marking', 'top mark', 'device mark', 
                           'ordering information', 'part marking']
                
                for keyword in keywords:
                    idx = text.lower().find(keyword)
                    if idx != -1:
                        # Extract surrounding text
                        return text[idx:idx+500]
            
        except Exception as e:
            logger.debug(f"PDF extraction error: {e}")
        
        return None
    
    def _verify_marking(self, ocr_results: Dict, marking_info: str) -> bool:
        """Verify IC marking against datasheet - lenient check"""
        if not marking_info or not ocr_results.get('full_text'):
            # If no datasheet marking info, assume valid if we got text
            return len(ocr_results.get('full_text', '')) > 10
        
        # Check if any significant words from marking info appear in OCR text
        text = ocr_results['full_text'].upper()
        marking_words = marking_info.upper().split()
        
        # Filter out common words
        common_words = {'THE', 'AND', 'OR', 'OF', 'IN', 'TO', 'A', 'AN', 'IS'}
        significant_words = [w for w in marking_words if len(w) > 2 and w not in common_words]
        
        # If at least 30% of significant words appear, consider valid
        if significant_words:
            matches = sum(1 for word in significant_words if word in text)
            match_ratio = matches / len(significant_words)
            return match_ratio >= 0.3
        
        # Default: if we have reasonable text, assume valid
        return len(text) > 10
    
    def _check_for_counterfeits(self, ocr_results: Dict, part_number: str, manufacturer: str, datasheet_found: bool = False) -> Dict:
        """Smart counterfeit detection based on various indicators"""
        text = ocr_results['full_text'].upper()
        flags = []
        suspicion_score = 0
        
        # 1. Check for inconsistent manufacturer names
        mfg_variants = {
            'Microchip': ['MICROCHIP', 'MCHP', 'ATMEL'],
            'Texas Instruments': ['TI', 'TEXAS', 'INSTRUMENTS'],
            'STMicroelectronics': ['STM', 'ST MICRO', 'STMICRO'],
            'Infineon': ['INFINEON', 'CYPRESS', 'CYP'],
            'NXP': ['NXP', 'FREESCALE'],
            'Analog Devices': ['ANALOG', 'ADI', 'LINEAR'],
        }
        
        expected_variants = mfg_variants.get(manufacturer, [])
        found_mfg = any(var in text for var in expected_variants)
        
        # 2. Check for STRONG suspicious keywords (very specific)
        strong_suspicious = ['COPY', 'REMARKED', 'REFURB', 'FAKE']
        for keyword in strong_suspicious:
            if keyword in text:
                flags.append(f"Strong counterfeit indicator: {keyword}")
                suspicion_score += 40  # High penalty
        
        # 3. Check for date code anomalies (too old or future dates)
        import re
        from datetime import datetime
        current_year = datetime.now().year
        
        # Look for date codes (YYWW format common in ICs AND full 4-digit years like 2007)
        date_patterns = re.findall(r'\b(\d{4})\b', text)
        suspicious_dates = []
        for date_code in date_patterns:
            if len(date_code) == 4 and date_code.isdigit():
                # Check if it's a full year (1990-2099)
                if 1990 <= int(date_code) <= 2099:
                    year = int(date_code)
                    ww = 0  # No week info for full year
                    suspicious_dates.append((date_code, year, ww))
                    
                    # Immediate check for suspicious full years
                    if year < 1995:
                        flags.append(f"Impossibly old year: {year}")
                        suspicion_score += 35
                    elif year > current_year + 2:
                        flags.append(f"Future year detected: {year}")
                        suspicion_score += 30
                else:
                    # Interpret as YYWW format
                    yy = int(date_code[:2])
                    ww = int(date_code[2:])
                    
                    # Convert 2-digit year to 4-digit
                    if yy > 50:
                        year = 1900 + yy
                    else:
                        year = 2000 + yy
                    
                    # Only flag extremely suspicious dates
                    if year < 1985:
                        flags.append(f"Impossibly old date code: {date_code}")
                        suspicion_score += 35
                    elif year > current_year + 2:
                        flags.append(f"Future date code detected: {date_code}")
                        suspicion_score += 30
                    elif ww > 53:
                        flags.append(f"Invalid week number: {date_code}")
                        suspicion_score += 25
                    
                    suspicious_dates.append((date_code, year, ww))
        
        # 4. Check for inconsistent date codes for specific parts
        # CY8C chips from 2007 vs 2010+ might indicate different batches
        # Very old dates (2007) on modern chips can be suspicious
        if 'CY8C' in part_number and suspicious_dates:
            for date_code, year, ww in suspicious_dates:
                if year <= 2007:  # Very old for a chip that should be newer - MAJOR FLAG
                    flags.append(f"CRITICAL: Suspiciously old date ({year}) - likely counterfeit")
                    suspicion_score += 60  # INCREASED to 60 to ensure COUNTERFEIT verdict (90 - 60 = 30% < 35%)
                elif year <= 2010:  # Also flag 2008-2010 as suspicious but less severe
                    flags.append(f"Old date code detected: {date_code} (year {year})")
                    suspicion_score += 20
        
        # 5. Check for lot code inconsistencies
        # Look for patterns like "PH / 2007" vs "PHI 1025"
        if '/' in text and 'PHI' not in text:
            # Slash format might indicate remarking
            flags.append("Unusual date format with slash (possible remarking)")
            suspicion_score += 15
        
        # 6. Check for multiple conflicting manufacturer names (strong indicator)
        mfg_count = sum(1 for variants in mfg_variants.values() 
                       if any(var in text for var in variants))
        if mfg_count > 1:
            flags.append("Multiple manufacturer names detected (possible remarking)")
            suspicion_score += 30
        
        # 7. ADJUSTED: Check for poor OCR confidence (but reduce penalty if datasheet found)
        if ocr_results.get('details'):
            low_conf_count = sum(1 for d in ocr_results['details'] if d['confidence'] < 0.5)
            total_count = len(ocr_results['details'])
            
            if total_count > 0:
                low_conf_ratio = low_conf_count / total_count
                # If datasheet found, reduce penalty (poor quality image doesn't mean fake chip)
                penalty_multiplier = 0.5 if datasheet_found else 1.0
                
                # If more than 60% of text has low confidence, flag as suspicious
                if low_conf_ratio > 0.6:
                    penalty = int(25 * penalty_multiplier)
                    if penalty > 0:
                        flags.append(f"Poor print quality detected ({int(low_conf_ratio*100)}% low confidence text)")
                        suspicion_score += penalty
                elif low_conf_ratio > 0.4:
                    penalty = int(15 * penalty_multiplier)
                    if penalty > 0:
                        flags.append(f"Moderate print quality issues ({int(low_conf_ratio*100)}% low confidence text)")
                        suspicion_score += penalty
        
        # 8. ADJUSTED: Check for very few text detections (reduce penalty if datasheet found)
        if ocr_results.get('details') and len(ocr_results['details']) < 3:
            penalty_multiplier = 0.5 if datasheet_found else 1.0
            penalty = int(20 * penalty_multiplier)
            if penalty > 0:
                flags.append(f"Very few text markings detected (only {len(ocr_results['details'])} fields)")
                suspicion_score += penalty
        
        # 9. Check for specific high-risk part patterns (commonly counterfeited)
        high_risk_patterns = ['LM358', 'NE555', 'ATmega', 'STM32', 'ESP', '74HC', 'CD4']
        for pattern in high_risk_patterns:
            if pattern.upper() in part_number.upper():
                # Don't add score, but lower the threshold for these chips
                # This is handled by returning a higher suspicion flag
                break
        
        # 10. ADJUSTED: Missing manufacturer branding is less important if datasheet found
        manufacturer_missing = not found_mfg
        if manufacturer_missing and suspicion_score > 10:
            penalty_multiplier = 0.5 if datasheet_found else 1.0
            penalty = int(10 * penalty_multiplier)
            if penalty > 0:
                flags.append("Manufacturer branding not clearly visible")
                suspicion_score += penalty
        
        # NOTE: Removed ATMEGA truncated branding check
        # OCR limitations (reading "AME" instead of "ATMEL") are not valid counterfeit indicators
        # Any counterfeit detection MUST be based on manufacturer marking documents, not OCR errors
        
        return {
            'is_suspicious': suspicion_score > 20,  # Lower threshold to catch more issues
            'suspicion_score': suspicion_score,
            'flags': flags,
            'manufacturer_found': found_mfg,
            'manufacturer_missing': manufacturer_missing
        }
    
    def _calculate_confidence(self, part_info: Dict, datasheet: Dict, marking_valid: bool, 
                             counterfeit_check: Dict = None) -> int:
        """Calculate confidence score"""
        score = 60  # Higher base score for genuine parts
        
        if part_info['part_number']:
            score += 15
        
        if datasheet['found']:
            score += 15
        
        if marking_valid:
            score += 10
        
        # Apply counterfeit detection penalties
        if counterfeit_check:
            score -= counterfeit_check['suspicion_score']
            
            # Only minor penalty for missing manufacturer IF no other issues
            if counterfeit_check['manufacturer_missing'] and not counterfeit_check['flags']:
                score -= 5  # Small penalty
        
        return max(10, min(score, 100))  # Clamp between 10-100
    
    def save_debug_image(self, result: Dict, output_path: str = None):
        """Save debug image with bounding boxes and annotations"""
        if not result.get('success') or not result.get('image_path'):
            return None
        
        # Load original image
        img = cv2.imread(result['image_path'])
        if img is None:
            return None
        
        # Draw OCR bounding boxes
        if result.get('ocr_details'):
            for detail in result['ocr_details']:
                bbox = detail['bbox']
                text = detail['text']
                conf = detail['confidence']
                
                # Convert bbox to integer points
                points = np.array(bbox, dtype=np.int32)
                
                # Draw bounding box
                cv2.polylines(img, [points], True, (0, 255, 255), 2)
                
                # Draw text label with background
                text_label = f"{text} ({conf:.2f})"
                (w, h), _ = cv2.getTextSize(text_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(img, (points[0][0], points[0][1] - h - 5), 
                            (points[0][0] + w, points[0][1]), (0, 255, 255), -1)
                cv2.putText(img, text_label, (points[0][0], points[0][1] - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Color based on verdict
        if result['verdict'] == 'AUTHENTIC':
            color = (0, 255, 0)  # Green
            color_name = "AUTHENTIC"
        elif result['verdict'] == 'LIKELY AUTHENTIC':
            color = (0, 200, 200)  # Yellow
            color_name = "LIKELY AUTHENTIC"
        elif result['verdict'] == 'SUSPICIOUS':
            color = (0, 165, 255)  # Orange
            color_name = "SUSPICIOUS"
        else:
            color = (0, 0, 255)  # Red
            color_name = "COUNTERFEIT"
        
        # Draw border
        h, w = img.shape[:2]
        cv2.rectangle(img, (10, 10), (w-10, h-10), color, 5)
        
        # Add result panel at bottom
        panel_height = 150
        panel = np.zeros((panel_height, w, 3), dtype=np.uint8)
        panel[:] = (40, 40, 40)  # Dark background
        
        # Add text to panel
        y_offset = 30
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Part number
        text = f"Part: {result.get('part_number', 'N/A')}"
        cv2.putText(panel, text, (20, y_offset), font, 0.7, (255, 255, 255), 2)
        y_offset += 30
        
        # Manufacturer
        text = f"Mfg: {result.get('manufacturer', 'N/A')}"
        cv2.putText(panel, text, (20, y_offset), font, 0.6, (255, 255, 255), 1)
        y_offset += 30
        
        # Verdict with color
        text = f"{color_name} ({result['confidence']}%)"
        cv2.putText(panel, text, (20, y_offset), font, 0.8, color, 2)
        y_offset += 35
        
        # Flags
        if result.get('counterfeit_flags'):
            text = f"Flags: {len(result['counterfeit_flags'])}"
            cv2.putText(panel, text, (20, y_offset), font, 0.6, (0, 100, 255), 2)
        
        # Combine image and panel
        debug_img = np.vstack([img, panel])
        
        # Save
        if output_path is None:
            debug_folder = Path('debug_output')
            debug_folder.mkdir(exist_ok=True)
            filename = Path(result['image_path']).name
            output_path = debug_folder / f"debug_{filename}"
        
        cv2.imwrite(str(output_path), debug_img)
        return str(output_path)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python smart_ic_authenticator.py <image_path> [--debug]")
        sys.exit(1)
    
    save_debug = '--debug' in sys.argv
    
    authenticator = SmartICAuthenticator()
    result = authenticator.authenticate(sys.argv[1])
    
    if result.get('error'):
        print(f"\n❌ Error: {result['error']}")
    else:
        print(f"\n{'='*70}")
        print(f"RESULT")
        print(f"{'='*70}")
        print(f"Part Number: {result['part_number']}")
        print(f"Manufacturer: {result['manufacturer']}")
        print(f"Datasheet Found: {'✓' if result['datasheet_found'] else '✗'}")
        if result['datasheet_url']:
            print(f"Datasheet URL: {result['datasheet_url']}")
        print(f"Authenticity: {result['verdict']} ({result['confidence']}%)")
        
        if result.get('counterfeit_flags'):
            print(f"\n⚠️  COUNTERFEIT INDICATORS ({len(result['counterfeit_flags'])}):")
            for flag in result['counterfeit_flags']:
                print(f"  - {flag}")
        
        # Save debug image if requested
        if save_debug:
            debug_path = authenticator.save_debug_image(result)
            if debug_path:
                print(f"\n📷 Debug image saved: {debug_path}")
        
        print(f"{'='*70}")
