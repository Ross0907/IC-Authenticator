"""
YOLO-OCR Text Detection and Recognition System
Based on research papers and dynamic IC text detection requirements

This system implements:
1. YOLO for text detection (bounding boxes)
2. Multi-scale preprocessing for different resolutions
3. Multiple OCR engines for text recognition
4. Dynamic adaptation to any IC image type

References:
- https://github.com/aqntks/Easy-Yolo-OCR
- ICText-AGCL: https://chunchet-ng.github.io/ICText-AGCL/
- Research papers on IC text detection
"""

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from ultralytics import YOLO
import pytesseract
import easyocr
import albumentations as A
from typing import List, Tuple, Dict, Optional
import os
import logging

# Suppress ultralytics warnings
logging.getLogger('ultralytics').setLevel(logging.ERROR)

class YOLOTextDetector:
    """
    YOLO-based text detection for IC markings
    Detects text regions and provides bounding boxes
    """
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load YOLOv8 model - start with pre-trained then fine-tune for IC text"""
        try:
            # Try to load custom IC text detection model first
            if os.path.exists('models/ic_text_detection.pt'):
                self.model = YOLO('models/ic_text_detection.pt')
                print("✓ Loaded custom IC text detection model")
            else:
                # Use general object detection model and adapt for text
                self.model = YOLO('yolov8n.pt')  # Lightweight model
                print("✓ Loaded YOLOv8 nano model (will adapt for text detection)")
        except Exception as e:
            print(f"⚠️ YOLO model loading failed: {e}")
            self.model = None
    
    def detect_text_regions(self, image: np.ndarray, confidence_threshold: float = 0.25) -> List[Dict]:
        """
        Detect text regions in IC image using YOLO
        
        Args:
            image: Input BGR image
            confidence_threshold: Detection confidence threshold
            
        Returns:
            List of detected regions with bounding boxes and confidence
        """
        if self.model is None:
            return self._fallback_text_detection(image)
        
        try:
            # Run YOLO detection
            results = self.model(image, conf=confidence_threshold, verbose=False)
            
            detected_regions = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        
                        # Ensure coordinates are within image bounds
                        h, w = image.shape[:2]
                        x1, y1, x2, y2 = max(0, int(x1)), max(0, int(y1)), min(w, int(x2)), min(h, int(y2))
                        
                        if x2 > x1 and y2 > y1:  # Valid box
                            detected_regions.append({
                                'bbox': (x1, y1, x2, y2),
                                'confidence': float(confidence),
                                'area': (x2 - x1) * (y2 - y1)
                            })
            
            # Sort by confidence and filter small regions
            detected_regions = [r for r in detected_regions if r['area'] > 100]
            detected_regions.sort(key=lambda x: x['confidence'], reverse=True)
            
            return detected_regions[:10]  # Top 10 detections
            
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return self._fallback_text_detection(image)
    
    def _fallback_text_detection(self, image: np.ndarray) -> List[Dict]:
        """
        Fallback text detection using traditional computer vision
        When YOLO is not available or fails
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Multiple detection strategies
        regions = []
        
        # Strategy 1: MSER (Maximally Stable Extremal Regions)
        regions.extend(self._mser_detection(gray))
        
        # Strategy 2: Contour-based detection
        regions.extend(self._contour_detection(gray))
        
        # Strategy 3: Edge-based detection
        regions.extend(self._edge_detection(gray))
        
        # Remove duplicates and filter
        regions = self._filter_regions(regions, image.shape[:2])
        
        return regions
    
    def _mser_detection(self, gray: np.ndarray) -> List[Dict]:
        """MSER-based text detection"""
        try:
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)
            
            detected = []
            for region in regions:
                if len(region) > 10:  # Minimum points
                    x, y, w, h = cv2.boundingRect(region)
                    if w > 10 and h > 5 and w < gray.shape[1] * 0.8 and h < gray.shape[0] * 0.8:
                        detected.append({
                            'bbox': (x, y, x + w, y + h),
                            'confidence': 0.7,
                            'area': w * h,
                            'method': 'mser'
                        })
            
            return detected
        except:
            return []
    
    def _contour_detection(self, gray: np.ndarray) -> List[Dict]:
        """Contour-based text detection"""
        try:
            # Apply threshold
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                # Filter by aspect ratio and size
                aspect_ratio = w / h if h > 0 else 0
                if (0.1 < aspect_ratio < 10 and 
                    area > 100 and area < gray.shape[0] * gray.shape[1] * 0.5):
                    
                    detected.append({
                        'bbox': (x, y, x + w, y + h),
                        'confidence': 0.6,
                        'area': area,
                        'method': 'contour'
                    })
            
            return detected
        except:
            return []
    
    def _edge_detection(self, gray: np.ndarray) -> List[Dict]:
        """Edge-based text detection"""
        try:
            # Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Dilate to connect text components
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Find contours in edges
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                if area > 200 and w > 15 and h > 8:
                    detected.append({
                        'bbox': (x, y, x + w, y + h),
                        'confidence': 0.5,
                        'area': area,
                        'method': 'edge'
                    })
            
            return detected
        except:
            return []
    
    def _filter_regions(self, regions: List[Dict], image_shape: Tuple[int, int]) -> List[Dict]:
        """Filter and deduplicate detected regions"""
        if not regions:
            return []
        
        h, w = image_shape
        
        # Filter by size and position
        filtered = []
        for region in regions:
            x1, y1, x2, y2 = region['bbox']
            
            # Check bounds
            if x1 >= 0 and y1 >= 0 and x2 <= w and y2 <= h:
                width, height = x2 - x1, y2 - y1
                area = width * height
                
                # Size filters
                if (width > 10 and height > 5 and 
                    area > 100 and area < w * h * 0.7):
                    filtered.append(region)
        
        # Remove overlapping regions (NMS-like)
        filtered = self._non_max_suppression(filtered, overlap_threshold=0.3)
        
        # Sort by confidence
        filtered.sort(key=lambda x: x['confidence'], reverse=True)
        
        return filtered[:15]  # Limit to top 15
    
    def _non_max_suppression(self, regions: List[Dict], overlap_threshold: float = 0.3) -> List[Dict]:
        """Remove overlapping bounding boxes"""
        if not regions:
            return []
        
        # Sort by confidence
        regions = sorted(regions, key=lambda x: x['confidence'], reverse=True)
        
        keep = []
        while regions:
            current = regions.pop(0)
            keep.append(current)
            
            # Remove overlapping regions
            remaining = []
            for region in regions:
                if self._calculate_overlap(current['bbox'], region['bbox']) < overlap_threshold:
                    remaining.append(region)
            regions = remaining
        
        return keep
    
    def _calculate_overlap(self, box1: Tuple[int, int, int, int], 
                          box2: Tuple[int, int, int, int]) -> float:
        """Calculate IoU overlap between two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0


class DynamicImagePreprocessor:
    """
    Dynamic preprocessing that adapts to any IC image resolution and type
    Implements albumentations for robust augmentation
    """
    
    def __init__(self):
        self.setup_augmentations()
    
    def setup_augmentations(self):
        """Setup albumentations pipeline for different IC types"""
        # For text enhancement
        self.text_enhance = A.Compose([
            A.CLAHE(clip_limit=4.0, tile_grid_size=(8, 8), p=1.0),
            A.GaussianBlur(blur_limit=(1, 3), p=0.3),
            A.Sharpen(alpha=(0.2, 0.5), lightness=(0.5, 1.0), p=0.5),
        ])
        
        # For contrast enhancement
        self.contrast_enhance = A.Compose([
            A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=1.0),
            A.CLAHE(clip_limit=6.0, tile_grid_size=(4, 4), p=1.0),
        ])
        
        # For noise reduction
        self.denoise = A.Compose([
            A.GaussianBlur(blur_limit=(1, 3), p=0.7),
            A.MedianBlur(blur_limit=3, p=0.3),
        ])
    
    def preprocess_for_detection(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for YOLO text detection
        Ensures optimal conditions for text detection
        """
        # Resize to optimal detection size
        target_size = 640  # YOLO standard
        image = self._resize_maintain_aspect(image, target_size)
        
        # Basic enhancement for detection
        if len(image.shape) == 3:
            # Convert to RGB for albumentations
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            enhanced = self.text_enhance(image=image_rgb)['image']
            image = cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)
        
        return image
    
    def preprocess_text_region(self, region: np.ndarray, method: str = 'adaptive') -> List[np.ndarray]:
        """
        Preprocess detected text region for OCR
        Returns multiple variants for ensemble OCR
        
        Args:
            region: Cropped text region
            method: 'adaptive', 'laser', 'printed', 'embossed'
        """
        if region.size == 0:
            return []
        
        # Always work with minimum size for OCR
        region = self._ensure_minimum_size(region, min_height=32)
        
        variants = []
        
        if method == 'adaptive' or method == 'all':
            # Generate multiple preprocessing variants
            variants.extend(self._generate_variants(region))
        else:
            # Specific preprocessing
            variants.append(self._preprocess_specific(region, method))
        
        return [v for v in variants if v is not None]
    
    def _resize_maintain_aspect(self, image: np.ndarray, target_size: int) -> np.ndarray:
        """Resize image maintaining aspect ratio"""
        h, w = image.shape[:2]
        
        if max(h, w) <= target_size:
            return image
        
        if h > w:
            new_h = target_size
            new_w = int(w * target_size / h)
        else:
            new_w = target_size
            new_h = int(h * target_size / w)
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    def _ensure_minimum_size(self, image: np.ndarray, min_height: int = 32) -> np.ndarray:
        """Ensure image has minimum size for OCR"""
        h, w = image.shape[:2]
        
        if h < min_height:
            scale = min_height / h
            new_w = int(w * scale)
            new_h = min_height
            image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        return image
    
    def _generate_variants(self, image: np.ndarray) -> List[np.ndarray]:
        """Generate multiple preprocessing variants"""
        variants = []
        
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Variant 1: CLAHE + Adaptive threshold
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
            enhanced = clahe.apply(gray)
            binary1 = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
            variants.append(binary1)
            
            # Variant 2: Otsu threshold with blur
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            _, binary2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append(binary2)
            
            # Variant 3: Sauvola-like threshold
            binary3 = self._sauvola_threshold(gray)
            variants.append(binary3)
            
            # Variant 4: Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morph = cv2.morphologyEx(enhanced, cv2.MORPH_TOPHAT, kernel)
            _, binary4 = cv2.threshold(morph, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append(binary4)
            
            # Variant 5: Inverted (for dark text on light background)
            _, binary5 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            variants.append(binary5)
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            # Fallback - simple threshold
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            variants = [binary]
        
        return variants
    
    def _preprocess_specific(self, image: np.ndarray, method: str) -> np.ndarray:
        """Apply specific preprocessing method"""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            if method == 'laser':
                # For laser-etched text
                clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
                enhanced = clahe.apply(gray)
                binary = self._sauvola_threshold(enhanced)
                return binary
            
            elif method == 'printed':
                # For printed text
                blurred = cv2.GaussianBlur(gray, (3, 3), 0)
                _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                return binary
            
            elif method == 'embossed':
                # For embossed text using gradient
                grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                gradient = np.sqrt(grad_x**2 + grad_y**2)
                gradient = np.uint8(gradient / gradient.max() * 255)
                _, binary = cv2.threshold(gradient, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                return binary
            
            else:
                # Default
                _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                return binary
                
        except Exception as e:
            print(f"Specific preprocessing error: {e}")
            return gray if 'gray' in locals() else image
    
    def _sauvola_threshold(self, image: np.ndarray, window_size: int = 15, k: float = 0.2) -> np.ndarray:
        """Sauvola adaptive thresholding"""
        try:
            # Ensure odd window size
            if window_size % 2 == 0:
                window_size += 1
            
            # Compute local mean and variance
            mean = cv2.blur(image.astype(np.float32), (window_size, window_size))
            mean_sq = cv2.blur((image.astype(np.float32))**2, (window_size, window_size))
            variance = mean_sq - mean**2
            std = np.sqrt(np.maximum(variance, 0))
            
            # Sauvola threshold
            r = 128  # Dynamic range
            threshold = mean * (1 + k * ((std / r) - 1))
            
            # Apply threshold
            binary = np.zeros_like(image)
            binary[image > threshold] = 255
            
            return binary.astype(np.uint8)
        except:
            # Fallback to adaptive threshold
            return cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                       cv2.THRESH_BINARY, window_size, 2)


class MultiOCREngine:
    """
    Multi-engine OCR with dynamic adaptation
    Combines EasyOCR, Tesseract, TrOCR, and other engines
    """
    
    def __init__(self):
        self.engines = {}
        self.setup_engines()
    
    def setup_engines(self):
        """Initialize all available OCR engines"""
        # EasyOCR
        try:
            self.engines['easyocr'] = easyocr.Reader(['en'], verbose=False, gpu=torch.cuda.is_available())
            print("✓ EasyOCR initialized")
        except Exception as e:
            print(f"⚠️ EasyOCR failed: {e}")
        
        # Tesseract
        try:
            # Test tesseract availability
            pytesseract.pytesseract.run_tesseract('test', 'txt', lang='eng')
            self.engines['tesseract'] = True
            print("✓ Tesseract initialized")
        except Exception as e:
            print(f"⚠️ Tesseract failed: {e}")
        
        # TrOCR (if available)
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            self.engines['trocr_processor'] = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
            self.engines['trocr_model'] = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
            print("✓ TrOCR initialized")
        except Exception as e:
            print(f"⚠️ TrOCR failed: {e}")
    
    def recognize_text(self, image_variants: List[np.ndarray]) -> Dict[str, str]:
        """
        Recognize text from preprocessed image variants
        Returns best result from all engines and variants
        """
        results = {}
        
        for variant_idx, image in enumerate(image_variants):
            variant_results = {}
            
            # EasyOCR
            if 'easyocr' in self.engines:
                text = self._run_easyocr(image)
                if text:
                    variant_results[f'easyocr_v{variant_idx}'] = text
            
            # Tesseract
            if 'tesseract' in self.engines:
                text = self._run_tesseract(image)
                if text:
                    variant_results[f'tesseract_v{variant_idx}'] = text
            
            # TrOCR
            if 'trocr_processor' in self.engines:
                text = self._run_trocr(image)
                if text:
                    variant_results[f'trocr_v{variant_idx}'] = text
            
            results.update(variant_results)
        
        return results
    
    def _run_easyocr(self, image: np.ndarray) -> str:
        """Run EasyOCR on image"""
        try:
            results = self.engines['easyocr'].readtext(image)
            texts = [result[1] for result in results if result[2] > 0.3]  # Confidence > 30%
            return ' '.join(texts).strip()
        except Exception as e:
            return ""
    
    def _run_tesseract(self, image: np.ndarray) -> str:
        """Run Tesseract on image"""
        try:
            # Multiple PSM modes for different text layouts
            psm_modes = [6, 7, 8, 13]  # Different page segmentation modes
            best_text = ""
            
            for psm in psm_modes:
                config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                text = pytesseract.image_to_string(image, config=config).strip()
                
                if len(text) > len(best_text):
                    best_text = text
            
            return best_text
        except Exception as e:
            return ""
    
    def _run_trocr(self, image: np.ndarray) -> str:
        """Run TrOCR on image"""
        try:
            from PIL import Image
            
            # Convert to PIL
            if len(image.shape) == 2:
                pil_image = Image.fromarray(image).convert('RGB')
            else:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Process
            pixel_values = self.engines['trocr_processor'](pil_image, return_tensors="pt").pixel_values
            generated_ids = self.engines['trocr_model'].generate(pixel_values)
            text = self.engines['trocr_processor'].batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return text.strip()
        except Exception as e:
            return ""


class DynamicYOLOOCR:
    """
    Main YOLO-OCR system that dynamically adapts to any IC image
    Combines YOLO detection with multi-engine OCR recognition
    """
    
    def __init__(self):
        self.text_detector = YOLOTextDetector()
        self.preprocessor = DynamicImagePreprocessor()
        self.ocr_engine = MultiOCREngine()
        
        print("🚀 Dynamic YOLO-OCR system initialized")
    
    def extract_text_from_ic(self, image: np.ndarray, 
                           detection_confidence: float = 0.25,
                           preprocessing_method: str = 'adaptive') -> Dict:
        """
        Main function to extract text from IC image
        
        Args:
            image: Input IC image (any resolution)
            detection_confidence: YOLO detection confidence threshold
            preprocessing_method: 'adaptive', 'laser', 'printed', 'embossed', 'all'
        
        Returns:
            Dict with extracted text and metadata
        """
        results = {
            'detected_regions': [],
            'ocr_results': {},
            'final_text': '',
            'confidence': 0.0,
            'metadata': {
                'image_size': image.shape,
                'num_regions': 0,
                'preprocessing_method': preprocessing_method
            }
        }
        
        try:
            # Step 1: Preprocess for detection
            detection_image = self.preprocessor.preprocess_for_detection(image.copy())
            
            # Step 2: Detect text regions using YOLO
            detected_regions = self.text_detector.detect_text_regions(
                detection_image, detection_confidence
            )
            
            results['detected_regions'] = detected_regions
            results['metadata']['num_regions'] = len(detected_regions)
            
            if not detected_regions:
                # Fallback: Process entire image
                print("No text regions detected, processing entire image")
                detected_regions = [{
                    'bbox': (0, 0, image.shape[1], image.shape[0]),
                    'confidence': 1.0,
                    'area': image.shape[0] * image.shape[1],
                    'method': 'fullimage'
                }]
            
            # Step 3: Process each detected region
            all_texts = []
            region_results = {}
            
            for i, region_info in enumerate(detected_regions[:5]):  # Limit to top 5
                x1, y1, x2, y2 = region_info['bbox']
                
                # Extract region with padding
                padding = 5
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(image.shape[1], x2 + padding)
                y2 = min(image.shape[0], y2 + padding)
                
                region_image = image[y1:y2, x1:x2]
                
                if region_image.size == 0:
                    continue
                
                # Step 4: Preprocess region for OCR
                processed_variants = self.preprocessor.preprocess_text_region(
                    region_image, preprocessing_method
                )
                
                if not processed_variants:
                    continue
                
                # Step 5: Run OCR on all variants
                ocr_results = self.ocr_engine.recognize_text(processed_variants)
                
                if ocr_results:
                    region_results[f'region_{i}'] = {
                        'bbox': (x1, y1, x2, y2),
                        'detection_confidence': region_info['confidence'],
                        'ocr_results': ocr_results,
                        'best_text': self._select_best_text(ocr_results)
                    }
                    
                    best_text = region_results[f'region_{i}']['best_text']
                    if best_text:
                        all_texts.append(best_text)
            
            results['ocr_results'] = region_results
            
            # Step 6: Combine results
            if all_texts:
                results['final_text'] = self._combine_texts(all_texts)
                results['confidence'] = self._calculate_overall_confidence(region_results)
            
            return results
            
        except Exception as e:
            print(f"YOLO-OCR extraction error: {e}")
            results['error'] = str(e)
            return results
    
    def _select_best_text(self, ocr_results: Dict[str, str]) -> str:
        """Select best text from multiple OCR results"""
        if not ocr_results:
            return ""
        
        # Score each result
        scored_results = []
        for engine_variant, text in ocr_results.items():
            if not text or len(text.strip()) < 2:
                continue
            
            score = self._score_ocr_result(text, engine_variant)
            scored_results.append((score, text, engine_variant))
        
        if not scored_results:
            return ""
        
        # Return highest scoring result
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return scored_results[0][1]
    
    def _score_ocr_result(self, text: str, engine_variant: str) -> float:
        """Score OCR result based on quality and engine reliability"""
        score = 0.0
        text_clean = text.strip()
        
        if not text_clean:
            return 0.0
        
        # Length score (prefer 5-50 characters for IC markings)
        length = len(text_clean)
        if 5 <= length <= 50:
            score += 0.3
        elif 2 <= length < 5:
            score += 0.1
        elif length > 50:
            score -= 0.2
        
        # Alphanumeric content (IC markings have both letters and numbers)
        has_letters = any(c.isalpha() for c in text_clean)
        has_numbers = any(c.isdigit() for c in text_clean)
        if has_letters and has_numbers:
            score += 0.4
        elif has_letters or has_numbers:
            score += 0.1
        
        # Special character penalty
        special_count = sum(1 for c in text_clean if not c.isalnum() and c != ' ')
        special_ratio = special_count / len(text_clean)
        if special_ratio > 0.5:
            score -= 0.3
        
        # Engine reliability bonus
        if 'easyocr' in engine_variant:
            score += 0.2
        elif 'tesseract' in engine_variant:
            score += 0.1
        elif 'trocr' in engine_variant:
            score += 0.15
        
        # IC-specific patterns
        text_upper = text_clean.upper()
        if any(pattern in text_upper for pattern in ['ATMEGA', 'STM32', 'PIC', 'SN74', 'LM']):
            score += 0.3
        
        # Date code pattern
        if any(len(word) == 4 and word.isdigit() for word in text_clean.split()):
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _combine_texts(self, texts: List[str]) -> str:
        """Combine multiple text extractions intelligently"""
        if not texts:
            return ""
        
        if len(texts) == 1:
            return texts[0]
        
        # Join with newlines for now
        # In future, could implement intelligent merging
        return '\n'.join(texts)
    
    def _calculate_overall_confidence(self, region_results: Dict) -> float:
        """Calculate overall confidence from all regions"""
        if not region_results:
            return 0.0
        
        confidences = []
        for region_data in region_results.values():
            detection_conf = region_data.get('detection_confidence', 0.0)
            text_quality = self._score_ocr_result(region_data.get('best_text', ''), 'combined')
            combined_conf = (detection_conf + text_quality) / 2
            confidences.append(combined_conf)
        
        return sum(confidences) / len(confidences) if confidences else 0.0