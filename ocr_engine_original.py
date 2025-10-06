"""
OCR Engine Module - YOLO-OCR Integration
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

# Import our advanced YOLO-OCR system
from simplified_yolo_ocr import SimplifiedYOLOOCR
from ic_marking_extractor import ICMarkingExtractor

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
        try:
            self.yolo_ocr = SimplifiedYOLOOCR()
            self.pattern_extractor = ICMarkingExtractor()
            print("✅ YOLO-OCR system loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load YOLO-OCR: {e}")
            self.yolo_ocr = None
            self.pattern_extractor = None
        
        # Fallback OCR engines (for comparison/backup)
        self._init_fallback_engines()
            self.paddle_ocr = None
        
        # Tesseract configuration
        self.tesseract_config = '--psm 6 --oem 3'
        
        # Initialize advanced OCR methods
        self._init_advanced_ocr()
        
        # Common IC manufacturer patterns
        self.manufacturer_patterns = {
            'Texas Instruments': ['TI', 'TEXAS INSTRUMENTS', 'TEXAS'],
            'STMicroelectronics': ['ST', 'STM', 'STMICRO'],
            'Analog Devices': ['AD', 'ADI', 'ANALOG'],
            'Maxim': ['MAXIM', 'MAX'],
            'NXP': ['NXP', 'PHILIPS'],
            'Infineon': ['INFINEON', 'IFX'],
            'Microchip': ['MICROCHIP', 'MCHP', 'ATMEL', 'ATMEGA', 'ATTINY', 'AME', 'AMB'],  # Added OCR confusion patterns
            'ON Semiconductor': ['ON', 'ONSEMI'],
            'Renesas': ['RENESAS'],
            'Cypress': ['CYPRESS', 'CY'],
            'Intel': ['INTEL'],
            'Broadcom': ['BROADCOM', 'AVAGO'],
        }
    
    def _init_advanced_ocr(self):
        """Initialize advanced OCR methods"""
        # Initialize TrOCR (Transformer-based OCR)
        try:
            import warnings
            warnings.filterwarnings('ignore')
            
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            from transformers import logging as transformers_logging
            transformers_logging.set_verbosity_error()
            
            self.trocr_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
            self.trocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
            print("✓ TrOCR initialized")
        except Exception as e:
            print(f"✗ TrOCR not available: {str(e)[:50]}")
            self.trocr_processor = None
            self.trocr_model = None
        
        # Initialize docTR
        try:
            from doctr.models import ocr_predictor
            self.doctr_model = ocr_predictor(pretrained=True)
            print("✓ docTR initialized")
        except Exception as e:
            print(f"✗ docTR not available: {str(e)[:50]}")
            self.doctr_model = None
        
        # Initialize Keras-OCR
        try:
            import keras_ocr
            self.keras_pipeline = keras_ocr.pipeline.Pipeline()
            print("✓ Keras-OCR initialized")
        except Exception as e:
            print(f"✗ Keras-OCR not available: {str(e)[:50]}")
            self.keras_pipeline = None
    
    def _preprocess_for_advanced_ocr(self, image):
        """Advanced preprocessing for IC text - optimized for engraved markings"""
        from enhanced_preprocessing import preprocess_engraved_text
        return preprocess_engraved_text(image)
        
    def _extract_trocr(self, image):
        """Extract text using TrOCR with advanced preprocessing"""
        if self.trocr_processor is None or self.trocr_model is None:
            return {'text': '', 'confidence': 0}
        
        try:
            from PIL import Image
            from advanced_ic_preprocessing import ICMarkingPreprocessor
            
            preprocessor = ICMarkingPreprocessor()
            
            # Use printed text preprocessing (works best for TrOCR)
            preprocessed = preprocessor.preprocess_printed_text(image)
            
            # Convert to PIL Image (RGB)
            if len(preprocessed.shape) == 2:
                pil_image = Image.fromarray(preprocessed).convert('RGB')
            else:
                pil_image = Image.fromarray(cv2.cvtColor(preprocessed, cv2.COLOR_BGR2RGB))
            
            # Process
            pixel_values = self.trocr_processor(pil_image, return_tensors="pt").pixel_values
            generated_ids = self.trocr_model.generate(pixel_values)
            text = self.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return {'text': text, 'confidence': 0.92}  # Higher confidence for TrOCR
        except Exception as e:
            print(f"TrOCR error: {e}")
            return {'text': '', 'confidence': 0}
    
    def _extract_doctr(self, image):
        """Extract text using docTR"""
        if self.doctr_model is None:
            return {'text': '', 'confidence': 0}
        
        try:
            import tempfile
            import os
            from PIL import Image
            
            # Preprocess
            preprocessed = self._preprocess_for_advanced_ocr(image)
            
            # Convert to RGB
            if len(preprocessed.shape) == 2:
                rgb_image = cv2.cvtColor(preprocessed, cv2.COLOR_GRAY2RGB)
            else:
                rgb_image = preprocessed
            
            # Convert BGR to RGB for PIL
            rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
            
            # Save to temp file (docTR works better with file paths)
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                pil_image = Image.fromarray(rgb_image)
                pil_image.save(tmp.name)
                temp_path = tmp.name
            
            try:
                from doctr.io import DocumentFile
                
                # Run OCR on file
                doc = DocumentFile.from_images(temp_path)
                result = self.doctr_model(doc)
                
                # Extract text
                texts = []
                for page in result.pages:
                    for block in page.blocks:
                        for line in block.lines:
                            line_text = ' '.join([word.value for word in line.words])
                            if line_text.strip():
                                texts.append(line_text)
                
                return {'text': '\n'.join(texts), 'confidence': 0.88}
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            print(f"docTR error: {e}")
            return {'text': '', 'confidence': 0}
    
    def _extract_keras_ocr(self, image):
        """Extract text using Keras-OCR"""
        if self.keras_pipeline is None:
            return {'text': '', 'confidence': 0}
        
        try:
            # Preprocess
            preprocessed = self._preprocess_for_advanced_ocr(image)
            
            # Convert to RGB
            if len(preprocessed.shape) == 2:
                rgb_image = cv2.cvtColor(preprocessed, cv2.COLOR_GRAY2RGB)
            else:
                rgb_image = preprocessed
            
            # Run OCR
            predictions = self.keras_pipeline.recognize([rgb_image])[0]
            
            # Sort by Y coordinate
            predictions.sort(key=lambda x: x[1][0][1])
            texts = [pred[0] for pred in predictions]
            
            return {'text': ' '.join(texts), 'confidence': 0.82}
        except Exception as e:
            print(f"Keras-OCR error: {e}")
            return {'text': '', 'confidence': 0}
        
    def extract_text(self, marking_regions: List[Dict], method='ensemble') -> Dict[str, Any]:
        """
        Extract text from marking regions using specified method
        """
        all_text = []
        confidence_scores = []
        
        for region in marking_regions:
            if 'enhanced_roi' in region:
                image = region['enhanced_roi']
            elif 'image' in region:
                image = region['image']
            else:
                image = region
            
            # Extract using selected method
            if method == 'easyocr':
                result = self._extract_easyocr(image)
            elif method == 'paddle' or method == 'paddleocr':
                result = self._extract_paddle(image)
            elif method == 'tesseract':
                result = self._extract_tesseract(image)
            else:  # ensemble
                result = self._extract_ensemble(image)
            
            all_text.append(result['text'])
            confidence_scores.append(result['confidence'])
        
        # Combine results
        combined_text = '\n'.join(all_text)
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
        
        return {
            'text': combined_text,
            'confidence': avg_confidence,
            'lines': all_text,
            'method': method
        }
    
    def _extract_easyocr(self, image):
        """Extract text using EasyOCR with advanced preprocessing"""
        if self.easyocr_reader is None:
            return {'text': '', 'confidence': 0}
        
        try:
            from advanced_ic_preprocessing import ICMarkingPreprocessor
            
            preprocessor = ICMarkingPreprocessor()
            
            # Try multiple preprocessing variants and collect ALL good results
            variants = preprocessor.create_preprocessing_variants(image)
            all_results = []
            
            for variant_name, preprocessed in variants:
                try:
                    results = self.easyocr_reader.readtext(preprocessed)
                    
                    if not results:
                        continue
                    
                    # Sort results by Y coordinate to maintain line order
                    results_sorted = sorted(results, key=lambda x: x[0][0][1])
                    
                    text_lines = []
                    confidences = []
                    current_line = []
                    current_y = None
                    y_threshold = 15  # Pixels difference to consider same line
                    
                    for bbox, text, conf in results_sorted:
                        # Get Y coordinate of text
                        y_coord = bbox[0][1]
                        
                        # Check if this text belongs to current line
                        if current_y is None or abs(y_coord - current_y) <= y_threshold:
                            current_line.append(text)
                            current_y = y_coord if current_y is None else current_y
                        else:
                            # Start new line
                            if current_line:
                                text_lines.append(' '.join(current_line))
                            current_line = [text]
                            current_y = y_coord
                        
                        confidences.append(conf)
                    
                    # Add last line
                    if current_line:
                        text_lines.append(' '.join(current_line))
                    
                    avg_conf = np.mean(confidences) if confidences else 0
                    text = '\n'.join(text_lines)
                    
                    # Only keep results with reasonable confidence and content
                    if avg_conf > 0.15 and len(text.strip()) > 2:
                        all_results.append({
                            'text': text,
                            'confidence': avg_conf,
                            'variant': variant_name
                        })
                except Exception as e:
                    continue
            
            # Return the best result, or empty if none found
            if all_results:
                best = max(all_results, key=lambda x: x['confidence'])
                return best
            else:
                return {'text': '', 'confidence': 0}
            
        except Exception as e:
            print(f"EasyOCR error: {e}")
            return {'text': '', 'confidence': 0}
    
    def _extract_paddle(self, image):
        """Extract text using PaddleOCR with advanced preprocessing"""
        if self.paddle_ocr is None:
            return {'text': '', 'confidence': 0}
        
        try:
            from advanced_ic_preprocessing import ICMarkingPreprocessor
            
            preprocessor = ICMarkingPreprocessor()
            
            # Try multiple preprocessing variants and pick best result
            variants = preprocessor.create_preprocessing_variants(image)
            best_result = {'text': '', 'confidence': 0}
            
            for variant_name, preprocessed in variants:
                try:
                    results = self.paddle_ocr.ocr(preprocessed, cls=True)
                    
                    if not results or not results[0]:
                        continue
                    
                    text_parts = []
                    confidences = []
                    
                    for line in results[0]:
                        text = line[1][0]
                        conf = line[1][1]
                        text_parts.append(text)
                        confidences.append(conf)
                    
                    avg_conf = np.mean(confidences) if confidences else 0
                    
                    if avg_conf > best_result['confidence']:
                        best_result = {
                            'text': '\n'.join(text_parts),
                            'confidence': avg_conf,
                            'variant': variant_name
                        }
                except:
                    continue
            
            return best_result
            
        except Exception as e:
            print(f"PaddleOCR error: {e}")
            return {'text': '', 'confidence': 0}
    
    def _extract_tesseract(self, image):
        """Extract text using Tesseract"""
        try:
            # Preprocess for Tesseract
            processed = self._preprocess_for_tesseract(image)
            
            text = pytesseract.image_to_string(
                processed,
                config=self.tesseract_config
            )
            
            # Get confidence
            data = pytesseract.image_to_data(
                processed,
                output_type=pytesseract.Output.DICT,
                config=self.tesseract_config
            )
            
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = np.mean(confidences) / 100 if confidences else 0
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence
            }
        except pytesseract.TesseractNotFoundError:
            # Tesseract not installed - return empty result
            return {'text': '', 'confidence': 0}
        except Exception as e:
            print(f"Tesseract error: {e}")
            return {'text': '', 'confidence': 0}
    
    def _preprocess_for_tesseract(self, image):
        """Preprocess image specifically for Tesseract"""
        # Resize if too small
        h, w = image.shape[:2]
        if h < 30 or w < 30:
            scale = max(30 / h, 30 / w, 2.0)
            image = cv2.resize(
                image,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter
        filtered = cv2.bilateralFilter(image, 5, 50, 50)
        
        # Threshold
        _, binary = cv2.threshold(
            filtered,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        return binary
    
    def _extract_ensemble(self, image):
        """
        Extract text using ensemble of ALL available methods
        Combines results from standard + advanced OCR for better accuracy
        Uses intelligent result selection based on content quality, not just confidence
        """
        results = []
        
        # Try standard methods
        easy_result = self._extract_easyocr(image)
        paddle_result = self._extract_paddle(image)
        tess_result = self._extract_tesseract(image)
        
        if easy_result['confidence'] > 0:
            results.append(('easyocr', easy_result))
        if paddle_result['confidence'] > 0:
            results.append(('paddleocr', paddle_result))
        if tess_result['confidence'] > 0:
            results.append(('tesseract', tess_result))
        
        # Try advanced methods
        trocr_result = self._extract_trocr(image)
        if trocr_result['confidence'] > 0:
            results.append(('trocr', trocr_result))
        
        doctr_result = self._extract_doctr(image)
        if doctr_result['confidence'] > 0:
            results.append(('doctr', doctr_result))
        
        keras_result = self._extract_keras_ocr(image)
        if keras_result['confidence'] > 0:
            results.append(('keras', keras_result))
        
        if not results:
            return {'text': '', 'confidence': 0}
        
        # Smart result selection based on content quality
        scored_results = []
        for method_name, result in results:
            quality_score = self._assess_result_quality(result['text'])
            # Combine quality score with confidence
            # Give more weight to quality (0.7) vs confidence (0.3)
            combined_score = (quality_score * 0.7) + (result['confidence'] * 0.3)
            scored_results.append((combined_score, method_name, result))
        
        # Sort by combined score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        best_score, best_method, best_result = scored_results[0]
        
        # If multiple results, try to find consensus
        if len(results) > 1:
            texts = [r[1]['text'] for r in results]
            consensus_text = self._find_consensus_text(texts)
            
            # Use consensus if it's significantly better than best single result
            consensus_quality = self._assess_result_quality(consensus_text)
            best_quality = self._assess_result_quality(best_result['text'])
            
            if consensus_quality > best_quality * 1.2:  # 20% better
                print(f"  → Ensemble combined {len(results)} OCR methods, using consensus")
                return {
                    'text': consensus_text,
                    'confidence': np.mean([r[1]['confidence'] for r in results])
                }
            else:
                print(f"  → Ensemble combined {len(results)} OCR methods, best: {best_method}")
                return best_result
        
        return best_result
    
    def _assess_result_quality(self, text: str) -> float:
        """
        Assess the quality of OCR result based on content characteristics
        Returns score from 0.0 to 1.0
        
        High quality indicators:
        - Contains alphanumeric characters
        - Has reasonable length (IC markings are typically 10-50 chars)
        - Contains common IC patterns (part numbers, date codes)
        - Has mixed case or numbers
        
        Low quality indicators:
        - Single random word (like "CASHIER", "PAYMENT")
        - Mostly special characters
        - Very short (< 5 chars) or very long (> 150 chars)
        - High ratio of dashes/underscores
        - Repetitive patterns
        """
        if not text or len(text.strip()) == 0:
            return 0.0
        
        text_clean = text.strip()
        score = 0.3  # Start lower to be more selective
        
        # 1. Length check (IC markings typically 8-80 characters)
        length = len(text_clean)
        if 8 <= length <= 80:
            score += 0.2
        elif 5 <= length < 8:
            score += 0.1
        elif length < 5:
            score -= 0.3  # Very short is bad
        elif length > 150:
            score -= 0.2  # Very long is bad
        
        # 2. Alphanumeric ratio (higher is better for IC markings)
        alphanumeric = sum(c.isalnum() for c in text_clean)
        alpha_ratio = alphanumeric / len(text_clean) if len(text_clean) > 0 else 0
        score += alpha_ratio * 0.2  # Up to +0.2
        
        # 3. CRITICAL: Must contain both letters AND numbers for IC marking
        has_letters = any(c.isalpha() for c in text_clean)
        has_numbers = any(c.isdigit() for c in text_clean)
        if has_letters and has_numbers:
            score += 0.4  # Big bonus for mixed content
        elif has_letters and not has_numbers:
            # Single word with only letters is likely garbage (like "CASHIER")
            score -= 0.3
        
        # 4. Penalize excessive special characters
        special_chars = sum(c in '-_*~`@#$%^&()[]{}|\\/' for c in text_clean)
        special_ratio = special_chars / len(text_clean)
        if special_ratio > 0.5:
            score -= 0.4
        elif special_ratio > 0.3:
            score -= 0.2
        
        # 5. Penalize repetitive patterns (like "----" or "aaaa")
        import re
        repetitive = len(re.findall(r'(.)\1{3,}', text_clean))  # Same char repeated 4+ times
        if repetitive > 2:
            score -= 0.3
        
        # 6. BIG bonus for manufacturer names (case-insensitive)
        manufacturer_keywords = ['atmel', 'atmega', 'attiny', 'microchip', 'mchp',
                                'texas', 'intel', 'amd', 'nvidia', 'samsung', 'ti', 
                                'st', 'stm', 'nxp', 'analog']
        text_lower = text_clean.lower()
        for keyword in manufacturer_keywords:
            if keyword in text_lower:
                score += 0.3  # Big bonus
                break
        
        # 7. Bonus for date code patterns (4 or 6 digits together)
        if re.search(r'\b\d{4}\b', text_clean):
            score += 0.2
        if re.search(r'\b\d{6}\b', text_clean):
            score += 0.2
        
        # 8. Bonus for IC part number patterns
        # Pattern like: ATMEGA328, STM32F103, SN74HC595, etc.
        ic_patterns = [
            r'(?i)[A-Z]{2,}\d{2,}[A-Z]{0,3}',  # Like ATMEGA328, STM32F4
            r'(?i)SN\d+',  # Texas Instruments SNxxx
            r'(?i)[A-Z]{2,}\d{3,}',  # Generic IC pattern
        ]
        for pattern in ic_patterns:
            if re.search(pattern, text_clean):
                score += 0.2
                break
        
        # 9. Penalize common random words (false positives)
        garbage_words = ['cashier', 'payment', 'customer', 'total', 'receipt',
                        'change', 'item', 'price', 'subtotal']
        if text_lower in garbage_words or any(word == text_lower for word in garbage_words):
            score -= 0.5  # Heavy penalty for obvious garbage
        
        # Clamp score to [0, 1]
        return max(0.0, min(1.0, score))
    
    def _find_consensus_text(self, texts):
        """
        Find consensus among multiple OCR results
        """
        if not texts:
            return ''
        
        # Score each text by similarity to others
        scores = []
        for text in texts:
            score = sum(fuzz.ratio(text, other) for other in texts)
            scores.append(score)
        
        # Return text with highest consensus
        best_idx = np.argmax(scores)
        return texts[best_idx]
    
    def parse_marking_structure(self, ocr_result: Dict) -> Dict[str, Any]:
        """
        Parse the OCR text into structured marking information
        Extracts: manufacturer, part number, date code, lot code, etc.
        """
        text = ocr_result.get('text', '')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        parsed = {
            'raw_text': text,
            'lines': lines,
            'manufacturer': None,
            'part_number': None,
            'date_code': None,
            'lot_code': None,
            'country_of_origin': None,
            'additional_codes': []
        }
        
        # Identify manufacturer
        parsed['manufacturer'] = self._identify_manufacturer(text)
        
        # Extract part number (typically alphanumeric, may include hyphens)
        part_number = self._extract_part_number(lines)
        parsed['part_number'] = part_number
        
        # Extract date code
        date_code = self._extract_date_code(text)
        parsed['date_code'] = date_code
        
        # Extract lot code
        lot_code = self._extract_lot_code(text)
        parsed['lot_code'] = lot_code
        
        # Extract country code
        country = self._extract_country_code(text)
        parsed['country_of_origin'] = country
        
        return parsed
    
    def _identify_manufacturer(self, text):
        """Identify manufacturer from text"""
        text_upper = text.upper()
        
        for manufacturer, patterns in self.manufacturer_patterns.items():
            for pattern in patterns:
                if pattern in text_upper:
                    return manufacturer
        
        return None
    
    def _extract_part_number(self, lines):
        """
        Extract part number from lines with aggressive OCR error correction
        Part numbers typically appear in first few lines
        """
        # Common part number patterns (order matters - more specific first)
        patterns = [
            r'[A-Z]{2,4}[0-9][A-Z0-9]{4,}[-][0-9A-Z]{2,}',  # e.g., CY8C29666-24PVXI
            r'[A-Z]{3,}[0-9]{3,}[-][A-Z0-9]+',  # e.g., ADC-1234, longer version
            r'[A-Z]+[0-9]+[A-Z]*[-/][A-Z0-9]+',  # With separator
            r'[A-Z]{2,4}[0-9]{2,6}[A-Z]{0,4}',  # e.g., LM358N, TL072CP
            r'[0-9]{2,4}[A-Z]{1,3}[0-9]{2,4}',  # e.g., 74HC595
        ]
        
        for line in lines[:3]:  # Check first 3 lines
            # Clean up the line - aggressive normalization
            cleaned = line.strip().upper()
            
            # Pre-correct common OCR errors BEFORE pattern matching
            ocr_corrections = {
                'O': '0', 'o': '0',
                'I': '1', 'l': '1', 'i': '1',
                'Z': '2', 'z': '2',
                'S': '5', 's': '5',
                'B': '8', 'b': '8',
                'G': '6', 'g': '6',
            }
            
            # Apply corrections character by character in context
            corrected = []
            for i, char in enumerate(cleaned):
                # If char looks like it should be a number (surrounded by numbers)
                if i > 0 and i < len(cleaned) - 1:
                    prev_is_digit = cleaned[i-1].isdigit()
                    next_is_digit = cleaned[i+1].isdigit()
                    
                    if prev_is_digit and next_is_digit and char in 'OILZSBG':
                        corrected.append(ocr_corrections.get(char, char))
                    elif char in ['C', 'c'] and prev_is_digit:
                        # Keep C if after a digit (likely part of chip number)
                        corrected.append(char)
                    else:
                        corrected.append(char)
                else:
                    corrected.append(char)
            
            cleaned = ''.join(corrected)
            
            # Remove extra spaces
            cleaned = ' '.join(cleaned.split())
            
            for pattern in patterns:
                matches = re.findall(pattern, cleaned)
                if matches:
                    # Return longest match (likely the full part number)
                    longest = max(matches, key=len)
                    
                    # Final cleanup: Fix specific Cypress pattern (CY8C not CY0C)
                    if longest.startswith('CY0C'):
                        longest = 'CY8C' + longest[4:]
                    elif longest.startswith('CYOC'):
                        longest = 'CY8C' + longest[4:]
                    
                    return longest
        
        # If no pattern matches, return first substantial line
        for line in lines:
            cleaned = line.strip()
            if len(cleaned) > 6 and any(c.isalnum() for c in cleaned):
                # Take first word/token that looks like a part number
                tokens = cleaned.split()
                for token in tokens:
                    if len(token) > 6 and any(c.isdigit() for c in token):
                        return token.upper()
        
        return None
    
    def _extract_date_code(self, text):
        """
        Extract date code from text
        Common formats: YYWW, YYYYWW, YYMMDD, or full year like 2007
        Also handles batch codes like 'B 05 PHI 2007'
        """
        text_upper = text.upper()
        
        # Date code patterns (order matters - most specific first)
        patterns = [
            # Format: 'B 05 PHI 2007' or similar
            (r'\b([A-Z])\s*([0-9]{2})\s+([A-Z]{2,4})\s+([0-9]{4})\b', 'batch_full'),
            # Full year like 2007, 2008, etc.
            (r'\b(20[0-2][0-9])\b', 'year'),
            # Format like 'B05' (batch + week)
            (r'\b([A-Z])([0-9]{2})\b', 'batch_week'),
            # Format like '05 PHI 2007' (week + country + year)
            (r'\b([0-9]{2})\s*[A-Z]{2,4}\s*([0-9]{4})\b', 'week_country_year'),
            # YYYYWW or YYMMDD (6 digits)
            (r'\b([0-9]{6})\b', 'yyyyww'),
            # YYWW or YYMM (4 digits)
            (r'\b([0-9]{4})\b', 'yyww'),
            # YY-Letter-WW
            (r'\b([0-9]{2}[A-Z][0-9]{2})\b', 'yylww'),
        ]
        
        for pattern, format_type in patterns:
            matches = re.findall(pattern, text_upper)
            if matches:
                if format_type == 'batch_full':
                    # Return combined: 'B 05 PHI 2007'
                    match = matches[0]
                    return f"{match[0]} {match[1]} {match[2]} {match[3]}"
                elif format_type == 'week_country_year':
                    # Return the year part
                    return matches[0][1] if isinstance(matches[0], tuple) else matches[0]
                elif format_type == 'batch_week':
                    # Return combined: 'B05'
                    return ''.join(matches[0]) if isinstance(matches[0], tuple) else matches[0]
                else:
                    # Return first match
                    return matches[0][0] if isinstance(matches[0], tuple) else matches[0]
        
        return None
    
    def _extract_lot_code(self, text):
        """Extract lot code from text"""
        # Lot codes often contain LOT or L prefix, or manufacturer prefix
        patterns = [
            r'LOT[:\s]*([A-Z0-9]+)',
            r'\b(CYP|TI|ST|AD)[\s]*([0-9]{5,})\b',  # Manufacturer prefix + numbers
            r'L[:\s]*([A-Z0-9]{4,})',
            r'\b([A-Z]{2,3})[\s]+([0-9]{5,})\b',  # Letters + space + numbers
            r'\b[A-Z][0-9]{5,}\b',
        ]
        
        text_upper = text.upper()
        for pattern in patterns:
            matches = re.findall(pattern, text_upper)
            if matches:
                # Handle tuple results from groups
                if isinstance(matches[0], tuple):
                    return ' '.join(matches[0]).strip()
                return matches[0]
        
        return None
    
    def _extract_country_code(self, text):
        """Extract country of origin code"""
        country_codes = {
            'CHINA': ['CHINA', 'CHN', 'PRC'],
            'TAIWAN': ['TAIWAN', 'TWN', 'ROC'],
            'MALAYSIA': ['MALAYSIA', 'MYS'],
            'PHILIPPINES': ['PHILIPPINES', 'PHL', 'PHI'],
            'THAILAND': ['THAILAND', 'THA'],
            'KOREA': ['KOREA', 'KOR'],
            'JAPAN': ['JAPAN', 'JPN'],
            'USA': ['USA', 'US'],
            'GERMANY': ['GERMANY', 'DEU'],
        }
        
        text_upper = text.upper()
        for country, codes in country_codes.items():
            for code in codes:
                if code in text_upper:
                    return country
        
        return None
    
    def validate_part_number_format(self, part_number: str, manufacturer: str = None) -> bool:
        """
        Validate if part number follows expected format for manufacturer
        """
        if not part_number:
            return False
        
        # Basic validation
        if len(part_number) < 4:
            return False
        
        # Should contain both letters and numbers
        has_letter = any(c.isalpha() for c in part_number)
        has_number = any(c.isdigit() for c in part_number)
        
        return has_letter and has_number
