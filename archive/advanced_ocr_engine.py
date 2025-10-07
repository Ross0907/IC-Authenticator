"""
Advanced OCR Engine Module
Implements multiple state-of-the-art OCR techniques for IC text detection
Including: MMOCR, TrOCR, CRAFT, and specialized IC text detection methods
"""

import cv2
import numpy as np
import re
from typing import List, Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')


class AdvancedOCREngine:
    """
    Advanced OCR engine with multiple specialized methods for IC text detection
    """
    
    def __init__(self):
        self.available_methods = []
        
        # Initialize MMOCR (if available)
        try:
            from mmocr.apis import MMOCRInferencer
            self.mmocr_inferencer = MMOCRInferencer(det='DBNet', rec='SAR')
            self.available_methods.append('mmocr')
            print("✓ MMOCR initialized successfully")
        except Exception as e:
            print(f"✗ MMOCR not available: {e}")
            self.mmocr_inferencer = None
        
        # Initialize TrOCR (Transformer-based OCR)
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            from PIL import Image
            self.trocr_processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
            self.trocr_model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
            self.available_methods.append('trocr')
            print("✓ TrOCR initialized successfully")
        except Exception as e:
            print(f"✗ TrOCR not available: {e}")
            self.trocr_processor = None
            self.trocr_model = None
        
        # Initialize CRAFT (Character Region Awareness)
        try:
            import torch
            from craft_text_detector import Craft
            self.craft_detector = Craft(output_dir=None, cuda=False)
            self.available_methods.append('craft')
            print("✓ CRAFT initialized successfully")
        except Exception as e:
            print(f"✗ CRAFT not available: {e}")
            self.craft_detector = None
        
        # Initialize KerasOCR (alternative OCR)
        try:
            import keras_ocr
            self.keras_pipeline = keras_ocr.pipeline.Pipeline()
            self.available_methods.append('keras_ocr')
            print("✓ Keras-OCR initialized successfully")
        except Exception as e:
            print(f"✗ Keras-OCR not available: {e}")
            self.keras_pipeline = None
        
        # Initialize docTR (Document Text Recognition)
        try:
            from doctr.models import ocr_predictor
            from doctr.io import DocumentFile
            self.doctr_model = ocr_predictor(pretrained=True)
            self.available_methods.append('doctr')
            print("✓ docTR initialized successfully")
        except Exception as e:
            print(f"✗ docTR not available: {e}")
            self.doctr_model = None
        
        print(f"\nAvailable OCR methods: {', '.join(self.available_methods)}")
    
    def preprocess_for_ic_text(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Advanced preprocessing specifically for IC text
        Returns multiple preprocessed versions for ensemble voting
        """
        preprocessed_images = []
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Method 1: CLAHE + Bilateral Filter
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
        preprocessed_images.append(bilateral)
        
        # Method 2: Adaptive Histogram Equalization
        adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        preprocessed_images.append(adaptive)
        
        # Method 3: Morphological Enhancement
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        preprocessed_images.append(morph)
        
        # Method 4: Unsharp Masking (for better edge definition)
        gaussian = cv2.GaussianBlur(gray, (0, 0), 2.0)
        unsharp = cv2.addWeighted(gray, 2.0, gaussian, -1.0, 0)
        preprocessed_images.append(unsharp)
        
        # Method 5: Contrast Limited + Denoising
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        preprocessed_images.append(denoised)
        
        return preprocessed_images
    
    def extract_with_mmocr(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using MMOCR (specialized for scene text)"""
        if self.mmocr_inferencer is None:
            return {'text': '', 'confidence': 0, 'lines': []}
        
        try:
            # MMOCR expects image path or numpy array
            result = self.mmocr_inferencer(image, return_vis=False)
            
            # Extract text and bounding boxes
            predictions = result['predictions'][0]
            texts = []
            confidences = []
            
            for pred in predictions['rec_texts']:
                texts.append(pred)
            
            for pred in predictions['rec_scores']:
                confidences.append(pred)
            
            # Sort by Y-coordinate to maintain line order
            combined = list(zip(texts, confidences, predictions['det_polygons']))
            combined.sort(key=lambda x: min(p[1] for p in x[2]))
            
            # Group by lines
            lines = self._group_by_lines([x[0] for x in combined], 
                                        [x[2] for x in combined])
            
            return {
                'text': '\n'.join(lines),
                'confidence': np.mean(confidences) if confidences else 0,
                'lines': lines,
                'method': 'mmocr'
            }
        except Exception as e:
            print(f"MMOCR extraction error: {e}")
            return {'text': '', 'confidence': 0, 'lines': []}
    
    def extract_with_trocr(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using TrOCR (Transformer-based OCR)"""
        if self.trocr_processor is None or self.trocr_model is None:
            return {'text': '', 'confidence': 0, 'lines': []}
        
        try:
            from PIL import Image
            
            # Convert numpy array to PIL Image
            if len(image.shape) == 2:
                pil_image = Image.fromarray(image).convert('RGB')
            else:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Process image
            pixel_values = self.trocr_processor(pil_image, return_tensors="pt").pixel_values
            
            # Generate text
            generated_ids = self.trocr_model.generate(pixel_values)
            generated_text = self.trocr_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return {
                'text': generated_text,
                'confidence': 0.8,  # TrOCR doesn't provide confidence scores
                'lines': [generated_text],
                'method': 'trocr'
            }
        except Exception as e:
            print(f"TrOCR extraction error: {e}")
            return {'text': '', 'confidence': 0, 'lines': []}
    
    def extract_with_craft(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using CRAFT (Character Region Awareness)"""
        if self.craft_detector is None:
            return {'text': '', 'confidence': 0, 'lines': []}
        
        try:
            # CRAFT detects text regions
            prediction_result = self.craft_detector.detect_text(image)
            
            # Extract regions and use secondary OCR for recognition
            texts = []
            boxes = prediction_result['boxes']
            
            for box in boxes:
                x1, y1, x2, y2 = box
                roi = image[int(y1):int(y2), int(x1):int(x2)]
                
                # Use simple OCR on detected region (you can replace with better OCR)
                text = self._simple_ocr_on_roi(roi)
                if text:
                    texts.append(text)
            
            return {
                'text': ' '.join(texts),
                'confidence': 0.75,
                'lines': texts,
                'method': 'craft'
            }
        except Exception as e:
            print(f"CRAFT extraction error: {e}")
            return {'text': '', 'confidence': 0, 'lines': []}
    
    def extract_with_keras_ocr(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using Keras-OCR"""
        if self.keras_pipeline is None:
            return {'text': '', 'confidence': 0, 'lines': []}
        
        try:
            # Keras-OCR expects RGB image
            if len(image.shape) == 2:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Run prediction
            prediction_groups = self.keras_pipeline.recognize([rgb_image])
            predictions = prediction_groups[0]
            
            # Extract text and sort by position
            texts_with_pos = [(pred[0], pred[1]) for pred in predictions]
            texts_with_pos.sort(key=lambda x: x[1][0][1])  # Sort by Y coordinate
            
            texts = [t[0] for t in texts_with_pos]
            
            return {
                'text': ' '.join(texts),
                'confidence': 0.8,
                'lines': texts,
                'method': 'keras_ocr'
            }
        except Exception as e:
            print(f"Keras-OCR extraction error: {e}")
            return {'text': '', 'confidence': 0, 'lines': []}
    
    def extract_with_doctr(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text using docTR"""
        if self.doctr_model is None:
            return {'text': '', 'confidence': 0, 'lines': []}
        
        try:
            from doctr.io import DocumentFile
            
            # Convert image for docTR
            if len(image.shape) == 2:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            else:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Create document
            doc = DocumentFile.from_images([rgb_image])
            
            # Run OCR
            result = self.doctr_model(doc)
            
            # Extract text
            texts = []
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        line_text = ' '.join([word.value for word in line.words])
                        if line_text.strip():
                            texts.append(line_text)
            
            return {
                'text': '\n'.join(texts),
                'confidence': 0.85,
                'lines': texts,
                'method': 'doctr'
            }
        except Exception as e:
            print(f"docTR extraction error: {e}")
            return {'text': '', 'confidence': 0, 'lines': []}
    
    def extract_with_ensemble(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Run all available OCR methods and combine results
        Uses weighted voting based on confidence scores
        """
        all_results = []
        
        # Preprocess image
        preprocessed = self.preprocess_for_ic_text(image)
        
        # Run all available methods
        if 'mmocr' in self.available_methods:
            result = self.extract_with_mmocr(preprocessed[0])
            if result['confidence'] > 0:
                all_results.append(result)
        
        if 'trocr' in self.available_methods:
            result = self.extract_with_trocr(preprocessed[1])
            if result['confidence'] > 0:
                all_results.append(result)
        
        if 'craft' in self.available_methods:
            result = self.extract_with_craft(preprocessed[2])
            if result['confidence'] > 0:
                all_results.append(result)
        
        if 'keras_ocr' in self.available_methods:
            result = self.extract_with_keras_ocr(preprocessed[3])
            if result['confidence'] > 0:
                all_results.append(result)
        
        if 'doctr' in self.available_methods:
            result = self.extract_with_doctr(preprocessed[4])
            if result['confidence'] > 0:
                all_results.append(result)
        
        if not all_results:
            return {'text': '', 'confidence': 0, 'lines': [], 'method': 'ensemble'}
        
        # Combine results using weighted voting
        combined_text = self._combine_results(all_results)
        combined_confidence = np.mean([r['confidence'] for r in all_results])
        
        return {
            'text': combined_text,
            'confidence': combined_confidence,
            'lines': combined_text.split('\n'),
            'method': 'ensemble',
            'individual_results': all_results
        }
    
    def _combine_results(self, results: List[Dict]) -> str:
        """
        Combine multiple OCR results using fuzzy matching and voting
        """
        if not results:
            return ''
        
        if len(results) == 1:
            return results[0]['text']
        
        # Extract all text lines from all results
        all_texts = [r['text'] for r in results]
        all_confidences = [r['confidence'] for r in results]
        
        # Use the result with highest confidence as base
        best_idx = np.argmax(all_confidences)
        best_text = all_texts[best_idx]
        
        # Try to improve with fuzzy matching from other results
        from fuzzywuzzy import fuzz
        
        for i, text in enumerate(all_texts):
            if i != best_idx:
                similarity = fuzz.ratio(best_text, text)
                # If another result is very similar but has higher confidence
                if similarity > 80 and all_confidences[i] > all_confidences[best_idx]:
                    best_text = text
        
        return best_text
    
    def _group_by_lines(self, texts: List[str], polygons: List) -> List[str]:
        """Group texts by lines based on Y-coordinate"""
        if not texts:
            return []
        
        # Calculate Y coordinates
        y_coords = []
        for poly in polygons:
            y_avg = sum(p[1] for p in poly) / len(poly)
            y_coords.append(y_avg)
        
        # Group by similar Y coordinates
        threshold = 15  # pixels
        lines = []
        current_line = []
        current_y = y_coords[0]
        
        for text, y in zip(texts, y_coords):
            if abs(y - current_y) <= threshold:
                current_line.append(text)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [text]
                current_y = y
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _simple_ocr_on_roi(self, roi: np.ndarray) -> str:
        """Simple OCR fallback for ROI"""
        try:
            import pytesseract
            text = pytesseract.image_to_string(roi, config='--psm 7')
            return text.strip()
        except:
            return ''


def test_advanced_ocr():
    """Test function to verify OCR engines"""
    print("Testing Advanced OCR Engine...")
    engine = AdvancedOCREngine()
    
    # Load test image
    import os
    test_img_path = 'test_images/ADC0831_0-300x300.png'
    
    if os.path.exists(test_img_path):
        image = cv2.imread(test_img_path)
        result = engine.extract_with_ensemble(image)
        
        print("\n" + "="*80)
        print("ADVANCED OCR RESULTS")
        print("="*80)
        print(f"Text: {result['text']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Lines: {result['lines']}")
        print("="*80)
    else:
        print(f"Test image not found: {test_img_path}")


if __name__ == '__main__':
    test_advanced_ocr()
