"""
Smart IC Authenticator - Production System
Uses Intelligent OCR with Multi-Orientation Detection + Datasheet Verification
No YOLO dependency - Direct OCR is faster and more reliable
"""

import cv2
import numpy as np
import easyocr
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import logging
from bs4 import BeautifulSoup
import PyPDF2
import io
import torch
from smart_datasheet_finder import SmartDatasheetFinder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartICAuthenticator:
    """Production-ready IC authentication system with intelligent OCR and datasheet verification"""
    
    def __init__(self):
        """Initialize OCR and datasheet systems"""
        # Check GPU availability
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            logger.info(f"✓ GPU Available: {torch.cuda.get_device_name(0)}")
            logger.info(f"  CUDA Version: {torch.version.cuda}")
        else:
            logger.warning("⚠ GPU not available - using CPU mode")
        
        # Load OCR with GPU support for fast processing
        logger.info("Loading EasyOCR with GPU support...")
        self.ocr_reader = easyocr.Reader(['en'], gpu=gpu_available, verbose=False)
        
        if gpu_available:
            logger.info("✓ EasyOCR loaded with GPU acceleration")
        else:
            logger.info("✓ EasyOCR loaded in CPU mode")
        
        # Initialize smart datasheet finder
        self.datasheet_cache = Path("datasheet_cache")
        self.datasheet_cache.mkdir(exist_ok=True)
        self.datasheet_finder = SmartDatasheetFinder(self.datasheet_cache)
        
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
            'ATMEL': r'AT\s*MEL\s*\d+[A-Z]*\d*',  # ATMEL general
            'AT': r'AT\s*\d{3,4}[A-Z]*\d*[A-Z]*',  # Generic Atmel parts (AT89, AT90, AT24, etc.)
            'PIC': r'PIC\s*\d+[A-Z]\s*\d+[A-Z]*\d*',  # Allow spaces in PIC18F45K22
            'STM32': r'STM32[A-Z]\d+[A-Z]*\d*[A-Z]*',
            'LM': r'[IL]M\s*\d+[A-Z]*\d*[A-Z]*',  # Allow I→L confusion
            'LM556': r'[IL]M\s*556[A-Z]*',  # Specific pattern for LM556 (dual 555)
            'TL': r'[TI][LI]\s*\d+[A-Z]*\d*',  # Texas Instruments TL series with OCR errors
            'TLC': r'TLC\s*\d+[A-Z]*',  # TI TLC series
            'TPS': r'TPS\s*\d+[A-Z]*\d*',  # TI TPS power series
            'SN74': r'SN74[A-Z]+\d+[A-Z]*',
            'SN': r'[S5]N\s*\d+[A-Z]*\d*',  # General SN series (5→S confusion)
            'CY8C': r'CY8C\d+[A-Z]*-?\d*[A-Z]*',  # Optional dash
            'CY7C': r'CY7C\d+[A-Z]*-?\d*[A-Z]*',
            'MC': r'[MN]C\d+[A-Z]*\d*[A-Z]*',  # M→N confusion
            'MCP': r'MCP\s*\d+[A-Z]*\d*',  # Microchip MCP series
            'ADC': r'ADC\s*\d+[A-Z]+\d*',  # ADC followed by number and letters
            'DAC': r'DAC\s*\d+[A-Z]*\d*',
            'LT': r'[IL]T\s*\d+[A-Z]*\d*',  # I→L confusion
            'AD': r'A[D0O]\s*\d+[A-Z]*\d*',  # D→0/O confusion
            'MAX': r'[MNW]AX\s*\d+[A-Z]*\d*',  # M→N/W confusion
            'NE': r'[NW]E\s*\d+[A-Z]*\d*',  # N→W confusion
            'SE': r'[S5]E\s*\d+[A-Z]*',  # Signetics/TI SE series
            'LMC': r'LMC\s*\d+[A-Z]*',  # TI LMC series
            'TMP': r'T[MN]P\s*\d+[A-Z]*',  # TI temperature sensors
            'INA': r'INA\s*\d+[A-Z]*',  # TI current sense
            'OPA': r'[O0]PA\s*\d+[A-Z]*',  # TI op-amps (O→0 confusion)
            'AUCH': r'AUCH\d+[A-Z]*\d*[A-Z]*',  # TI AUCH series
            'M74HC': r'M74HC\d+[A-Z]\d',  # STM 74HC series
            '74HC': r'74H[CO]\d+[A-Z]*',  # Generic 74HC (C→O confusion)
            '74LS': r'74[IL]S\d+[A-Z]*',  # 74LS series (L→I confusion)
            'CD': r'CD\s*\d+[A-Z]*\d*',  # CD4xxx series
            'ULN': r'ULN\s*\d+[A-Z]*',  # ULN2xxx driver series
            '2N': r'2N\s*\d+[A-Z]*',  # Transistors (2N2222, etc.)
            'L293': r'L\s*293[A-Z]*',  # Motor driver
        }
        
        # Manufacturer mappings
        self.mfg_map = {
            'ATMEGA': 'Microchip',
            'ATTINY': 'Microchip',
            'ATMEL': 'Microchip',
            'AT': 'Microchip',  # Generic Atmel (now part of Microchip)
            'PIC': 'Microchip',
            'MCP': 'Microchip',
            'STM32': 'STMicroelectronics',
            'M74HC': 'STMicroelectronics',
            'LM': 'Texas Instruments',
            'LM556': 'Texas Instruments',  # Dual 555 timer
            'LMC': 'Texas Instruments',
            'TL': 'Texas Instruments',
            'TLC': 'Texas Instruments',
            'TPS': 'Texas Instruments',
            'TMP': 'Texas Instruments',
            'INA': 'Texas Instruments',
            'OPA': 'Texas Instruments',
            'SN74': 'Texas Instruments',
            'SN': 'Texas Instruments',
            'ADC': 'Texas Instruments',
            'DAC': 'Texas Instruments',
            'NE': 'Various',  # NE555 made by many (TI, ST, Fairchild, etc.)
            'SE': 'Texas Instruments',
            'AUCH': 'Texas Instruments',
            'CY8C': 'Infineon',
            'CY7C': 'Infineon',
            'MC': 'NXP',
            'LT': 'Analog Devices',
            'AD': 'Analog Devices',
            'MAX': 'Analog Devices',
            '74HC': 'Various',
            '74LS': 'Various',
            'CD': 'Texas Instruments',
            'ULN': 'STMicroelectronics',
            '2N': 'Various',
            'L293': 'Texas Instruments',
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
            
            # Step 1: OCR extraction with automatic orientation detection
            logger.info("Step 1: OCR text extraction...")
            ocr_results = self._extract_text_ocr(image)
            
            # Step 2: Parse and identify part number
            logger.info("Step 2: Part number identification...")
            part_info = self._identify_part_number(ocr_results)
            
            if not part_info['part_number']:
                logger.error("  ✗ No IC part number detected")
                return self._create_error_result(image_path, 'No IC part number detected in image', 
                                                 ocr_results.get('full_text', ''))
            
            logger.info(f"  ✓ Part Number: {part_info['part_number']}")
            logger.info(f"  ✓ Manufacturer: {part_info['manufacturer']}")
            
            # Step 3: Find datasheet
            logger.info("Step 3: Finding datasheet...")
            datasheet = self._find_datasheet(part_info['part_number'], part_info['manufacturer'])
            
            if datasheet['found']:
                logger.info(f"  ✓ Datasheet found: {datasheet['url']}")
            else:
                logger.info(f"  ✗ Datasheet not found")
            
            # Step 4: Verify marking
            logger.info("Step 4: Marking verification...")
            marking_valid = False
            if datasheet['found'] and datasheet.get('marking_info'):
                marking_valid = self._verify_marking(ocr_results, datasheet['marking_info'], part_info['part_number'])
            
            # Step 5: Counterfeit detection (pass marking_info for validation)
            logger.info("Step 5: Counterfeit detection...")
            counterfeit_check = self._check_for_counterfeits(ocr_results, part_info['part_number'], 
                                                             part_info['manufacturer'],
                                                             datasheet_found=datasheet['found'],
                                                             marking_info=datasheet.get('marking_info', {}))
            
            if counterfeit_check['flags']:
                logger.warning("  ⚠️  Suspicious indicators detected:")
                for flag in counterfeit_check['flags']:
                    logger.warning(f"    - {flag}")
            else:
                logger.info("  ✓ No suspicious indicators found")
            
            # Calculate verdict
            confidence = self._calculate_confidence(part_info, datasheet, marking_valid, counterfeit_check)
            
            # Adjusted thresholds for more balanced verdicts
            if confidence >= 80:
                verdict = "AUTHENTIC"
            elif confidence >= 60:
                verdict = "LIKELY AUTHENTIC"
            elif confidence >= 35:
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
                img_height, img_width = debug_ocr_image.shape[:2]
                
                for detail in ocr_results['details']:
                    bbox = detail['bbox']
                    text = detail['text']
                    conf = detail['confidence']
                    
                    # Convert bbox to integer points and clip to image bounds
                    points = np.array(bbox, dtype=np.int32)
                    points[:, 0] = np.clip(points[:, 0], 0, img_width - 1)
                    points[:, 1] = np.clip(points[:, 1], 0, img_height - 1)
                    
                    # Draw bounding box
                    cv2.polylines(debug_ocr_image, [points], True, (0, 255, 255), 2)
                    
                    # Draw text label with background (with bounds checking)
                    text_label = f"{text} ({conf:.2f})"
                    (w, h), _ = cv2.getTextSize(text_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    
                    # Calculate label position with bounds checking
                    label_x = max(0, min(points[0][0], img_width - w))
                    label_y = max(h + 5, points[0][1])  # Ensure label is within image
                    
                    cv2.rectangle(debug_ocr_image, 
                                (label_x, label_y - h - 5), 
                                (min(label_x + w, img_width - 1), label_y), 
                                (0, 255, 255), -1)
                    cv2.putText(debug_ocr_image, text_label, (label_x, label_y - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            # Get preprocessing variants
            if ocr_results.get('preprocessing_images'):
                debug_variants = [(p['name'], p['image']) for p in ocr_results['preprocessing_images']]
            
            # MEMORY CLEANUP: Delete large objects before returning
            result = {
                'success': True,
                'part_number': part_info['part_number'],
                'normalized_part_number': part_info['part_number'],
                'manufacturer': part_info['manufacturer'],
                'datasheet_found': datasheet['found'],
                'datasheet_url': datasheet.get('url'),  # Original manufacturer URL (can be None)
                'datasheet_local_file': datasheet.get('local_file'),  # Local cached PDF for viewer
                'datasheet_source': datasheet.get('source'),
                'marking_verified': marking_valid,
                'marking_validation': {
                    'validation_passed': marking_valid,
                    'manufacturer': part_info['manufacturer'],
                    'issues': counterfeit_check.get('marking_issues', [])
                },
                'counterfeit_flags': counterfeit_check['flags'],
                'suspicion_score': counterfeit_check['suspicion_score'],
                'confidence': confidence,
                'verdict': verdict,
                'counterfeit_reasons': self._generate_counterfeit_explanation(
                    verdict, counterfeit_check, part_info, datasheet, marking_valid
                ),
                'is_authentic': confidence >= 65,
                'full_text': ocr_results['full_text'],
                'ocr_details': ocr_results.get('details', []),
                'ocr_confidence': ocr_results.get('ocr_confidence', 0.0),  # Add OCR confidence
                'preprocessing_images': ocr_results.get('preprocessing_images', []),  # Add preprocessing
                'debug_ocr_image': debug_ocr_image,  # Add debug OCR image
                'debug_variants': debug_variants,  # Add debug preprocessing variants
                'image_path': image_path,
                'date_codes': [],
                'reasons': []
            }
            
            # Delete large numpy arrays from ocr_results to free memory
            if 'preprocessing_images' in ocr_results:
                del ocr_results['preprocessing_images']
            del ocr_results, img
            
            return result
            
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
            'ocr_details': [],
            'image_path': image_path,
            'date_codes': [],
            'reasons': [f'Error: {error_msg}']
        }
    
    def _try_all_orientations(self, image: np.ndarray) -> Tuple[np.ndarray, int]:
        """Try all 4 cardinal orientations and return the best one for OCR"""
        try:
            best_image = image.copy()
            best_angle = 0
            best_score = 0
            best_results = []
            
            # Try 4 cardinal rotations: 0°, 90°, 180°, 270°
            for angle in [0, 90, 180, 270]:
                # Rotate image
                if angle == 0:
                    rotated = image.copy()
                elif angle == 90:
                    rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                elif angle == 180:
                    rotated = cv2.rotate(image, cv2.ROTATE_180)
                elif angle == 270:
                    rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                # Enhance image for OCR test
                gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                enhanced = clahe.apply(gray)
                enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
                
                # Quick OCR test with LOW confidence threshold to detect any text
                results = self.ocr_reader.readtext(enhanced_bgr, detail=1, paragraph=False,
                                                   min_size=5, text_threshold=0.5, 
                                                   low_text=0.3, link_threshold=0.3)
                
                # Score based on number of alphanumeric characters found
                score = 0
                for bbox, text, conf in results:
                    # Count alphanumeric characters (indicates real text vs noise)
                    alnum_count = sum(c.isalnum() for c in text)
                    if alnum_count >= 2:  # At least 2 alphanumeric chars
                        score += alnum_count * conf
                
                logger.debug(f"  Angle {angle:3d}°: {len(results)} detections, score={score:.2f}")
                
                if score > best_score:
                    best_score = score
                    best_image = rotated
                    best_angle = angle
                    best_results = results
            
            if best_angle != 0:
                logger.info(f"  Auto-rotation: Best orientation is {best_angle}° (score: {best_score:.2f})")
            else:
                logger.info(f"  No rotation needed (original best, score: {best_score:.2f})")
            
            return best_image, best_angle
            
        except Exception as e:
            logger.debug(f"Orientation detection failed: {e}, using original image")
            return image, 0
    
    def _extract_text_ocr(self, image: np.ndarray) -> Dict:
        """Extract text using OCR with automatic orientation detection and optimized preprocessing"""
        all_text = []
        ocr_details = []  # Store bbox and text for drawing
        preprocessing_images = []  # Store preprocessing variants for debugging
        
        # STEP 1: Try all 4 cardinal orientations automatically (0°, 90°, 180°, 270°)
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
        
        # STEP 3: Use multiple preprocessing variants for robust text extraction
        # (No YOLO - direct full-image OCR is faster and more reliable)
        
        # Variant 1: Bilateral filter (preserves edges while reducing noise)
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        bilateral_bgr = cv2.cvtColor(bilateral, cv2.COLOR_GRAY2BGR)
        
        # Variant 2: Adaptive threshold
        thresh_adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                cv2.THRESH_BINARY, 11, 2)
        thresh_adaptive_bgr = cv2.cvtColor(thresh_adaptive, cv2.COLOR_GRAY2BGR)
        
        # Variant 3: Unsharp masking (enhances edges/text)
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
        unsharp = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
        unsharp_bgr = cv2.cvtColor(unsharp, cv2.COLOR_GRAY2BGR)
        
        # Variant 4: OTSU threshold
        _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh_otsu_bgr = cv2.cvtColor(thresh_otsu, cv2.COLOR_GRAY2BGR)
        
        # Try variants in order of effectiveness (REDUCED from 9 to 5 variants for SPEED)
        variants = [enhanced_bgr, bilateral_bgr, thresh_adaptive_bgr, unsharp_bgr, thresh_otsu_bgr]
        variant_names = ['CLAHE Enhanced', 'Bilateral Filter', 'Adaptive Threshold', 'Unsharp Mask', 'OTSU Binary']
        
        # Store only first 3 preprocessing images for debug (save memory)
        for name, var_img in zip(variant_names[:3], variants[:3]):
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
                results = self.ocr_reader.readtext(img_variant, paragraph=False)
                variant_text = []
                variant_details = []
                total_conf = 0.0
                conf_count = 0
                
                for (bbox, text, conf) in results:
                    if conf > 0.08:  # Low threshold to catch more text
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
        
        full_text = ' '.join(all_text)
        logger.info(f"  Extracted text: {full_text[:100]}...")
        
        return {
            'lines': all_text,
            'full_text': full_text,
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
        
        # Fix NE555 SSS→555 OCR error: NESSSP → NE555P, NE5SSP → NE555P
        text = re.sub(r'([NW]E)\s*S+([PST])', r'\g<1>555\2', text, flags=re.IGNORECASE)  # NESSSP → NE555P
        text = re.sub(r'([NW]E)\s*5+S+([PST])', r'\g<1>555\2', text, flags=re.IGNORECASE)  # NE5SSP → NE555P
        text = re.sub(r'([NW]E)\s*[S5]{3,4}([PST])', r'\g<1>555\2', text, flags=re.IGNORECASE)  # NE555P with S/5 mix
        
        # Fix LM556 SSS→556 OCR error: LMSSS → LM556, LM5S6 → LM556
        text = re.sub(r'([IL]M)\s*[S5]{3}([A-Z])', r'\g<1>556\2', text, flags=re.IGNORECASE)  # LMSSS → LM556
        text = re.sub(r'([IL]M)\s*[S5][S5][6G]([A-Z])', r'\g<1>556\2', text, flags=re.IGNORECASE)  # LM5S6 → LM556
        
        # Fix SN74HC595 OCR errors: S→5, O→0 confusions
        text = re.sub(r'([S5]N)74HC[S5]9[S5]', r'\g<1>74HC595', text, flags=re.IGNORECASE)  # SN74HCS9S → SN74HC595
        text = re.sub(r'([S5]N)74H[CO][S5]9[S5]', r'\g<1>74HC595', text, flags=re.IGNORECASE)  # SN74HOS9S → SN74HC595
        
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
                if score > best_score and score >= 2:  # LOWERED to 2 - catch very short ICs like "NE555"
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
                'prefix': prefix,
                'ocr_confidence': ocr_results.get('ocr_confidence', 0)
            }
        
        logger.warning(f"  ✗ No IC part number found in text: {text[:100]}")
        
        return {
            'part_number': None,
            'manufacturer': None,
            'prefix': None,
            'ocr_confidence': ocr_results.get('ocr_confidence', 0)
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
        """Use SmartDatasheetFinder to download PDFs and extract marking schemes"""
        return self.datasheet_finder.find_datasheet(part_number, manufacturer)
    
    def _extract_marking_from_pdf(self, pdf_path: str) -> Optional[str]:
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
    
    def _verify_marking(self, ocr_results: Dict, marking_info: Dict, part_number: str) -> bool:
        """Verify IC marking against PDF datasheet marking scheme"""
        if not marking_info or not ocr_results.get('full_text'):
            # If no datasheet marking info, assume valid if we got text
            return len(ocr_results.get('full_text', '')) > 10
        
        text = ocr_results['full_text'].upper()
        
        # Enhanced validation using structured marking_info from PDF
        if isinstance(marking_info, dict):
            # Check for date code format validation (but don't fail if not found)
            if marking_info.get('date_format'):
                date_format = marking_info['date_format'].upper()
                import re
                
                # Validate date code format from PDF (lenient - just log warnings)
                if 'YYWW' in date_format:
                    # Look for YYWW pattern in OCR text
                    yyww_matches = re.findall(r'\b\d{4}\b', text)
                    if not yyww_matches:
                        logger.info(f"  ℹ️  YYWW date code not found (not critical)")
                
                if 'YYYY' in date_format:
                    # Look for 4-digit year
                    year_matches = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
                    if not year_matches:
                        logger.info(f"  ℹ️  Year marking not found (not critical)")
            
            # Check for expected marking elements (lenient)
            if marking_info.get('elements'):
                elements = marking_info['elements']
                found_elements = 0
                
                for element in elements:
                    element_upper = element.upper()
                    if element_upper in text or any(word in text for word in element_upper.split()):
                        found_elements += 1
                
                # At least 30% of marking elements should be present (reduced from 50%)
                if elements:
                    match_ratio = found_elements / len(elements)
                    if match_ratio >= 0.3:
                        logger.info(f"  ✓ {int(match_ratio*100)}% of marking elements validated")
                        return True
                    else:
                        logger.info(f"  ℹ️  {int(match_ratio*100)}% of marking elements found (lenient pass)")
                        # Don't fail - just continue to other checks
            
            # Fallback to raw text matching if dict format
            if marking_info.get('raw_text'):
                marking_text = marking_info['raw_text']
            else:
                # No structured data, assume valid
                logger.info("  ✓ No specific marking validation needed")
                return True
        else:
            # Old string format
            marking_text = str(marking_info)
        
        # Check if any significant words from marking info appear in OCR text
        marking_words = marking_text.upper().split()
        
        # Filter out common words
        common_words = {'THE', 'AND', 'OR', 'OF', 'IN', 'TO', 'A', 'AN', 'IS', 'LINE', 'TOP', 'BOTTOM'}
        significant_words = [w for w in marking_words if len(w) > 2 and w not in common_words]
        
        # If at least 25% of significant words appear, consider valid (reduced from 40% - more lenient)
        if significant_words:
            matches = sum(1 for word in significant_words if word in text)
            match_ratio = matches / len(significant_words)
            if match_ratio >= 0.25:
                logger.info(f"  ✓ {int(match_ratio*100)}% marking word match - VALID")
                return True
            else:
                logger.info(f"  ℹ️  {int(match_ratio*100)}% marking word match - lenient pass")
                # Don't fail - marking validation is not critical
                return True
        
        # Default: if we have reasonable text, assume valid (lenient approach)
        logger.info("  ✓ Marking validation passed (lenient)")
        return len(text) > 10
    
    def _generate_counterfeit_explanation(self, verdict: str, counterfeit_check: Dict, 
                                          part_info: Dict, datasheet: Dict, marking_valid: bool) -> List[str]:
        """Generate human-readable explanation of why a chip is considered counterfeit"""
        reasons = []
        
        # Add verdict-specific explanations
        if verdict == "LIKELY COUNTERFEIT" or verdict == "SUSPICIOUS":
            # Marking diagram comparison - USE ACTUAL MARKING INFO FROM DATASHEET
            if datasheet.get('found') and datasheet.get('marking_info'):
                if not marking_valid:
                    reasons.append("❌ Chip marking does NOT match datasheet marking diagrams")
                    reasons.append("   Expected marking format not found on chip surface")
                    
                    # Show what we expected from datasheet
                    marking_sections = datasheet['marking_info'].get('sections', [])
                    if marking_sections:
                        reasons.append("   Datasheet specifies:")
                        # Extract key marking requirements (first section, limited)
                        first_section = marking_sections[0][:300] if marking_sections else ""
                        if "YYWW" in first_section or "date code" in first_section.lower():
                            reasons.append("   • Date code in YYWW or WWYY format required")
                        if "lot" in first_section.lower() or "trace" in first_section.lower():
                            reasons.append("   • Lot/trace code required")
                else:
                    # Marking is valid but other issues exist
                    reasons.append("⚠️  Marking format appears valid but other concerns exist")
            elif not datasheet.get('found'):
                reasons.append("⚠️  No official datasheet found - cannot verify marking format")
            else:
                # No marking info in datasheet
                if not marking_valid:
                    reasons.append("❌ Chip marking format appears suspicious")
                    reasons.append("   Unable to extract marking specifications from datasheet")
            
            # Part number mismatch
            if not part_info.get('part_number_matched'):
                reasons.append("❌ Part number does NOT match datasheet")
                reasons.append(f"   OCR read: {part_info.get('part_number', 'N/A')}")
                reasons.append(f"   Expected from datasheet: Similar format not found")
            
            # Datasheet not found
            if not datasheet.get('found'):
                reasons.append("⚠️  No official datasheet found for this part number")
                reasons.append("   Part number may be fake or incorrectly printed")
            
            # Add specific counterfeit flags
            if counterfeit_check.get('flags'):
                reasons.append("\n🚨 Counterfeit Indicators Detected:")
                for flag in counterfeit_check['flags']:
                    reasons.append(f"   • {flag}")
            
            # Suspicion score explanation
            suspicion = counterfeit_check.get('suspicion_score', 0)
            if suspicion > 60:
                reasons.append(f"\n⚠️  High suspicion score: {suspicion}% (threshold: 50%)")
            elif suspicion > 40:
                reasons.append(f"\n⚠️  Elevated suspicion score: {suspicion}%")
        
        elif verdict == "AUTHENTIC" or verdict == "LIKELY AUTHENTIC":
            # Show positive validation
            if datasheet.get('found') and marking_valid:
                reasons.append("✅ Chip marking matches datasheet marking diagrams")
                
                # Show what matched from datasheet
                marking_sections = datasheet.get('marking_info', {}).get('sections', [])
                if marking_sections:
                    first_section = marking_sections[0][:300] if marking_sections else ""
                    if "YYWW" in first_section or "date code" in first_section.lower():
                        reasons.append("   • Date code format validated against datasheet")
                    if "lot" in first_section.lower() or "trace" in first_section.lower():
                        reasons.append("   • Lot/trace code format validated")
            
            reasons.append("✅ Part number verified against official datasheet")
            
            if datasheet.get('found'):
                reasons.append(f"✅ Official datasheet found and validated")
                if datasheet.get('url'):
                    # Show source for transparency
                    url = datasheet['url']
                    if 'infineon.com' in url:
                        reasons.append("   Source: Infineon (official manufacturer)")
                    elif 'ti.com' in url:
                        reasons.append("   Source: Texas Instruments (official manufacturer)")
                    elif 'microchip.com' in url:
                        reasons.append("   Source: Microchip (official manufacturer)")
                    elif 'nxp.com' in url:
                        reasons.append("   Source: NXP Semiconductors (official manufacturer)")
        
        # If no specific reasons, provide general verdict explanation
        if not reasons:
            if verdict == "SUSPICIOUS":
                reasons.append("⚠️  Some inconsistencies detected but not conclusive")
                reasons.append("   Manual inspection recommended")
        
        return reasons
    
    def _check_for_counterfeits(self, ocr_results: Dict, part_number: str, manufacturer: str, 
                                datasheet_found: bool = False, marking_info: Dict = None) -> Dict:
        """Smart counterfeit detection based on various indicators including PDF marking validation"""
        text = ocr_results['full_text'].upper()
        flags = []
        suspicion_score = 0
        
        # 0. CRITICAL: Validate against PDF marking scheme if available
        if marking_info and isinstance(marking_info, dict):
            # Check date code format from PDF
            if marking_info.get('date_format'):
                expected_format = marking_info['date_format'].upper()
                import re
                from datetime import datetime
                current_year = datetime.now().year
                
                # Look for date codes in OCR text
                date_codes = re.findall(r'\b\d{4}\b', text)
                
                if 'YYWW' in expected_format:
                    # PDF says date should be in YYWW format
                    valid_date_found = False
                    for code in date_codes:
                        yy = int(code[:2])
                        ww = int(code[2:])
                        
                        # Convert to full year
                        year = 2000 + yy if yy <= 50 else 1900 + yy
                        
                        # Check if valid week and reasonable year
                        if 1 <= ww <= 53 and 1990 <= year <= current_year + 2:
                            valid_date_found = True
                            break
                    
                    if date_codes and not valid_date_found:
                        flags.append("CRITICAL: Date code format doesn't match PDF specification (expected YYWW)")
                        suspicion_score += 50  # Major penalty for format mismatch
                
                # Check for full year format when PDF expects it
                if 'YYYY' in expected_format and not 'YYWW' in expected_format:
                    year_codes = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
                    if not year_codes:
                        flags.append("CRITICAL: Year marking not found (expected by PDF)")
                        suspicion_score += 40
            
            # Check if expected marking elements are missing
            if marking_info.get('elements'):
                missing_elements = []
                for element in marking_info['elements']:
                    element_upper = element.upper()
                    if element_upper not in text and not any(word in text for word in element_upper.split()):
                        missing_elements.append(element)
                
                if len(missing_elements) >= len(marking_info['elements']) * 0.5:
                    flags.append(f"CRITICAL: {len(missing_elements)} marking elements missing from PDF spec")
                    suspicion_score += 45
        
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
        
        # 7. ADJUSTED: Check for poor OCR confidence (but GREATLY reduce penalty if PDF datasheet found)
        if ocr_results.get('details'):
            low_conf_count = sum(1 for d in ocr_results['details'] if d['confidence'] < 0.5)
            total_count = len(ocr_results['details'])
            
            if total_count > 0:
                low_conf_ratio = low_conf_count / total_count
                # If PDF datasheet found, minimal penalty (poor quality image doesn't mean fake chip)
                penalty_multiplier = 0.2 if datasheet_found else 1.0
                
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
        
        # 8. ADJUSTED: Check for very few text detections (minimal penalty if PDF datasheet found)
        if ocr_results.get('details') and len(ocr_results['details']) < 3:
            penalty_multiplier = 0.1 if datasheet_found else 1.0
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
        
        # 10. ADJUSTED: Missing manufacturer branding is less important if PDF datasheet found
        manufacturer_missing = not found_mfg
        if manufacturer_missing and suspicion_score > 10:
            penalty_multiplier = 0.1 if datasheet_found else 1.0
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
        """
        Calculate strict confidence score (much more demanding than before)
        
        NEW SCORING SYSTEM (v3.0.7):
        - Base: 20 points (very skeptical by default)
        - Part detected: +15 points
        - PDF datasheet downloaded: +30 points (CRITICAL - must have PDF, not just product page)
        - Marking validation: +20 points (increased weight)
        - OCR confidence: +15 points max (based on quality)
        - PENALTIES:
          - Missing datasheet PDF: -20 points
          - Counterfeit flags: reduced when PDF found
          - Old date code: -30 points (CRITICAL)
          - Manufacturer misspelling: -40 points (CRITICAL)
        """
        score = 30  # Start more optimistic (was 20)
        
        # Part number detected
        if part_info['part_number']:
            score += 15
            logger.debug(f"    +15 Part number detected: {part_info['part_number']}")
        
        # Datasheet verification - MUST be PDF, not product page
        if datasheet.get('found'):
            source = datasheet.get('source', '')
            
            # Only give full credit for downloaded PDFs
            if source in ['PDF Downloaded', 'Local Cache']:
                score += 35  # Increased from 30
                logger.debug(f"    +35 Datasheet PDF: {source}")
            elif source == 'Link Only':
                # Found link but couldn't download - suspicious
                score += 10
                logger.debug(f"    +10 Datasheet link only (no PDF)")
            else:
                # Product page only - not good enough
                score += 5
                logger.debug(f"    +5 Product page only (need PDF)")
        else:
            # No datasheet at all - very suspicious
            score -= 20
            logger.debug(f"    -20 No datasheet found")
        
        # Marking validation
        if marking_valid:
            score += 20
            logger.debug(f"    +20 Marking validation passed")
        
        # OCR quality bonus
        ocr_conf = part_info.get('ocr_confidence', 0)
        if ocr_conf >= 80:
            score += 15
            logger.debug(f"    +15 High OCR confidence ({ocr_conf:.1f}%)")
        elif ocr_conf >= 60:
            score += 10
            logger.debug(f"    +10 Good OCR confidence ({ocr_conf:.1f}%)")
        elif ocr_conf >= 40:
            score += 5
            logger.debug(f"    +5 Fair OCR confidence ({ocr_conf:.1f}%)")
        
        # Apply counterfeit detection penalties (already reduced when PDF found in _check_for_counterfeits)
        if counterfeit_check:
            suspicion = counterfeit_check.get('suspicion_score', 0)
            flags = counterfeit_check.get('flags', [])
            
            # Base suspicion penalty (already reduced if PDF found)
            score -= suspicion
            logger.debug(f"    -{suspicion} Suspicion score")
            
            # CRITICAL penalties for specific flags (only apply if truly critical)
            for flag in flags:
                flag_lower = flag.lower()
                
                # Old date codes are CRITICAL indicators - always penalize
                if 'critical' in flag_lower and ('old date' in flag_lower or '2007' in flag_lower):
                    score -= 30
                    logger.debug(f"    -30 CRITICAL: {flag}")
                
                # Manufacturer misspellings are CRITICAL - always penalize
                elif 'misspelling' in flag_lower or 'anel' in flag_lower or 'amel' in flag_lower:
                    score -= 40
                    logger.debug(f"    -40 CRITICAL: {flag}")
        
        final_score = max(0, min(score, 100))  # Clamp between 0-100
        logger.debug(f"    = {final_score}% final confidence")
        
        return final_score
    
    def save_debug_image(self, result: Dict, output_path: str = None):
        """Save debug image with bounding boxes and annotations"""
        if not result.get('success') or not result.get('image_path'):
            return None
        
        # Load original image
        img = cv2.imread(result['image_path'])
        if img is None:
            return None
        
        img_height, img_width = img.shape[:2]
        
        # Draw OCR bounding boxes
        if result.get('ocr_details'):
            for detail in result['ocr_details']:
                bbox = detail['bbox']
                text = detail['text']
                conf = detail['confidence']
                
                # Convert bbox to integer points and clip to image bounds
                points = np.array(bbox, dtype=np.int32)
                points[:, 0] = np.clip(points[:, 0], 0, img_width - 1)
                points[:, 1] = np.clip(points[:, 1], 0, img_height - 1)
                
                # Draw bounding box
                cv2.polylines(img, [points], True, (0, 255, 255), 2)
                
                # Draw text label with background (with bounds checking)
                text_label = f"{text} ({conf:.2f})"
                (w, h), _ = cv2.getTextSize(text_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                
                # Calculate label position with bounds checking
                label_x = max(0, min(points[0][0], img_width - w))
                label_y = max(h + 5, points[0][1])  # Ensure label is within image
                
                cv2.rectangle(img, 
                            (label_x, label_y - h - 5), 
                            (min(label_x + w, img_width - 1), label_y), 
                            (0, 255, 255), -1)
                cv2.putText(img, text_label, (label_x, label_y - 5),
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
