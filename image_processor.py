"""
Image Processing Module
Handles image preprocessing, enhancement, and IC detection
"""

import cv2
import numpy as np
from skimage import exposure, filters, morphology
from skimage.feature import canny
from scipy import ndimage


class ImageProcessor:
    """Advanced image processing for IC component analysis"""
    
    def __init__(self):
        self.debug_images = {}
        
    def process_image(self, image):
        """
        Process and enhance input image
        Returns dictionary of processed images at various stages
        """
        self.debug_images = {}
        
        # Store original
        self.debug_images['original'] = image.copy()
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        self.debug_images['grayscale'] = gray
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        self.debug_images['denoised'] = denoised
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        self.debug_images['enhanced'] = enhanced
        
        # Additional enhancement using histogram equalization
        equalized = cv2.equalizeHist(enhanced)
        self.debug_images['equalized'] = equalized
        
        # Edge detection
        edges = cv2.Canny(enhanced, 50, 150)
        self.debug_images['edges'] = edges
        
        # Morphological operations
        kernel = np.ones((3, 3), np.uint8)
        morph = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        self.debug_images['morphological'] = morph
        
        return self.debug_images
    
    def detect_ic_regions(self, image):
        """
        Detect IC component regions in the image
        Uses contour detection and geometric analysis
        """
        # Apply binary threshold
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up
        kernel_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_rect)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel_rect)
        
        # Find contours
        contours, _ = cv2.findContours(
            cleaned,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours to find IC-like regions
        ic_regions = []
        debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area (IC should be significant size)
            if area < 1000 or area > image.shape[0] * image.shape[1] * 0.8:
                continue
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            
            # ICs typically have aspect ratios between 0.5 and 2.0
            if 0.3 < aspect_ratio < 3.0:
                ic_regions.append({
                    'x': x, 'y': y, 'w': w, 'h': h,
                    'contour': contour,
                    'area': area,
                    'aspect_ratio': aspect_ratio
                })
                
                # Draw on debug image
                cv2.rectangle(debug_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    debug_image,
                    f"IC",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )
        
        self.debug_images['ic_detected'] = debug_image
        
        return ic_regions
    
    def extract_marking_regions(self, ic_regions):
        """
        Extract marking regions from detected IC areas
        Focuses on text areas
        """
        if not ic_regions:
            # If no IC detected, use full image
            return [self.debug_images.get('enhanced')]
        
        marking_images = []
        debug_image = self.debug_images['original'].copy()
        
        for region in ic_regions:
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            
            # Extract ROI
            roi = self.debug_images['enhanced'][y:y+h, x:x+w]
            
            # Further enhance for text detection
            # Apply bilateral filter to preserve edges
            filtered = cv2.bilateralFilter(roi, 9, 75, 75)
            
            # Adaptive thresholding for text
            adaptive_thresh = cv2.adaptiveThreshold(
                filtered,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Detect text regions using morphological operations
            kernel_text = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 3))
            text_regions = cv2.morphologyEx(
                adaptive_thresh,
                cv2.MORPH_CLOSE,
                kernel_text
            )
            
            marking_images.append({
                'original_roi': roi,
                'enhanced_roi': filtered,
                'text_mask': text_regions,
                'adaptive_thresh': adaptive_thresh,
                'bbox': (x, y, w, h)
            })
            
            # Draw text regions on debug image
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        self.debug_images['roi'] = debug_image
        
        return marking_images
    
    def segment_text_lines(self, image):
        """
        Segment individual text lines from marking region
        """
        # Apply morphological operations to connect text in lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 2))
        connected = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        
        # Find contours of text lines
        contours, _ = cv2.findContours(
            connected,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        text_lines = []
        debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter small regions
            if w < 20 or h < 5:
                continue
            
            text_lines.append({
                'bbox': (x, y, w, h),
                'image': image[y:y+h, x:x+w]
            })
            
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 1)
        
        self.debug_images['text_regions'] = debug_image
        
        # Sort text lines top to bottom
        text_lines.sort(key=lambda x: x['bbox'][1])
        
        return text_lines
    
    def analyze_print_quality(self, image):
        """
        Analyze print quality characteristics
        Helps identify potential counterfeits based on printing defects
        """
        # Calculate sharpness (variance of Laplacian)
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        sharpness = laplacian.var()
        
        # Calculate contrast
        contrast = image.std()
        
        # Detect blur using frequency domain analysis
        f_transform = np.fft.fft2(image)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = 20 * np.log(np.abs(f_shift) + 1)
        
        # High frequency content indicates sharp edges
        rows, cols = image.shape
        crow, ccol = rows // 2, cols // 2
        high_freq_region = magnitude_spectrum[
            crow-30:crow+30,
            ccol-30:ccol+30
        ]
        blur_score = high_freq_region.mean()
        
        # Edge density
        edges = cv2.Canny(image, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        
        # Noise analysis
        noise_estimate = self.estimate_noise(image)
        
        quality_metrics = {
            'sharpness': float(sharpness),
            'contrast': float(contrast),
            'blur_score': float(blur_score),
            'edge_density': float(edge_density),
            'noise_level': float(noise_estimate),
            'overall_quality': self.compute_quality_score(
                sharpness, contrast, edge_density, noise_estimate
            )
        }
        
        return quality_metrics
    
    def estimate_noise(self, image):
        """
        Estimate noise level in image
        """
        # Use median absolute deviation method
        h, w = image.shape
        img_float = image.astype(float)
        
        # Apply median filter
        median_filtered = ndimage.median_filter(img_float, size=3)
        
        # Calculate difference
        diff = np.abs(img_float - median_filtered)
        
        # Estimate noise using MAD
        noise_estimate = np.median(diff) / 0.6745
        
        return noise_estimate
    
    def compute_quality_score(self, sharpness, contrast, edge_density, noise):
        """
        Compute overall quality score (0-100)
        """
        # Normalize metrics
        sharpness_norm = min(sharpness / 1000, 1.0)
        contrast_norm = min(contrast / 100, 1.0)
        edge_norm = min(edge_density * 10, 1.0)
        noise_norm = max(0, 1.0 - noise / 50)
        
        # Weighted combination
        score = (
            sharpness_norm * 0.3 +
            contrast_norm * 0.25 +
            edge_norm * 0.25 +
            noise_norm * 0.2
        ) * 100
        
        return score
    
    def detect_laser_marking(self, image):
        """
        Detect if text is laser-etched vs printed
        Laser marking has specific characteristics
        """
        # Analyze texture patterns
        # Laser marking typically shows:
        # 1. High contrast edges
        # 2. Uniform depth
        # 3. Specific texture patterns
        
        # Edge analysis
        edges = cv2.Canny(image, 50, 150)
        edge_strength = edges.mean()
        
        # Texture analysis using Local Binary Patterns
        from skimage.feature import local_binary_pattern
        
        radius = 3
        n_points = 8 * radius
        lbp = local_binary_pattern(image, n_points, radius, method='uniform')
        
        # Calculate histogram
        hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3))
        hist = hist.astype(float)
        hist /= (hist.sum() + 1e-6)
        
        # Laser etching typically shows higher uniformity in texture
        texture_uniformity = 1.0 - np.std(hist)
        
        # Analyze surface characteristics
        sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        marking_features = {
            'edge_strength': float(edge_strength),
            'texture_uniformity': float(texture_uniformity),
            'gradient_variance': float(gradient_magnitude.var()),
            'is_laser_marked': texture_uniformity > 0.6 and edge_strength > 30
        }
        
        return marking_features
    
    def get_debug_images(self):
        """Return all debug images"""
        return self.debug_images
