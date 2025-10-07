"""Visual inspection of type2.jpg to understand OCR challenge"""

import cv2
import numpy as np

# Load the image
img = cv2.imread("test_images/type2.jpg")
print("Image loaded successfully")
print(f"Image shape: {img.shape}")
print(f"Image size: {img.shape[1]}x{img.shape[0]} pixels")

# Let's check the actual pixel intensity of the problematic area
# The text should say "ATMEGA328P" but OCR reads "ATMEGA3282"
# This means the "P" at the end is being read as "2"

# Convert to grayscale for analysis
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

print(f"\nImage statistics:")
print(f"  Mean brightness: {np.mean(gray):.1f}")
print(f"  Min brightness: {np.min(gray)}")
print(f"  Max brightness: {np.max(gray)}")
print(f"  Std dev: {np.std(gray):.1f}")

# Check if image is low contrast
if np.std(gray) < 30:
    print("\n⚠️ WARNING: Low contrast image - text may be faded")
    
if np.mean(gray) < 100:
    print("⚠️ WARNING: Dark image - characters may blend with background")
    
if np.mean(gray) > 200:
    print("⚠️ WARNING: Bright image - characters may be washed out")

# Let's try extreme preprocessing to see if P is even readable
print("\n" + "=" * 60)
print("TESTING EXTREME PREPROCESSING")
print("=" * 60)

# Test 1: Maximum upscaling + maximum sharpening
print("\nTest 1: Extreme upscale (10x) + double sharpening")
huge = cv2.resize(gray, None, fx=10, fy=10, interpolation=cv2.INTER_CUBIC)
kernel_sharpen = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
sharp1 = cv2.filter2D(huge, -1, kernel_sharpen)
sharp2 = cv2.filter2D(sharp1, -1, kernel_sharpen)
cv2.imwrite("debug_extreme_upscale_sharp.png", sharp2)
print("  Saved to: debug_extreme_upscale_sharp.png")
print(f"  Output size: {sharp2.shape[1]}x{sharp2.shape[0]} pixels")

# Test 2: Adaptive thresholding to isolate text
print("\nTest 2: Adaptive thresholding")
adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 11, 2)
cv2.imwrite("debug_adaptive_thresh.png", adaptive)
print("  Saved to: debug_adaptive_thresh.png")

# Test 3: CLAHE extreme
print("\nTest 3: Extreme CLAHE")
clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(2, 2))
extreme = clahe.apply(gray)
cv2.imwrite("debug_extreme_clahe.png", extreme)
print("  Saved to: debug_extreme_clahe.png")

# Test 4: Morphological operations to enhance edges
print("\nTest 4: Morphological gradient (edge emphasis)")
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
cv2.imwrite("debug_morph_gradient.png", gradient)
print("  Saved to: debug_morph_gradient.png")

# Test 5: Combination approach
print("\nTest 5: Combined approach (upscale + CLAHE + sharpen + bilateral)")
step1 = cv2.resize(gray, None, fx=8, fy=8, interpolation=cv2.INTER_CUBIC)
step2 = cv2.bilateralFilter(step1, 9, 75, 75)
step3 = clahe.apply(step2)
step4 = cv2.filter2D(step3, -1, kernel_sharpen)
cv2.imwrite("debug_combined.png", step4)
print("  Saved to: debug_combined.png")

print("\n" + "=" * 60)
print("✅ Generated 5 debug images for manual inspection")
print("   Check if '328P' is clearly visible in any of them")
print("=" * 60)
