"""
Advanced Preprocessing Pipeline for IC Text Detection
Based on research papers: pixel voting, adaptive binarization, CLAHE optimization
Implements the workflow from Figure 3 in the research paper
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict
import os
from pathlib import Path


class AdvancedICPreprocessor:
    """
    Advanced preprocessing with exposure/contrast adjustment, 
    multiple binarization methods, and pixel voting
    """
    
    def __init__(self):
        self.debug_mode = True
        self.debug_dir = "debug_preprocessing"
        if self.debug_mode:
            os.makedirs(self.debug_dir, exist_ok=True)
    
    def save_debug_image(self, image, name, subfolder=""):
        """Save debug images for analysis"""
        if not self.debug_mode:
            return
        folder = os.path.join(self.debug_dir, subfolder) if subfolder else self.debug_dir
        os.makedirs(folder, exist_ok=True)
        cv2.imwrite(os.path.join(folder, name), image)
    
    def straighten_image(self, image: np.ndarray) -> np.ndarray:
        """Step 1: Straighten the image using Hough transform"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
        
        if lines is not None and len(lines) > 0:
            angles = []
            for rho, theta in lines[:, 0]:
                angle = np.degrees(theta) - 90
                if -45 < angle < 45:
                    angles.append(angle)
            
            if angles:
                median_angle = np.median(angles)
                if abs(median_angle) > 0.5:  # Only rotate if significantly skewed
                    h, w = gray.shape
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    image = cv2.warpAffine(image, M, (w, h), 
                                          flags=cv2.INTER_CUBIC,
                                          borderMode=cv2.BORDER_REPLICATE)
        
        return image
    
    def scale_image(self, image: np.ndarray, target_size: int = 2000) -> np.ndarray:
        """Step 2: Scale the image to optimal size"""
        h, w = image.shape[:2]
        max_dim = max(h, w)
        
        if max_dim < target_size:
            # Upscale
            scale = target_size / max_dim
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        elif max_dim > target_size * 2:
            # Downscale if too large
            scale = target_size / max_dim
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        return image
    
    def adjust_exposure_contrast(self, image: np.ndarray, 
                                 alpha: float = 1.3, beta: int = 20) -> np.ndarray:
        """
        Adjust image exposure and contrast
        alpha: contrast control (1.0-3.0)
        beta: brightness control (0-100)
        """
        adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return adjusted
    
    def apply_clahe_variants(self, gray: np.ndarray) -> List[Tuple[str, np.ndarray]]:
        """Apply CLAHE with different tile sizes and clip limits (from paper)"""
        variants = []
        
        # From paper: test 4, 8, 16, 32 tiles with different clip limits
        configs = [
            (4, 0.0020, "clahe_4_0.0020"),
            (8, 0.0025, "clahe_8_0.0025"),
            (16, 0.0040, "clahe_16_0.0040"),
            (32, 0.0060, "clahe_32_0.0060"),
        ]
        
        for tiles, clip_limit, name in configs:
            clahe = cv2.createCLAHE(clipLimit=clip_limit * 10000, 
                                   tileGridSize=(tiles, tiles))
            enhanced = clahe.apply(gray)
            variants.append((name, enhanced))
        
        return variants
    
    def apply_binarization_methods(self, gray: np.ndarray, 
                                   neighborhood_sizes: List[int] = [11, 21, 51, 71, 81]) -> Dict[str, List[np.ndarray]]:
        """
        Apply all binarization methods from the paper
        Returns dict with method name and list of variants for different neighborhood sizes
        """
        results = {}
        
        for size in neighborhood_sizes:
            if size % 2 == 0:  # Ensure odd
                size += 1
            
            # Otsu (global threshold)
            _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if 'Otsu' not in results:
                results['Otsu'] = []
            results['Otsu'].append(otsu)
            
            # Bernsen
            bernsen = self._bernsen_threshold(gray, size)
            if 'Bernsen' not in results:
                results['Bernsen'] = []
            results['Bernsen'].append(bernsen)
            
            # Bradley
            bradley = self._bradley_threshold(gray, size)
            if 'Bradley' not in results:
                results['Bradley'] = []
            results['Bradley'].append(bradley)
            
            # Feng
            feng = self._feng_threshold(gray, size)
            if 'Feng' not in results:
                results['Feng'] = []
            results['Feng'].append(feng)
            
            # Niblack
            niblack = self._niblack_threshold(gray, size, k=-0.2)
            if 'Niblack' not in results:
                results['Niblack'] = []
            results['Niblack'].append(niblack)
            
            # NICK
            nick = self._nick_threshold(gray, size)
            if 'NICK' not in results:
                results['NICK'] = []
            results['NICK'].append(nick)
            
            # Sauvola
            sauvola = self._sauvola_threshold(gray, size, k=0.5)
            if 'Sauvola' not in results:
                results['Sauvola'] = []
            results['Sauvola'].append(sauvola)
            
            # Wolf
            wolf = self._wolf_threshold(gray, size)
            if 'Wolf' not in results:
                results['Wolf'] = []
            results['Wolf'].append(wolf)
            
            # Van Herk (using morphological operations)
            van_herk = self._van_herk_threshold(gray, size)
            if 'VanHerk' not in results:
                results['VanHerk'] = []
            results['VanHerk'].append(van_herk)
        
        return results
    
    def _bernsen_threshold(self, gray: np.ndarray, window_size: int) -> np.ndarray:
        """Bernsen local thresholding"""
        pad = window_size // 2
        padded = cv2.copyMakeBorder(gray, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
        binary = np.zeros_like(gray)
        
        for i in range(gray.shape[0]):
            for j in range(gray.shape[1]):
                window = padded[i:i+window_size, j:j+window_size]
                local_max = np.max(window)
                local_min = np.min(window)
                mid_gray = (local_max + local_min) / 2
                
                if (local_max - local_min) < 15:  # Low contrast
                    binary[i, j] = 255 if mid_gray >= 128 else 0
                else:
                    binary[i, j] = 255 if gray[i, j] >= mid_gray else 0
        
        return binary
    
    def _bradley_threshold(self, gray: np.ndarray, window_size: int, t: float = 0.15) -> np.ndarray:
        """Bradley adaptive thresholding"""
        integral = cv2.integral(gray)
        binary = np.zeros_like(gray)
        
        h, w = gray.shape
        s = window_size // 2
        
        for i in range(h):
            for j in range(w):
                x1 = max(0, j - s)
                x2 = min(w - 1, j + s)
                y1 = max(0, i - s)
                y2 = min(h - 1, i + s)
                
                count = (x2 - x1) * (y2 - y1)
                sum_val = integral[y2+1, x2+1] - integral[y1, x2+1] - integral[y2+1, x1] + integral[y1, x1]
                
                # Convert to float to avoid overflow
                if int(gray[i, j]) * count < sum_val * (1.0 - t):
                    binary[i, j] = 0
                else:
                    binary[i, j] = 255
        
        return binary
    
    def _feng_threshold(self, gray: np.ndarray, window_size: int) -> np.ndarray:
        """Feng adaptive thresholding"""
        mean = cv2.blur(gray.astype(np.float32), (window_size, window_size))
        mean_sq = cv2.blur((gray.astype(np.float32) ** 2), (window_size, window_size))
        std = np.sqrt(mean_sq - mean ** 2)
        
        alpha1 = 0.1
        alpha2 = 0.2
        alpha3 = 2.0
        
        threshold = mean * (1 + alpha1 * ((std / 128) - 1)) * (1 + alpha2 * ((mean / 128) - 1)) * alpha3
        binary = (gray > threshold).astype(np.uint8) * 255
        
        return binary
    
    def _niblack_threshold(self, gray: np.ndarray, window_size: int, k: float = -0.2) -> np.ndarray:
        """Niblack adaptive thresholding"""
        mean = cv2.blur(gray.astype(np.float32), (window_size, window_size))
        mean_sq = cv2.blur((gray.astype(np.float32) ** 2), (window_size, window_size))
        std = np.sqrt(mean_sq - mean ** 2)
        
        threshold = mean + k * std
        binary = (gray > threshold).astype(np.uint8) * 255
        
        return binary
    
    def _nick_threshold(self, gray: np.ndarray, window_size: int, k: float = -0.1) -> np.ndarray:
        """NICK adaptive thresholding"""
        mean = cv2.blur(gray.astype(np.float32), (window_size, window_size))
        mean_sq = cv2.blur((gray.astype(np.float32) ** 2), (window_size, window_size))
        variance = mean_sq - mean ** 2
        
        threshold = mean + k * np.sqrt(variance + mean ** 2)
        binary = (gray > threshold).astype(np.uint8) * 255
        
        return binary
    
    def _sauvola_threshold(self, gray: np.ndarray, window_size: int, k: float = 0.5, R: float = 128) -> np.ndarray:
        """Sauvola adaptive thresholding"""
        mean = cv2.blur(gray.astype(np.float32), (window_size, window_size))
        mean_sq = cv2.blur((gray.astype(np.float32) ** 2), (window_size, window_size))
        std = np.sqrt(mean_sq - mean ** 2)
        
        threshold = mean * (1 + k * ((std / R) - 1))
        binary = (gray > threshold).astype(np.uint8) * 255
        
        return binary
    
    def _wolf_threshold(self, gray: np.ndarray, window_size: int, k: float = 0.5) -> np.ndarray:
        """Wolf adaptive thresholding"""
        mean = cv2.blur(gray.astype(np.float32), (window_size, window_size))
        mean_sq = cv2.blur((gray.astype(np.float32) ** 2), (window_size, window_size))
        std = np.sqrt(mean_sq - mean ** 2)
        
        min_gray = np.min(gray)
        max_std = np.max(std)
        
        threshold = (1 - k) * mean + k * min_gray + k * (std / max_std) * (mean - min_gray)
        binary = (gray > threshold).astype(np.uint8) * 255
        
        return binary
    
    def _van_herk_threshold(self, gray: np.ndarray, window_size: int) -> np.ndarray:
        """Van Herk morphological thresholding"""
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (window_size, window_size))
        tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
        
        enhanced = cv2.add(gray, tophat)
        enhanced = cv2.subtract(enhanced, blackhat)
        
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    
    def pixel_voting(self, binary_images: List[np.ndarray]) -> np.ndarray:
        """
        Pixel voting from paper: combine multiple binarization results
        Takes median vote across all methods
        """
        if len(binary_images) == 0:
            raise ValueError("No binary images provided for voting")
        
        # Stack all binary images
        stack = np.stack(binary_images, axis=0)
        
        # Vote: pixel is white if majority of methods say white
        voted = np.median(stack, axis=0).astype(np.uint8)
        
        return voted
    
    def clean_border(self, binary: np.ndarray, border_size: int = 5) -> np.ndarray:
        """Clean the border artifacts"""
        cleaned = binary.copy()
        cleaned[:border_size, :] = 0
        cleaned[-border_size:, :] = 0
        cleaned[:, :border_size] = 0
        cleaned[:, -border_size:] = 0
        return cleaned
    
    def remove_noise(self, binary: np.ndarray) -> np.ndarray:
        """Remove noise using morphological operations"""
        # Remove small noise
        kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small)
        
        # Remove small holes
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_close)
        
        return cleaned
    
    def process_image_complete_pipeline(self, image: np.ndarray, image_name: str = "image") -> List[Tuple[str, np.ndarray]]:
        """
        Complete preprocessing pipeline from research paper
        Returns list of (method_name, processed_image) tuples
        """
        print(f"\n🔬 Processing {image_name} through complete pipeline...")
        
        # Step 1: Straighten
        print("  [1/7] Straightening image...")
        straightened = self.straighten_image(image)
        self.save_debug_image(straightened, f"{image_name}_01_straightened.jpg")
        
        # Step 2: Scale
        print("  [2/7] Scaling image...")
        scaled = self.scale_image(straightened, target_size=2000)
        self.save_debug_image(scaled, f"{image_name}_02_scaled.jpg")
        
        # Convert to grayscale
        if len(scaled.shape) == 3:
            gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)
        else:
            gray = scaled.copy()
        
        # Step 3: Exposure/Contrast adjustment
        print("  [3/7] Adjusting exposure/contrast...")
        exposure_variants = []
        for alpha in [1.0, 1.3, 1.5]:  # Test different contrast levels
            for beta in [0, 20, 40]:  # Test different brightness levels
                adjusted = self.adjust_exposure_contrast(gray, alpha=alpha, beta=beta)
                name = f"exp_a{alpha:.1f}_b{beta}"
                exposure_variants.append((name, adjusted))
                self.save_debug_image(adjusted, f"{image_name}_03_{name}.jpg")
        
        # Step 4: CLAHE (optional - test both with and without)
        print("  [4/7] Applying CLAHE variants...")
        clahe_variants = []
        for name, exp_img in exposure_variants[:3]:  # Test CLAHE on top 3 exposure settings
            variants = self.apply_clahe_variants(exp_img)
            clahe_variants.extend([(f"{name}_{v_name}", v_img) for v_name, v_img in variants])
        
        # Save sample CLAHE results
        for i, (name, img) in enumerate(clahe_variants[:5]):
            self.save_debug_image(img, f"{image_name}_04_{name}.jpg")
        
        # Step 5: Binarization with multiple methods
        print("  [5/7] Applying binarization methods...")
        
        # Test binarization on best exposure and CLAHE variants
        test_images = [
            ("original", gray),
            ("exp_best", exposure_variants[4][1]),  # a1.3_b20
        ]
        if clahe_variants:
            test_images.append(("clahe_best", clahe_variants[1][1]))
        
        all_binary_results = []
        
        for base_name, base_img in test_images:
            binary_methods = self.apply_binarization_methods(base_img, neighborhood_sizes=[61])
            
            for method_name, method_variants in binary_methods.items():
                for idx, binary_img in enumerate(method_variants):
                    result_name = f"{base_name}_{method_name}_61px"
                    all_binary_results.append((result_name, binary_img))
                    self.save_debug_image(binary_img, f"{image_name}_05_{result_name}.jpg")
        
        # Step 6: Pixel voting
        print("  [6/7] Applying pixel voting...")
        if len(all_binary_results) >= 5:
            # Select top performing methods for voting
            voting_images = [img for _, img in all_binary_results[:11]]  # Top 11 methods
            voted = self.pixel_voting(voting_images)
            self.save_debug_image(voted, f"{image_name}_06_pixel_voted.jpg")
            all_binary_results.append(("pixel_voted_11methods", voted))
            
            # Also try voting with 5 methods
            voting_images_5 = [img for _, img in all_binary_results[:5]]
            voted_5 = self.pixel_voting(voting_images_5)
            self.save_debug_image(voted_5, f"{image_name}_06_pixel_voted_5methods.jpg")
            all_binary_results.append(("pixel_voted_5methods", voted_5))
        
        # Step 7: Post-processing (clean border + remove noise)
        print("  [7/7] Post-processing (border cleaning + noise removal)...")
        final_results = []
        
        for name, binary_img in all_binary_results:
            # Clean border
            cleaned = self.clean_border(binary_img)
            
            # Remove noise
            final = self.remove_noise(cleaned)
            
            final_name = f"final_{name}"
            final_results.append((final_name, final))
            self.save_debug_image(final, f"{image_name}_07_{final_name}.jpg")
        
        print(f"✅ Generated {len(final_results)} preprocessed variants for {image_name}")
        
        return final_results


def test_advanced_preprocessing():
    """Test the advanced preprocessing on all test images"""
    test_images = [
        "test_images/ADC0831_0-300x300.png",
        "test_images/Screenshot 2025-10-06 222749.png",
        "test_images/Screenshot 2025-10-06 222803.png",
        "test_images/sn74hc595n-shift-register-cmos-logic-ic-integrated-circuit-3.jpg",
        "test_images/type1.jpg",
        "test_images/type2.jpg"
    ]
    
    preprocessor = AdvancedICPreprocessor()
    
    for img_path in test_images:
        if not os.path.exists(img_path):
            print(f"⚠️ Skipping {img_path} - not found")
            continue
        
        image = cv2.imread(img_path)
        image_name = Path(img_path).stem
        
        results = preprocessor.process_image_complete_pipeline(image, image_name)
        
        print(f"\n📊 Results for {image_name}: {len(results)} variants generated")
        print(f"   Debug images saved to: {preprocessor.debug_dir}/{image_name}_*.jpg")


if __name__ == "__main__":
    print("="*100)
    print("ADVANCED IC PREPROCESSING SYSTEM")
    print("Based on research paper methods: pixel voting + adaptive binarization")
    print("="*100)
    test_advanced_preprocessing()
