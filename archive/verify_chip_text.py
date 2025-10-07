"""
VERIFY ACTUAL CHIP TEXT - Extensive Preprocessing & Debug
Goal: Confirm both type1 and type2 have ATMEGA328P with different secondary markings
"""

import cv2
import numpy as np
import easyocr
import os
from pathlib import Path


class ExtensiveChipVerifier:
    """Verify chip text with massive preprocessing variations"""
    
    def __init__(self):
        print("🔬 Initializing Extensive Chip Text Verifier...")
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.debug_dir = "chip_verification_debug"
        os.makedirs(self.debug_dir, exist_ok=True)
        print(f"✅ Debug images will be saved to: {self.debug_dir}/\n")
    
    def generate_extensive_variants(self, image: np.ndarray, image_name: str):
        """Generate 50+ preprocessing variants with focus on text clarity"""
        variants = []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        print(f"📸 Generating extensive preprocessing variants for {image_name}...")
        
        # 1. Original
        variants.append(("01_original", image.copy()))
        
        # 2. Grayscale
        variants.append(("02_grayscale", cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)))
        
        # 3-12. Upscaling variants (crucial for blurry text)
        for scale in [2, 3, 4, 6, 8]:
            scaled = cv2.resize(gray, (w*scale, h*scale), interpolation=cv2.INTER_CUBIC)
            variants.append((f"03_upscale_{scale}x", cv2.cvtColor(scaled, cv2.COLOR_GRAY2BGR)))
            
            # Sharpen after upscaling
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(scaled, -1, kernel)
            variants.append((f"04_upscale_{scale}x_sharp", cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)))
        
        # 13-22. Exposure/Contrast adjustments
        for alpha in [1.0, 1.2, 1.4, 1.6, 1.8]:
            for beta in [0, 20, 40]:
                adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
                variants.append((f"05_exp_a{alpha}_b{beta}", adjusted))
        
        # 23-34. CLAHE variants (crucial for uneven lighting)
        for clip in [1.0, 2.0, 4.0, 8.0]:
            for tile in [4, 8, 16]:
                clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
                if len(image.shape) == 3:
                    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                    lab[:,:,0] = clahe.apply(lab[:,:,0])
                    clahe_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                else:
                    clahe_img = clahe.apply(gray)
                    clahe_img = cv2.cvtColor(clahe_img, cv2.COLOR_GRAY2BGR)
                variants.append((f"06_clahe_c{clip}_t{tile}", clahe_img))
        
        # 35-40. Denoising variants
        for h_param in [3, 7, 10]:
            denoised = cv2.fastNlMeansDenoising(gray, None, h_param, 7, 21)
            variants.append((f"07_denoise_h{h_param}", cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)))
            
            # Sharpen after denoising
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            variants.append((f"08_denoise_h{h_param}_sharp", cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)))
        
        # 41-46. Morphological operations
        for kernel_size in [2, 3, 4]:
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            
            # Erosion (thin text)
            eroded = cv2.erode(gray, kernel, iterations=1)
            variants.append((f"09_erode_k{kernel_size}", cv2.cvtColor(eroded, cv2.COLOR_GRAY2BGR)))
            
            # Dilation (thick text)
            dilated = cv2.dilate(gray, kernel, iterations=1)
            variants.append((f"10_dilate_k{kernel_size}", cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)))
        
        # 47-52. Bilateral filtering (edge-preserving blur)
        for d in [5, 9]:
            for sigma in [50, 75, 100]:
                bilateral = cv2.bilateralFilter(gray, d, sigma, sigma)
                variants.append((f"11_bilateral_d{d}_s{sigma}", cv2.cvtColor(bilateral, cv2.COLOR_GRAY2BGR)))
        
        # 53-58. Adaptive thresholding
        for block in [31, 51, 71]:
            # Mean
            adaptive_mean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                                  cv2.THRESH_BINARY, block, 10)
            variants.append((f"12_adaptive_mean_{block}", cv2.cvtColor(adaptive_mean, cv2.COLOR_GRAY2BGR)))
            
            # Gaussian
            adaptive_gauss = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                   cv2.THRESH_BINARY, block, 10)
            variants.append((f"13_adaptive_gauss_{block}", cv2.cvtColor(adaptive_gauss, cv2.COLOR_GRAY2BGR)))
        
        # 59-62. Otsu thresholding with blur
        for blur_size in [0, 3, 5, 7]:
            if blur_size > 0:
                blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
            else:
                blurred = gray.copy()
            _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append((f"14_otsu_blur{blur_size}", cv2.cvtColor(otsu, cv2.COLOR_GRAY2BGR)))
        
        # 63-68. Unsharp masking (detail enhancement)
        for amount in [0.5, 1.0, 2.0]:
            gaussian = cv2.GaussianBlur(gray, (0, 0), 3.0)
            unsharp = cv2.addWeighted(gray, 1.0 + amount, gaussian, -amount, 0)
            variants.append((f"15_unsharp_{amount}", cv2.cvtColor(unsharp, cv2.COLOR_GRAY2BGR)))
            
            # With CLAHE after unsharp
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            unsharp_clahe = clahe.apply(unsharp)
            variants.append((f"16_unsharp_{amount}_clahe", cv2.cvtColor(unsharp_clahe, cv2.COLOR_GRAY2BGR)))
        
        print(f"✅ Generated {len(variants)} preprocessing variants")
        
        # Save all variants
        for name, img in variants:
            save_path = os.path.join(self.debug_dir, f"{image_name}_{name}.jpg")
            cv2.imwrite(save_path, img)
        
        return variants
    
    def run_ocr_on_all_variants(self, variants, image_name):
        """Run OCR on all variants and return all unique text found"""
        all_results = []
        
        print(f"\n🔍 Running OCR on {len(variants)} variants...")
        
        for i, (variant_name, img) in enumerate(variants):
            try:
                # Convert to grayscale for OCR
                if len(img.shape) == 3:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                else:
                    gray = img
                
                # Run OCR
                result = self.reader.readtext(gray, detail=1)
                
                if result:
                    text = ' '.join([t[1] for t in result])
                    conf = np.mean([t[2] for t in result]) * 100
                    
                    all_results.append({
                        'variant': variant_name,
                        'text': text,
                        'confidence': conf,
                        'raw_result': result
                    })
                    
                    # Print promising results (high confidence or contains ATMEGA)
                    if conf > 40 or 'ATMEGA' in text.upper() or '328' in text:
                        print(f"  [{i+1:3d}] {variant_name[:40]:<40} | {text[:60]:<60} | {conf:.1f}%")
            
            except Exception as e:
                continue
        
        return all_results
    
    def analyze_results(self, results, image_name):
        """Analyze all OCR results to find the true chip text"""
        print(f"\n{'='*120}")
        print(f"📊 ANALYSIS FOR {image_name}")
        print('='*120)
        
        # Find all unique text extractions
        unique_texts = {}
        for r in results:
            text = r['text'].upper().strip()
            if text not in unique_texts:
                unique_texts[text] = []
            unique_texts[text].append(r)
        
        print(f"\n🔍 Found {len(unique_texts)} unique text extractions:")
        print(f"\n{'Text':<80} {'Count':<8} {'Avg Conf':<10} {'Best Variant'}")
        print('-'*120)
        
        # Sort by frequency and confidence
        sorted_texts = sorted(unique_texts.items(), 
                            key=lambda x: (len(x[1]), np.mean([r['confidence'] for r in x[1]])),
                            reverse=True)
        
        for text, occurrences in sorted_texts[:20]:  # Top 20
            count = len(occurrences)
            avg_conf = np.mean([r['confidence'] for r in occurrences])
            best_variant = max(occurrences, key=lambda x: x['confidence'])['variant']
            
            print(f"{text[:80]:<80} {count:<8} {avg_conf:>7.1f}%   {best_variant}")
        
        # Find texts containing ATMEGA328
        print(f"\n{'='*120}")
        print("🎯 TEXTS CONTAINING 'ATMEGA328':")
        print('='*120)
        
        atmega_texts = [(text, occs) for text, occs in sorted_texts if 'ATMEGA328' in text]
        
        if atmega_texts:
            for text, occurrences in atmega_texts:
                count = len(occurrences)
                avg_conf = np.mean([r['confidence'] for r in occurrences])
                best = max(occurrences, key=lambda x: x['confidence'])
                
                print(f"\n✅ '{text}'")
                print(f"   Frequency: {count} times")
                print(f"   Avg Confidence: {avg_conf:.1f}%")
                print(f"   Best Variant: {best['variant']} ({best['confidence']:.1f}%)")
                print(f"   Best OCR: {best['text']}")
        else:
            print("❌ No variants extracted 'ATMEGA328P' correctly")
            print("\n⚠️ Most common extractions:")
            for text, occs in sorted_texts[:5]:
                avg_conf = np.mean([r['confidence'] for r in occs])
                print(f"   - '{text}' ({len(occs)} times, {avg_conf:.1f}% confidence)")
        
        # Find the most reliable result (highest confidence among most frequent)
        if results:
            best_overall = max(results, key=lambda x: x['confidence'])
            print(f"\n{'='*120}")
            print(f"🏆 BEST OVERALL RESULT:")
            print(f"   Variant: {best_overall['variant']}")
            print(f"   Text: {best_overall['text']}")
            print(f"   Confidence: {best_overall['confidence']:.1f}%")
            print('='*120)


def main():
    """Verify both type1 and type2 chips"""
    
    print("="*120)
    print("🔬 EXTENSIVE CHIP TEXT VERIFICATION")
    print("   Goal: Confirm both type1 and type2 have ATMEGA328P (not ATMEGAS2BP)")
    print("   Method: 60+ preprocessing variants with detailed OCR analysis")
    print("="*120)
    
    verifier = ExtensiveChipVerifier()
    
    test_images = [
        "test_images/type1.jpg",
        "test_images/type2.jpg"
    ]
    
    for img_path in test_images:
        if not os.path.exists(img_path):
            print(f"\n❌ Image not found: {img_path}")
            continue
        
        image_name = Path(img_path).stem
        print(f"\n{'='*120}")
        print(f"🔍 PROCESSING: {image_name}")
        print('='*120)
        
        # Load image
        image = cv2.imread(img_path)
        if image is None:
            print(f"❌ Failed to load {img_path}")
            continue
        
        # Generate extensive variants
        variants = verifier.generate_extensive_variants(image, image_name)
        
        # Run OCR on all
        results = verifier.run_ocr_on_all_variants(variants, image_name)
        
        # Analyze
        verifier.analyze_results(results, image_name)
        
        print(f"\n✅ Processing complete for {image_name}")
        print(f"   Debug images saved to: {verifier.debug_dir}/{image_name}_*.jpg")
    
    print(f"\n\n{'='*120}")
    print("✅ VERIFICATION COMPLETE")
    print(f"   All debug images saved to: {verifier.debug_dir}/")
    print("="*120)


if __name__ == "__main__":
    main()
