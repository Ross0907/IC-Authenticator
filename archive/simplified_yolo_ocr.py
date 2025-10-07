"""
Simplified Dynamic YOLO-OCR System for IC Authentication
Works with any IC image type and resolution using intelligent text detection

This system provides:
1. Adaptive text detection (YOLO + fallback methods)
2. Multi-resolution preprocessing  
3. Multi-engine OCR (EasyOCR, Tesseract, PaddleOCR)
4. Quality-based result selection
5. IC pattern extraction
"""

import cv2
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings

# Suppress warnings for clean output
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  YOLO not available, using fallback detection")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️  EasyOCR not available")

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("⚠️  PaddleOCR not available")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  Tesseract not available")


class SmartTextDetector:
    """
    Smart text detection using multiple methods
    Falls back gracefully when YOLO is not available
    """
    
    def __init__(self):
        self.yolo_model = None
        self.init_yolo()
    
    def init_yolo(self):
        """Initialize YOLO model if available"""
        if YOLO_AVAILABLE:
            try:
                self.yolo_model = YOLO('yolov8n.pt')
                print("✓ YOLO model loaded successfully")
            except Exception as e:
                print(f"⚠️  YOLO initialization failed: {e}")
                self.yolo_model = None
        else:
            print("ℹ️  Using traditional computer vision for text detection")
    
    def detect_text_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Detect text regions using best available method
        Returns list of bounding boxes with confidence scores
        """
        if self.yolo_model is not None:
            return self._yolo_detection(image)
        else:
            return self._traditional_detection(image)
    
    def _yolo_detection(self, image: np.ndarray) -> List[Dict]:
        """YOLO-based text detection"""
        try:
            # Ensure image has 3 channels (RGB) for YOLO
            if len(image.shape) == 2:
                # Grayscale to RGB
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 1:
                # Single channel to RGB
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 4:
                # RGBA to RGB
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            elif len(image.shape) == 3 and image.shape[2] == 3:
                # Already RGB, but make sure it's BGR to RGB for YOLO
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            results = self.yolo_model(image, conf=0.25, verbose=False)
            
            regions = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        
                        h, w = image.shape[:2]
                        x1, y1, x2, y2 = max(0, int(x1)), max(0, int(y1)), min(w, int(x2)), min(h, int(y2))
                        
                        if x2 > x1 and y2 > y1:
                            regions.append({
                                'bbox': (x1, y1, x2, y2),
                                'confidence': float(confidence),
                                'method': 'yolo'
                            })
            
            # Sort by confidence
            regions.sort(key=lambda x: x['confidence'], reverse=True)
            return regions[:10]
            
        except Exception as e:
            print(f"YOLO detection error: {e}, falling back to traditional methods")
            return self._traditional_detection(image)
    
    def _traditional_detection(self, image: np.ndarray) -> List[Dict]:
        """Traditional computer vision text detection"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        regions = []
        
        # Method 1: MSER (Maximally Stable Extremal Regions)
        try:
            mser = cv2.MSER_create()
            mser_regions, _ = mser.detectRegions(gray)
            
            for region in mser_regions:
                if len(region) > 15:
                    x, y, w, h = cv2.boundingRect(region)
                    if 10 < w < gray.shape[1] * 0.8 and 5 < h < gray.shape[0] * 0.8:
                        regions.append({
                            'bbox': (x, y, x + w, y + h),
                            'confidence': 0.7,
                            'method': 'mser'
                        })
        except:
            pass
        
        # Method 2: Contour detection
        try:
            # Multiple thresholding approaches
            thresh_methods = [
                cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
                cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1],
                cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            ]
            
            for binary in thresh_methods:
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = w * h
                    aspect_ratio = w / h if h > 0 else 0
                    
                    if (0.1 < aspect_ratio < 20 and 
                        100 < area < gray.shape[0] * gray.shape[1] * 0.5 and
                        w > 15 and h > 8):
                        
                        regions.append({
                            'bbox': (x, y, x + w, y + h),
                            'confidence': 0.6,
                            'method': 'contour'
                        })
        except:
            pass
        
        # Method 3: Edge-based detection
        try:
            edges = cv2.Canny(gray, 50, 150)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 20 and h > 10 and w * h > 300:
                    regions.append({
                        'bbox': (x, y, x + w, y + h),
                        'confidence': 0.5,
                        'method': 'edge'
                    })
        except:
            pass
        
        # Remove overlapping regions and filter
        regions = self._filter_regions(regions, gray.shape)
        return regions[:15]
    
    def _filter_regions(self, regions: List[Dict], image_shape: Tuple[int, int]) -> List[Dict]:
        """Filter and deduplicate regions"""
        if not regions:
            return []
        
        h, w = image_shape
        
        # Filter by size
        filtered = []
        for region in regions:
            x1, y1, x2, y2 = region['bbox']
            if (0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h and
                (x2 - x1) > 10 and (y2 - y1) > 5):
                filtered.append(region)
        
        # Simple non-maximum suppression
        filtered.sort(key=lambda x: x['confidence'], reverse=True)
        
        keep = []
        for region in filtered:
            overlap = False
            for kept in keep:
                if self._calculate_overlap(region['bbox'], kept['bbox']) > 0.3:
                    overlap = True
                    break
            if not overlap:
                keep.append(region)
        
        return keep
    
    def _calculate_overlap(self, box1: Tuple[int, int, int, int], 
                          box2: Tuple[int, int, int, int]) -> float:
        """Calculate IoU overlap"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
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


class AdaptiveImageProcessor:
    """
    Adaptive image preprocessing for different IC types and resolutions
    """
    
    def __init__(self):
        pass
    
    def preprocess_for_detection(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for text detection"""
        # Ensure proper channel format for YOLO (RGB)
        if len(image.shape) == 2:
            # Grayscale to RGB
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif len(image.shape) == 3:
            if image.shape[2] == 1:
                # Single channel to RGB  
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                # RGBA to RGB
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            elif image.shape[2] == 3:
                # Assume BGR, convert to RGB for YOLO
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize if too large (keep aspect ratio)
        h, w = image.shape[:2]
        max_size = 1024
        
        if max(h, w) > max_size:
            if h > w:
                new_h = max_size
                new_w = int(w * max_size / h)
            else:
                new_w = max_size
                new_h = int(h * max_size / w)
            image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        return image
    
    def preprocess_for_ocr(self, region: np.ndarray) -> List[np.ndarray]:
        """Create multiple variants of image region for OCR"""
        if region.size == 0:
            return []
        
        # Ensure minimum size for OCR
        h, w = region.shape[:2]
        if h < 32:
            scale = 32 / h
            new_w = int(w * scale)
            region = cv2.resize(region, (new_w, 32), interpolation=cv2.INTER_CUBIC)
        
        variants = []
        
        # Convert to grayscale if needed
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        else:
            gray = region.copy()
        
        try:
            # Variant 1: CLAHE enhancement
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
            enhanced = clahe.apply(gray)
            variants.append(enhanced)
            
            # Variant 2: Adaptive threshold
            adaptive = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                           cv2.THRESH_BINARY, 11, 2)
            variants.append(adaptive)
            
            # Variant 3: Otsu threshold
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append(otsu)
            
            # Variant 4: Inverted
            _, inv_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            variants.append(inv_otsu)
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            variants = [gray]
        
        return variants


class MultiEngineOCR:
    """
    Multi-engine OCR system that adapts based on available engines
    """
    
    def __init__(self):
        self.engines = {}
        self.init_engines()
    
    def init_engines(self):
        """Initialize available OCR engines"""
        # EasyOCR
        if EASYOCR_AVAILABLE:
            try:
                self.engines['easyocr'] = easyocr.Reader(['en'], verbose=False)
                print("✓ EasyOCR initialized")
            except Exception as e:
                print(f"⚠️  EasyOCR failed: {e}")
        
        # PaddleOCR
        if PADDLEOCR_AVAILABLE:
            try:
                self.engines['paddleocr'] = PaddleOCR(use_angle_cls=True, lang='en')
                print("✓ PaddleOCR initialized")
            except Exception as e:
                print(f"⚠️  PaddleOCR failed: {e}")
        
        # Tesseract
        if TESSERACT_AVAILABLE:
            try:
                # Test if tesseract is available
                pytesseract.image_to_string(np.ones((10, 10), dtype=np.uint8))
                self.engines['tesseract'] = True
                print("✓ Tesseract initialized")
            except Exception as e:
                print(f"⚠️  Tesseract failed: {e}")
        
        if not self.engines:
            print("❌ No OCR engines available!")
    
    def recognize_text(self, image_variants: List[np.ndarray]) -> Dict[str, str]:
        """Run OCR on all image variants using all available engines"""
        results = {}
        
        for i, image in enumerate(image_variants):
            # EasyOCR
            if 'easyocr' in self.engines:
                text = self._run_easyocr(image)
                if text:
                    results[f'easyocr_v{i}'] = text
            
            # PaddleOCR
            if 'paddleocr' in self.engines:
                text = self._run_paddleocr(image)
                if text:
                    results[f'paddleocr_v{i}'] = text
            
            # Tesseract
            if 'tesseract' in self.engines:
                text = self._run_tesseract(image)
                if text:
                    results[f'tesseract_v{i}'] = text
        
        return results
    
    def _run_easyocr(self, image: np.ndarray) -> str:
        """Run EasyOCR"""
        try:
            results = self.engines['easyocr'].readtext(image)
            texts = [result[1] for result in results if result[2] > 0.3]
            return ' '.join(texts).strip()
        except:
            return ""
    
    def _run_paddleocr(self, image: np.ndarray) -> str:
        """Run PaddleOCR"""
        try:
            results = self.engines['paddleocr'].ocr(image, cls=True)
            texts = []
            if results and results[0]:
                for line in results[0]:
                    if line[1][1] > 0.3:  # Confidence threshold
                        texts.append(line[1][0])
            return ' '.join(texts).strip()
        except:
            return ""
    
    def _run_tesseract(self, image: np.ndarray) -> str:
        """Run Tesseract"""
        try:
            # Try different PSM modes
            psm_modes = [6, 7, 8, 13]
            best_text = ""
            
            for psm in psm_modes:
                config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                text = pytesseract.image_to_string(image, config=config).strip()
                if len(text) > len(best_text):
                    best_text = text
            
            return best_text
        except:
            return ""


class SimplifiedYOLOOCR:
    """
    Main system that combines detection, preprocessing, and OCR
    """
    
    def __init__(self):
        self.detector = SmartTextDetector()
        self.processor = AdaptiveImageProcessor()
        self.ocr = MultiEngineOCR()
        
        print("🚀 Simplified YOLO-OCR system ready!")
    
    def extract_text(self, image: np.ndarray) -> Dict:
        """Extract text from IC image"""
        results = {
            'regions': [],
            'texts': [],
            'best_text': '',
            'confidence': 0.0
        }
        
        try:
            # Step 1: Preprocess for detection
            detection_image = self.processor.preprocess_for_detection(image.copy())
            
            # Step 2: Detect text regions
            regions = self.detector.detect_text_regions(detection_image)
            
            if not regions:
                # Fallback: process entire image
                h, w = image.shape[:2]
                regions = [{'bbox': (0, 0, w, h), 'confidence': 1.0, 'method': 'fullimage'}]
            
            results['regions'] = regions
            
            # Step 3: Process each region
            all_texts = []
            
            for region_info in regions[:5]:  # Top 5 regions
                x1, y1, x2, y2 = region_info['bbox']
                
                # Add padding
                padding = 5
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(image.shape[1], x2 + padding)
                y2 = min(image.shape[0], y2 + padding)
                
                region_image = image[y1:y2, x1:x2]
                
                if region_image.size == 0:
                    continue
                
                # Step 4: Preprocess for OCR
                variants = self.processor.preprocess_for_ocr(region_image)
                
                if not variants:
                    continue
                
                # Step 5: Run OCR
                ocr_results = self.ocr.recognize_text(variants)
                
                # Step 6: Select best result
                best_text = self._select_best_result(ocr_results)
                
                if best_text:
                    all_texts.append(best_text)
            
            results['texts'] = all_texts
            
            # Combine all texts
            if all_texts:
                results['best_text'] = '\n'.join(all_texts)
                results['confidence'] = 0.8  # Simplified confidence
            
            return results
            
        except Exception as e:
            print(f"Error in text extraction: {e}")
            results['error'] = str(e)
            return results
    
    def _select_best_result(self, ocr_results: Dict[str, str]) -> str:
        """Select best OCR result"""
        if not ocr_results:
            return ""
        
        # Score each result
        scored = []
        for engine, text in ocr_results.items():
            if text and len(text.strip()) >= 2:
                score = self._score_text(text, engine)
                scored.append((score, text))
        
        if not scored:
            return ""
        
        # Return highest scoring
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]
    
    def _score_text(self, text: str, engine: str) -> float:
        """Score OCR result quality"""
        score = 0.0
        text_clean = text.strip()
        
        if not text_clean:
            return 0.0
        
        # Length score
        length = len(text_clean)
        if 3 <= length <= 50:
            score += 0.3
        
        # Content score
        has_letters = any(c.isalpha() for c in text_clean)
        has_numbers = any(c.isdigit() for c in text_clean)
        if has_letters and has_numbers:
            score += 0.4
        elif has_letters or has_numbers:
            score += 0.2
        
        # Engine reliability
        if 'easyocr' in engine:
            score += 0.3
        elif 'paddleocr' in engine:
            score += 0.2
        elif 'tesseract' in engine:
            score += 0.1
        
        return score


# Import pattern extractor if available
try:
    from ic_marking_extractor import ICMarkingExtractor
    PATTERN_EXTRACTOR_AVAILABLE = True
except ImportError:
    PATTERN_EXTRACTOR_AVAILABLE = False
    print("⚠️  IC pattern extractor not available")


def test_simplified_system():
    """Test the simplified system"""
    print("🧪 Testing Simplified YOLO-OCR System")
    print("=" * 50)
    
    # Initialize
    yolo_ocr = SimplifiedYOLOOCR()
    
    if PATTERN_EXTRACTOR_AVAILABLE:
        pattern_extractor = ICMarkingExtractor()
    else:
        pattern_extractor = None
    
    # Test directory
    test_dir = "test_images"
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return
    
    # Find test images
    image_files = []
    for ext in ['.png', '.jpg', '.jpeg']:
        image_files.extend([f for f in os.listdir(test_dir) if f.lower().endswith(ext)])
    
    if not image_files:
        print(f"❌ No images found in {test_dir}")
        return
    
    print(f"📁 Found {len(image_files)} test images")
    
    # Test each image
    results = {}
    
    for image_file in image_files:
        image_path = os.path.join(test_dir, image_file)
        print(f"\n🖼️  Testing: {image_file}")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ Could not load {image_file}")
                continue
            
            print(f"📐 Image size: {image.shape}")
            
            # Extract text
            result = yolo_ocr.extract_text(image)
            
            print(f"🔍 Detected {len(result['regions'])} regions")
            print(f"📝 Extracted text: '{result['best_text']}'")
            
            # Pattern extraction if available
            if pattern_extractor and result['best_text']:
                patterns = pattern_extractor.parse_ic_marking(result['best_text'])
                print(f"🏭 Manufacturer: {patterns.get('manufacturer', 'Unknown')}")
                print(f"🔧 Part: {patterns.get('part_number', 'Unknown')}")
                print(f"📅 Date: {patterns.get('date_code', 'Unknown')}")
                result['patterns'] = patterns
            
            results[image_file] = result
            
        except Exception as e:
            print(f"❌ Error processing {image_file}: {e}")
            results[image_file] = {'error': str(e)}
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    
    successful = 0
    for image_file, result in results.items():
        if 'best_text' in result and result['best_text']:
            print(f"✅ {image_file}: '{result['best_text'][:50]}...'")
            successful += 1
        else:
            print(f"❌ {image_file}: No text extracted")
    
    print(f"\n✓ Success rate: {successful}/{len(image_files)} ({successful/len(image_files)*100:.1f}%)")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"simplified_yolo_results_{timestamp}.json"
    
    try:
        # Convert numpy arrays to lists for JSON
        def convert_for_json(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            else:
                return obj
        
        json_results = convert_for_json(results)
        
        with open(results_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"💾 Results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")


if __name__ == "__main__":
    test_simplified_system()