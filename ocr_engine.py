"""
OCR Engine Module - YOLO-OCR Integration for IC Authentication UI
Research-based IC text extraction using YOLO detection + Multi-engine OCR

Based on research papers:
- Harrison: Automated Laser Marking Analysis for Counterfeit IC Identification  
- IEEE ISTFA 2021: Logo Classification and Data Augmentation for PCB Assurance
- IEEE IPFA 2021: IC SynthLogo Dataset for Counterfeit Detection
- Deep Learning AOI System for Component Marks Detection
"""

import cv2
import numpy as np
import re
from typing import List, Dict, Any, Optional
import warnings
import os
import sys

# Import our advanced YOLO-OCR system
try:
    from simplified_yolo_ocr import SimplifiedYOLOOCR
    from ic_marking_extractor import ICMarkingExtractor
    YOLO_OCR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  YOLO-OCR not available: {e}")
    YOLO_OCR_AVAILABLE = False

# Suppress warnings for clean UI output
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class OCREngine:
    """
    Production-grade OCR engine using YOLO-based text detection
    Implements research-based approaches from IC authentication papers
    
    Features:
    - YOLO text region detection (from research papers)
    - Multi-engine OCR ensemble (EasyOCR, PaddleOCR, Tesseract)  
    - Dynamic preprocessing for any IC type/resolution
    - Advanced pattern recognition for IC markings
    - Quality-based result selection
    """
    
    def __init__(self):
        print("🚀 Initializing Research-based YOLO-OCR Engine...")
        
        # Initialize our production YOLO-OCR system
        if YOLO_OCR_AVAILABLE:
            try:
                self.yolo_ocr = SimplifiedYOLOOCR()
                self.pattern_extractor = ICMarkingExtractor()
                print("✅ YOLO-OCR system loaded successfully")
                self.primary_engine = 'yolo'
            except Exception as e:
                print(f"❌ Failed to load YOLO-OCR: {e}")
                self.yolo_ocr = None
                self.pattern_extractor = None
                self.primary_engine = 'fallback'
        else:
            self.yolo_ocr = None
            self.pattern_extractor = None
            self.primary_engine = 'fallback'
        
        # Initialize fallback OCR engines
        self._init_fallback_engines()
        
        # Common IC manufacturer patterns for validation
        self.manufacturer_patterns = {
            'Atmel': ['ATMEL', 'ATMEGA', 'ATTINY', 'AT90', 'AT32U'],
            'Texas Instruments': ['TI', 'TEXAS', 'SN74', 'LM', 'TPS'],
            'STMicroelectronics': ['ST', 'STM', 'STM32'],
            'Microchip': ['MICROCHIP', 'PIC', '24LC', '25LC'],
            'Cypress': ['CYPRESS', 'CY8C', 'CY7C'],
            'Analog Devices': ['AD', 'ADI', 'ANALOG'],
            'Maxim': ['MAXIM', 'MAX', 'DS'],
            'Intel': ['INTEL'],
            'Espressif': ['ESP32', 'ESP8266'],
            'NXP': ['NXP', 'PHILIPS'],
            'Infineon': ['INFINEON', 'IFX'],
            'ON Semiconductor': ['ON', 'ONSEMI'],
            'Renesas': ['RENESAS']
        }
    
    def _init_fallback_engines(self):
        """Initialize fallback OCR engines for when YOLO-OCR is not available"""
        print("🔧 Initializing fallback OCR engines...")
        
        # EasyOCR
        try:
            import easyocr
            self.easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            print("✓ EasyOCR initialized")
        except Exception as e:
            print(f"⚠️  EasyOCR not available: {e}")
            self.easyocr_reader = None
        
        # Tesseract  
        try:
            import pytesseract
            # Test if tesseract is available
            pytesseract.image_to_string(np.ones((10, 10), dtype=np.uint8))
            self.tesseract_available = True
            print("✓ Tesseract initialized")
        except Exception as e:
            print(f"⚠️  Tesseract not available: {e}")
            self.tesseract_available = False
    
    def extract_text_from_file(self, image_path: str, method: str = 'yolo') -> Dict[str, Any]:
        """
        Extract text from IC image file using specified method
        
        Args:
            image_path: Path to image file
            method: OCR method ('yolo', 'ensemble', 'easyocr', 'tesseract')
        
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'text': '',
                    'confidence': 0.0,
                    'method': method,
                    'error': f'Could not load image: {image_path}'
                }
            
            # Ensure proper format - YOLO expects RGB, others can handle various formats
            if method.lower() == 'yolo':
                # Convert BGR to RGB for YOLO
                if len(image.shape) == 3 and image.shape[2] == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to regions format for compatibility
            image_regions = [image]
            return self.extract_text(image_regions, method)
            
        except Exception as e:
            return {
                'text': '',
                'confidence': 0.0,
                'method': method,
                'error': f'Failed to process image file: {str(e)}'
            }

    def extract_text(self, image_regions: List[np.ndarray], method: str = 'yolo') -> Dict[str, Any]:
        """
        Extract text from IC image regions using specified method
        
        Args:
            image_regions: List of image regions to process
            method: OCR method ('yolo', 'ensemble', 'easyocr', 'tesseract')
        
        Returns:
            Dictionary with extracted text and metadata
        """
        print(f"🔍 Starting text extraction using method: {method}")
        
        if not image_regions:
            return {
                'text': '',
                'confidence': 0.0,
                'method': method,
                'error': 'No image regions provided'
            }
        
        # Use primary image region (typically the largest/best quality)
        primary_image = image_regions[0] if image_regions else None
        
        if primary_image is None or primary_image.size == 0:
            return {
                'text': '',
                'confidence': 0.0,
                'method': method,
                'error': 'Invalid image region'
            }
        
        try:
            if method.lower() == 'yolo' and self.yolo_ocr is not None:
                return self._extract_with_yolo(primary_image)
            elif method.lower() == 'ensemble':
                return self._extract_with_ensemble(primary_image)
            elif method.lower() == 'easyocr':
                return self._extract_with_easyocr(primary_image)
            elif method.lower() == 'tesseract':
                return self._extract_with_tesseract(primary_image)
            else:
                # Default to best available method
                if self.yolo_ocr is not None:
                    return self._extract_with_yolo(primary_image)
                else:
                    return self._extract_with_ensemble(primary_image)
                    
        except Exception as e:
            print(f"❌ Text extraction failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'method': method,
                'error': str(e)
            }
    
    def _extract_with_yolo(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using our production YOLO-OCR system"""
        try:
            print("🎯 Using YOLO-OCR system...")
            
            # Run YOLO-OCR extraction
            result = self.yolo_ocr.extract_text(image)
            
            extracted_text = result.get('best_text', '')
            confidence = result.get('confidence', 0.0)
            
            print(f"📝 YOLO-OCR extracted: '{extracted_text}'")
            print(f"🎯 Confidence: {confidence:.3f}")
            
            return {
                'text': extracted_text,
                'confidence': confidence,
                'method': 'yolo',
                'regions_detected': len(result.get('regions', [])),
                'yolo_details': result
            }
            
        except Exception as e:
            print(f"❌ YOLO-OCR extraction failed: {e}")
            # Fallback to ensemble method
            return self._extract_with_ensemble(image)
    
    def _extract_with_ensemble(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using ensemble of available OCR engines"""
        try:
            print("🔧 Using ensemble OCR method...")
            
            results = []
            
            # EasyOCR
            if self.easyocr_reader is not None:
                easy_result = self._extract_with_easyocr(image)
                if easy_result['text']:
                    results.append(easy_result)
            
            # Tesseract
            if self.tesseract_available:
                tess_result = self._extract_with_tesseract(image)
                if tess_result['text']:
                    results.append(tess_result)
            
            if not results:
                return {
                    'text': '',
                    'confidence': 0.0,
                    'method': 'ensemble',
                    'error': 'No OCR engines available'
                }
            
            # Select best result based on confidence and text quality
            best_result = max(results, key=lambda x: self._calculate_text_quality(x['text']))
            best_result['method'] = 'ensemble'
            best_result['ensemble_results'] = results
            
            print(f"📝 Ensemble best: '{best_result['text']}'")
            return best_result
            
        except Exception as e:
            print(f"❌ Ensemble extraction failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'ensemble',
                'error': str(e)
            }
    
    def _extract_with_easyocr(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using EasyOCR"""
        if self.easyocr_reader is None:
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'easyocr',
                'error': 'EasyOCR not available'
            }
        
        try:
            results = self.easyocr_reader.readtext(image)
            
            if results:
                # Combine all detected text
                texts = []
                confidences = []
                
                for (bbox, text, confidence) in results:
                    if confidence > 0.3:  # Filter low confidence
                        texts.append(text)
                        confidences.append(confidence)
                
                if texts:
                    combined_text = ' '.join(texts)
                    avg_confidence = sum(confidences) / len(confidences)
                    
                    return {
                        'text': combined_text,
                        'confidence': avg_confidence,
                        'method': 'easyocr',
                        'raw_results': results
                    }
            
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'easyocr'
            }
            
        except Exception as e:
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'easyocr',
                'error': str(e)
            }
    
    def _extract_with_tesseract(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using Tesseract OCR"""
        if not self.tesseract_available:
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'tesseract',
                'error': 'Tesseract not available'
            }
        
        try:
            import pytesseract
            
            # Try different PSM modes for IC text
            psm_modes = [6, 7, 8, 13]  # Different page segmentation modes
            best_result = None
            best_quality = 0
            
            for psm in psm_modes:
                try:
                    config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                    text = pytesseract.image_to_string(image, config=config).strip()
                    
                    if text:
                        quality = self._calculate_text_quality(text)
                        if quality > best_quality:
                            best_quality = quality
                            best_result = {
                                'text': text,
                                'confidence': min(quality * 100, 95),  # Convert to percentage
                                'method': 'tesseract',
                                'psm_mode': psm
                            }
                except:
                    continue
            
            if best_result:
                return best_result
            else:
                return {
                    'text': '',
                    'confidence': 0.0,
                    'method': 'tesseract'
                }
                
        except Exception as e:
            return {
                'text': '',
                'confidence': 0.0,
                'method': 'tesseract',
                'error': str(e)
            }
    
    def _calculate_text_quality(self, text: str) -> float:
        """Calculate text quality score for result selection"""
        if not text:
            return 0.0
        
        score = 0.0
        text_clean = text.strip()
        
        # Length score (IC markings typically 5-50 characters)
        length = len(text_clean)
        if 5 <= length <= 50:
            score += 0.3
        elif 2 <= length < 5:
            score += 0.1
        
        # Alphanumeric content (IC markings have both letters and numbers)
        has_letters = any(c.isalpha() for c in text_clean)
        has_numbers = any(c.isdigit() for c in text_clean)
        if has_letters and has_numbers:
            score += 0.4
        elif has_letters or has_numbers:
            score += 0.2
        
        # Special character penalty
        special_count = sum(1 for c in text_clean if not c.isalnum() and c != ' ')
        special_ratio = special_count / len(text_clean) if text_clean else 0
        if special_ratio < 0.2:
            score += 0.2
        
        # Manufacturer pattern bonus
        text_upper = text_clean.upper()
        for manufacturer, patterns in self.manufacturer_patterns.items():
            if any(pattern in text_upper for pattern in patterns):
                score += 0.1
                break
        
        return min(score, 1.0)
    
    def parse_marking_structure(self, extracted_text: str) -> Dict[str, Any]:
        """
        Parse extracted text to identify IC marking components
        
        Args:
            extracted_text: Raw text extracted from OCR
            
        Returns:
            Dictionary with parsed components (manufacturer, part_number, date_code, etc.)
        """
        print(f"🔍 Parsing marking structure from: '{extracted_text}'")
        
        if not extracted_text:
            return {
                'manufacturer': None,
                'part_number': None,
                'date_code': None,
                'lot_code': None,
                'package_type': None,
                'confidence': 0.0
            }
        
        try:
            # Use our advanced pattern extractor if available
            if self.pattern_extractor is not None:
                parsed_data = self.pattern_extractor.parse_ic_marking(extracted_text)
                
                # Add confidence based on how many components were extracted
                components_found = sum(1 for v in parsed_data.values() if v is not None)
                confidence = min(components_found / 3, 1.0)  # 3 main components: mfg, part, date
                
                parsed_data['confidence'] = confidence
                parsed_data['raw_text'] = extracted_text
                
                print(f"✅ Parsed: Manufacturer={parsed_data.get('manufacturer')}, "
                      f"Part={parsed_data.get('part_number')}, "
                      f"Date={parsed_data.get('date_code')}")
                
                return parsed_data
            
            else:
                # Fallback basic parsing
                return self._basic_parse_marking(extracted_text)
                
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            return {
                'manufacturer': None,
                'part_number': None,
                'date_code': None,
                'lot_code': None,
                'package_type': None,
                'confidence': 0.0,
                'raw_text': extracted_text,
                'error': str(e)
            }
    
    def _basic_parse_marking(self, text: str) -> Dict[str, Any]:
        """Basic fallback parsing when advanced extractor is not available"""
        result = {
            'manufacturer': None,
            'part_number': None,
            'date_code': None,
            'lot_code': None,
            'package_type': None,
            'confidence': 0.3,  # Lower confidence for basic parsing
            'raw_text': text
        }
        
        text_upper = text.upper()
        
        # Basic manufacturer detection
        for manufacturer, patterns in self.manufacturer_patterns.items():
            if any(pattern in text_upper for pattern in patterns):
                result['manufacturer'] = manufacturer
                break
        
        # Basic part number extraction (first alphanumeric sequence)
        words = text.split()
        for word in words:
            if len(word) > 3 and any(c.isalpha() for c in word) and any(c.isdigit() for c in word):
                result['part_number'] = word
                break
        
        # Basic date code detection (4 digit numbers)
        date_match = re.search(r'\b\d{4}\b', text)
        if date_match:
            result['date_code'] = date_match.group()
        
        return result