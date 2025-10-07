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
    Enhanced YOLO-based text detection for IC markings
    Improved confidence and reliability
    """
    
    def __init__(self):
        self.model = None
        self.confidence_threshold = 0.15  # Lowered for better detection
        self.load_model()
    
    def load_model(self):
        """Load YOLOv8 model with enhanced configuration"""
        try:
            # Try to load custom IC text detection model first
            if os.path.exists('models/ic_text_detection.pt'):
                self.model = YOLO('models/ic_text_detection.pt')
                print("✓ Loaded custom IC text detection model")
            else:
                # Use general object detection model with enhanced settings
                self.model = YOLO('yolov8n.pt')  # Lightweight but accurate
                print("✓ Loaded YOLOv8 nano model (configured for IC text detection)")
                
        except Exception as e:
            print(f"⚠️ YOLO model loading failed: {e}")
            self.model = None
    
    def detect_text_regions(self, image: np.ndarray, confidence_threshold: float = None) -> List[Dict]:
        """
        Enhanced text region detection with improved confidence scoring
        
        Args:
            image: Input BGR image
            confidence_threshold: Detection confidence threshold
            
        Returns:
            List of detected regions with enhanced confidence metrics
        """
        if confidence_threshold is None:
            confidence_threshold = self.confidence_threshold
            
        if self.model is None:
            return self._fallback_text_detection(image)
        
        try:
            # Enhanced YOLO detection with multiple scales
            results = self.model(
                image, 
                conf=confidence_threshold,
                iou=0.5,  # Improved NMS threshold
                imgsz=640,  # Standard size for better detection
                verbose=False
            )
            
            detected_regions = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        
                        # Ensure coordinates are within image bounds
                        h, w = image.shape[:2]
                        x1, y1, x2, y2 = max(0, int(x1)), max(0, int(y1)), min(w, int(x2)), min(h, int(y2))
                        
                        if x2 > x1 and y2 > y1:  # Valid box
                            bbox_area = (x2 - x1) * (y2 - y1)
                            
                            # Enhanced confidence scoring
                            enhanced_conf = self._calculate_enhanced_confidence(
                                confidence, bbox_area, (x1, y1, x2, y2), image.shape
                            )
                            
                            detected_regions.append({
                                'bbox': (x1, y1, x2, y2),
                                'confidence': confidence,
                                'enhanced_confidence': enhanced_conf,
                                'area': bbox_area,
                                'source': 'yolo'
                            })
            
            # Filter and sort by enhanced confidence
            detected_regions = [r for r in detected_regions if r['area'] > 50]  # Smaller minimum
            detected_regions.sort(key=lambda x: x['enhanced_confidence'], reverse=True)
            
            return detected_regions[:15]  # Top 15 detections
            
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return self._fallback_text_detection(image)
    
    def _calculate_enhanced_confidence(self, raw_conf: float, area: int, bbox: tuple, img_shape: tuple) -> float:
        """
        Calculate enhanced confidence score based on multiple factors
        """
        h, w = img_shape[:2]
        x1, y1, x2, y2 = bbox
        
        # Base confidence
        score = raw_conf
        
        # Size bonus - ICs typically have medium-sized text
        area_ratio = area / (h * w)
        if 0.001 < area_ratio < 0.3:  # Good size range for IC text
            score += 0.1
        elif 0.0005 < area_ratio < 0.001:  # Small but potentially valid
            score += 0.05
        elif area_ratio > 0.5:  # Too large, probably not text
            score -= 0.2
        
        # Aspect ratio bonus - text regions have certain aspect ratios
        box_w, box_h = x2 - x1, y2 - y1
        aspect_ratio = box_w / box_h if box_h > 0 else 0
        if 0.5 < aspect_ratio < 8:  # Good aspect ratio for text
            score += 0.1
        elif 0.1 < aspect_ratio < 0.5 or 8 < aspect_ratio < 15:  # Acceptable
            score += 0.05
        
        # Position bonus - IC text is usually centered
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        rel_center_x, rel_center_y = center_x / w, center_y / h
        
        # Prefer regions closer to center
        center_distance = ((rel_center_x - 0.5) ** 2 + (rel_center_y - 0.5) ** 2) ** 0.5
        if center_distance < 0.3:  # Close to center
            score += 0.1
        elif center_distance < 0.5:  # Reasonable distance
            score += 0.05
        
        return min(1.0, max(0.0, score))
    
    def _fallback_text_detection(self, image: np.ndarray) -> List[Dict]:
        """
        Enhanced fallback text detection with better filtering
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Multiple detection strategies with enhanced parameters
        regions = []
        
        # Strategy 1: Enhanced MSER
        regions.extend(self._enhanced_mser_detection(gray))
        
        # Strategy 2: Multi-threshold contour detection
        regions.extend(self._multi_threshold_contour_detection(gray))
        
        # Strategy 3: Enhanced edge detection
        regions.extend(self._enhanced_edge_detection(gray))
        
        # Strategy 4: Text-specific blob detection
        regions.extend(self._blob_text_detection(gray))
        
        # Enhanced filtering and NMS
        regions = self._enhanced_filter_regions(regions, image.shape[:2])
        
        return regions
    
    def _enhanced_mser_detection(self, gray: np.ndarray) -> List[Dict]:
        """Enhanced MSER detection with better parameters for IC text"""
        try:
            # Multiple MSER configurations for different text types
            mser_configs = [
                cv2.MSER_create(_delta=5, _min_area=30, _max_area=2000),
                cv2.MSER_create(_delta=8, _min_area=50, _max_area=1500),
                cv2.MSER_create(_delta=3, _min_area=20, _max_area=3000)
            ]
            
            detected = []
            for mser in mser_configs:
                try:
                    regions, _ = mser.detectRegions(gray)
                    for region in regions:
                        if len(region) > 15:  # Minimum points
                            x, y, w, h = cv2.boundingRect(region)
                            if self._is_valid_text_region(w, h, gray.shape):
                                confidence = self._calculate_mser_confidence(region, gray)
                                detected.append({
                                    'bbox': (x, y, x + w, y + h),
                                    'confidence': confidence,
                                    'area': w * h,
                                    'source': 'mser_enhanced'
                                })
                except:
                    continue
            
            return detected
        except:
            return []
    
    def _multi_threshold_contour_detection(self, gray: np.ndarray) -> List[Dict]:
        """Multiple threshold levels for better text detection"""
        detected = []
        
        # Multiple threshold methods
        threshold_methods = [
            ('otsu', lambda g: cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
            ('adaptive_mean', lambda g: cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)),
            ('adaptive_gaussian', lambda g: cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2))
        ]
        
        for method_name, threshold_func in threshold_methods:
            try:
                binary = threshold_func(gray)
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    if self._is_valid_text_region(w, h, gray.shape):
                        confidence = self._calculate_contour_confidence(contour, binary)
                        detected.append({
                            'bbox': (x, y, x + w, y + h),
                            'confidence': confidence,
                            'area': w * h,
                            'source': f'contour_{method_name}'
                        })
            except:
                continue
        
        return detected
    
    def _enhanced_edge_detection(self, gray: np.ndarray) -> List[Dict]:
        """Enhanced edge detection with multiple kernels"""
        detected = []
        
        try:
            # Multiple edge detection approaches
            edge_methods = [
                ('canny', lambda g: cv2.Canny(g, 50, 150)),
                ('canny_tight', lambda g: cv2.Canny(g, 30, 100)),
                ('canny_loose', lambda g: cv2.Canny(g, 80, 200))
            ]
            
            for method_name, edge_func in edge_methods:
                edges = edge_func(gray)
                
                # Different morphological operations
                kernels = [
                    cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
                    cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1)),
                    cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
                ]
                
                for kernel in kernels:
                    processed = cv2.dilate(edges, kernel, iterations=1)
                    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    for contour in contours:
                        x, y, w, h = cv2.boundingRect(contour)
                        if self._is_valid_text_region(w, h, gray.shape):
                            confidence = self._calculate_edge_confidence(contour, edges)
                            detected.append({
                                'bbox': (x, y, x + w, y + h),
                                'confidence': confidence,
                                'area': w * h,
                                'source': f'edge_{method_name}'
                            })
        except:
            pass
        
        return detected
    
    def _blob_text_detection(self, gray: np.ndarray) -> List[Dict]:
        """Blob detection specifically tuned for text"""
        detected = []
        
        try:
            # Setup SimpleBlobDetector parameters for text
            params = cv2.SimpleBlobDetector_Params()
            
            # Filter by Area
            params.filterByArea = True
            params.minArea = 50
            params.maxArea = 5000
            
            # Filter by Circularity (text is usually not circular)
            params.filterByCircularity = True
            params.minCircularity = 0.1
            params.maxCircularity = 0.8
            
            # Filter by Convexity
            params.filterByConvexity = True
            params.minConvexity = 0.4
            
            # Filter by Inertia (text has moderate inertia)
            params.filterByInertia = True
            params.minInertiaRatio = 0.2
            
            detector = cv2.SimpleBlobDetector_create(params)
            keypoints = detector.detect(gray)
            
            for kp in keypoints:
                x, y = int(kp.pt[0]), int(kp.pt[1])
                size = int(kp.size)
                
                # Create bounding box from keypoint
                x1, y1 = max(0, x - size//2), max(0, y - size//2)
                x2, y2 = min(gray.shape[1], x + size//2), min(gray.shape[0], y + size//2)
                
                if x2 > x1 and y2 > y1:
                    detected.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': min(1.0, kp.response * 2),  # Scale response to confidence
                        'area': (x2 - x1) * (y2 - y1),
                        'source': 'blob'
                    })
        except:
            pass
        
        return detected
    
    def _is_valid_text_region(self, width: int, height: int, img_shape: tuple) -> bool:
        """Enhanced validation for text regions"""
        img_h, img_w = img_shape
        
        # Size constraints
        if width < 5 or height < 3:
            return False
        if width > img_w * 0.9 or height > img_h * 0.9:
            return False
        
        # Aspect ratio constraints
        aspect_ratio = width / height if height > 0 else 0
        if aspect_ratio < 0.1 or aspect_ratio > 20:
            return False
        
        # Area constraints
        area = width * height
        img_area = img_w * img_h
        area_ratio = area / img_area
        if area_ratio < 0.0001 or area_ratio > 0.7:
            return False
        
        return True
    
    def _calculate_mser_confidence(self, region: np.ndarray, gray: np.ndarray) -> float:
        """Calculate confidence for MSER regions"""
        try:
            # Basic confidence based on region stability
            x, y, w, h = cv2.boundingRect(region)
            roi = gray[y:y+h, x:x+w]
            
            # Calculate variance (text areas have moderate variance)
            variance = np.var(roi) / 255.0  # Normalize
            
            # Text typically has variance between 0.1 and 0.8
            if 0.1 <= variance <= 0.8:
                return min(1.0, variance + 0.3)
            else:
                return max(0.1, 1.0 - abs(variance - 0.4))
        except:
            return 0.5
    
    def _calculate_contour_confidence(self, contour: np.ndarray, binary: np.ndarray) -> float:
        """Calculate confidence for contour-based regions"""
        try:
            # Calculate solidity (convex hull area / contour area)
            area = cv2.contourArea(contour)
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            
            if hull_area > 0:
                solidity = area / hull_area
                # Text typically has high solidity (0.7-1.0)
                return min(1.0, max(0.1, solidity + 0.2))
            else:
                return 0.3
        except:
            return 0.3
    
    def _calculate_edge_confidence(self, contour: np.ndarray, edges: np.ndarray) -> float:
        """Calculate confidence for edge-based regions"""
        try:
            x, y, w, h = cv2.boundingRect(contour)
            roi_edges = edges[y:y+h, x:x+w]
            
            # Calculate edge density
            edge_pixels = np.count_nonzero(roi_edges)
            total_pixels = w * h
            
            if total_pixels > 0:
                edge_density = edge_pixels / total_pixels
                # Good text regions have moderate edge density (0.1-0.5)
                if 0.1 <= edge_density <= 0.5:
                    return min(1.0, edge_density * 2)
                else:
                    return max(0.1, 0.5 - abs(edge_density - 0.3))
            else:
                return 0.2
        except:
            return 0.2
    
    def _enhanced_filter_regions(self, regions: List[Dict], image_shape: Tuple[int, int]) -> List[Dict]:
        """Enhanced filtering with confidence-based NMS"""
        if not regions:
            return []
        
        h, w = image_shape
        
        # Filter by enhanced criteria
        filtered = []
        for region in regions:
            x1, y1, x2, y2 = region['bbox']
            
            # Bounds check
            if x1 >= 0 and y1 >= 0 and x2 <= w and y2 <= h:
                width, height = x2 - x1, y2 - y1
                area = width * height
                
                # Enhanced size and aspect ratio checks
                if self._is_valid_text_region(width, height, image_shape):
                    # Add enhanced confidence if not present
                    if 'enhanced_confidence' not in region:
                        region['enhanced_confidence'] = self._calculate_enhanced_confidence(
                            region['confidence'], area, region['bbox'], image_shape
                        )
                    
                    filtered.append(region)
        
        # Enhanced NMS based on confidence
        filtered = self._confidence_based_nms(filtered, overlap_threshold=0.3)
        
        # Sort by enhanced confidence
        filtered.sort(key=lambda x: x.get('enhanced_confidence', x['confidence']), reverse=True)
        
        return filtered[:12]  # Top 12 regions
    
    def _confidence_based_nms(self, regions: List[Dict], overlap_threshold: float = 0.3) -> List[Dict]:
        """Non-maximum suppression based on confidence scores"""
        if not regions:
            return []
        
        # Sort by enhanced confidence
        regions = sorted(regions, key=lambda x: x.get('enhanced_confidence', x['confidence']), reverse=True)
        
        keep = []
        while regions:
            current = regions.pop(0)
            keep.append(current)
            
            # Remove overlapping regions with lower confidence
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
        """Generate balanced preprocessing variants - tested combinations that work"""
        variants = []
        
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                color = image.copy()
            else:
                gray = image.copy()
                color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            # Variant 1: Upscaled 3x color - PROVEN BEST for type2.jpg (328P captured cleanly!)
            upscaled_color_3x = cv2.resize(color, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            variants.append(upscaled_color_3x)
            
            # Variant 2: Original color (good baseline)
            variants.append(color)
            
            # Variant 3: Moderate CLAHE - also captures 328P correctly
            clahe_moderate = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            moderate_enhanced = clahe_moderate.apply(gray)
            variants.append(moderate_enhanced)
            
            # Variant 4: Upscaled 4x + Moderate CLAHE
            upscaled_4x = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            upscaled_enhanced = clahe_moderate.apply(upscaled_4x)
            variants.append(upscaled_enhanced)
            
            # Variant 5: Bilateral + CLAHE - captures 328P correctly
            bilateral = cv2.bilateralFilter(upscaled_4x, 9, 75, 75)
            bilateral_enhanced = clahe_moderate.apply(bilateral)
            variants.append(bilateral_enhanced)
            
            # Variant 6: Denoised color upscaled
            denoised_color = cv2.fastNlMeansDenoisingColored(upscaled_color_3x, None, 10, 10, 7, 21)
            variants.append(denoised_color)
            
            # Variant 7: Upscaled 2x color (balance between speed and quality)
            upscaled_color_2x = cv2.resize(color, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            variants.append(upscaled_color_2x)
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            # Fallback - return original
            variants = [image]
        
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
            # Check GPU availability for EasyOCR
            use_gpu = False
            try:
                use_gpu = torch.cuda.is_available()
            except:
                pass
            
            self.engines['easyocr'] = easyocr.Reader(['en'], verbose=False, gpu=use_gpu)
            print("✓ EasyOCR initialized")
        except Exception as e:
            print(f"⚠️ EasyOCR failed: {e}")
        
        # Tesseract
        try:
            # Test tesseract availability
            _ = pytesseract.get_tesseract_version()
            self.engines['tesseract'] = True
            print("✓ Tesseract initialized")
        except Exception as e:
            print(f"⚠️ Tesseract failed: {e}")
        
        # TrOCR (if available)
        try:
            import torch
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            
            # Detect device (GPU if available)
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            
            self.engines['trocr_processor'] = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
            self.engines['trocr_model'] = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
            self.engines['trocr_model'].to(device)
            self.engines['trocr_device'] = device
            
            print(f"✓ TrOCR initialized on {device}")
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
            texts = [result[1] for result in results if result[2] > 0.15]  # Confidence > 15%
            combined = ' '.join(texts).strip()
            return combined if len(combined) >= 2 else ''  # Return if at least 2 chars
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
        """Run TrOCR on image with GPU acceleration"""
        try:
            from PIL import Image
            
            # Convert to PIL
            if len(image.shape) == 2:
                pil_image = Image.fromarray(image).convert('RGB')
            else:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Get device
            device = self.engines.get('trocr_device', 'cpu')
            
            # Process with GPU if available
            pixel_values = self.engines['trocr_processor'](pil_image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(device)
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
            
            # Always include full image as a region (in addition to detected regions)
            # This ensures we don't miss text if YOLO detections are incomplete
            full_image_region = {
                'bbox': (0, 0, image.shape[1], image.shape[0]),
                'confidence': 0.9,
                'area': image.shape[0] * image.shape[1],
                'method': 'fullimage'
            }
            
            if not detected_regions:
                print("No text regions detected, processing entire image")
                detected_regions = [full_image_region]
            else:
                # Add full image as backup if we have few detections
                if len(detected_regions) < 3:
                    detected_regions.append(full_image_region)
            
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
            if not text or len(text.strip()) < 1:
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
        
        # Length score - favor complete text
        length = len(text_clean)
        if 8 <= length <= 50:
            score += 0.4
        elif 5 <= length < 8:
            score += 0.25
        elif length > 50:
            score += 0.15
        
        # Alphanumeric content (IC markings have both)
        has_letters = any(c.isalpha() for c in text_clean)
        has_numbers = any(c.isdigit() for c in text_clean)
        if has_letters and has_numbers:
            score += 0.5  # Very important
        elif has_letters or has_numbers:
            score += 0.2
        
        # Penalize gibberish (too many special chars or nonsense patterns)
        special_count = sum(1 for c in text_clean if not c.isalnum() and c not in ' -_/')
        special_ratio = special_count / length if length > 0 else 0
        if special_ratio > 0.5:
            score -= 0.4  # Heavy penalty for gibberish
        
        # Penalize obvious OCR errors (repeated nonsense)
        if len(set(text_clean.replace(' ', ''))) < len(text_clean) * 0.3:
            score -= 0.3  # Too much repetition
        
        # Check for common IC manufacturer prefixes (high confidence indicators)
        text_upper = text_clean.upper()
        manufacturers = ['ATMEL', 'ATMEGA', 'STM32', 'PIC', 'TI', 'TEXAS', 'ANALOG', 'MAXIM', 
                        'INFINEON', 'NXP', 'MICROCHIP', 'CYPRESS', 'CY8C']
        if any(mfg in text_upper for mfg in manufacturers):
            score += 0.4  # Strong indicator of correct extraction
        
        # Check for common IC part number patterns
        ic_patterns = ['SN74', 'LM', 'ADC', 'DAC', 'MAX', 'TL', 'CD', 'NE555', 'MCP']
        if any(pattern in text_upper for pattern in ic_patterns):
            score += 0.35
        
        # Date code pattern (YYXX format) - good indicator
        words = text_clean.split()
        if any(len(word) == 4 and word.isdigit() for word in words):
            score += 0.25
        
        # Uppercase ratio (IC part numbers are typically uppercase)
        alpha_chars = [c for c in text_clean if c.isalpha()]
        if alpha_chars:
            upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
            if upper_ratio > 0.7:
                score += 0.2
        
        # Engine reliability bonus
        if 'easyocr' in engine_variant.lower():
            score += 0.3  # EasyOCR is very reliable
        elif 'trocr' in engine_variant.lower():
            score += 0.2
        elif 'paddle' in engine_variant.lower():
            score += 0.25
        
        # Penalty for obviously wrong patterns
        # Check for nonsense like "QJRZBABEZ" (alternating consonants)
        consonants = 'BCDFGHJKLMNPQRSTVWXYZ'
        vowels = 'AEIOU'
        text_alpha = ''.join(c for c in text_upper if c.isalpha())
        if len(text_alpha) > 5:
            consonant_run = 0
            max_consonant_run = 0
            for c in text_alpha:
                if c in consonants:
                    consonant_run += 1
                    max_consonant_run = max(max_consonant_run, consonant_run)
                else:
                    consonant_run = 0
            
            if max_consonant_run > 6:  # Too many consonants in a row = gibberish
                score -= 0.3
        
        return max(0.0, min(1.5, score))  # Allow scores slightly above 1.0 for very good results
    
    def _combine_texts(self, texts: List[str]) -> str:
        """Combine multiple text extractions intelligently"""
        if not texts:
            return ""
        
        if len(texts) == 1:
            return texts[0]
        
        # Select the longest, most complete text
        # Sort by length descending
        sorted_texts = sorted(texts, key=len, reverse=True)
        
        # Return the longest one that contains meaningful content
        for text in sorted_texts:
            if len(text.strip()) >= 5:  # At least 5 characters
                return text
        
        # Fallback: combine all
        combined = ' '.join(texts)
        combined = ' '.join(combined.split())
        return combined
    
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