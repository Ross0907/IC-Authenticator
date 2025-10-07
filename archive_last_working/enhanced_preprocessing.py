"""
Enhanced preprocessing module for low-contrast IC markings
Specifically designed for engraved text on dark surfaces
"""
import cv2
import numpy as np


def preprocess_engraved_text(image, debug=False):
    """
    Advanced preprocessing for engraved IC text on dark surfaces
    Handles low contrast and variable lighting
    
    Args:
        image: Input image (BGR or grayscale)
        debug: If True, returns intermediate steps for visualization
        
    Returns:
        Enhanced image optimized for OCR
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    steps = {'original': gray.copy()} if debug else {}
    
    # Step 1: Increase contrast dramatically
    # Normalize to full range
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    if debug: steps['normalized'] = gray.copy()
    
    # Step 2: Apply aggressive CLAHE for local contrast
    clahe = cv2.createCLAHE(clipLimit=8.0, tileGridSize=(4, 4))
    clahe_enhanced = clahe.apply(gray)
    if debug: steps['clahe'] = clahe_enhanced.copy()
    
    # Step 3: Bilateral filter to reduce noise while keeping edges
    bilateral = cv2.bilateralFilter(clahe_enhanced, 11, 100, 100)
    if debug: steps['bilateral'] = bilateral.copy()
    
    # Step 4: Adaptive thresholding with larger block size
    adaptive = cv2.adaptiveThreshold(
        bilateral, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY,
        blockSize=31,  # Larger block for engraved text
        C=5
    )
    if debug: steps['adaptive'] = adaptive.copy()
    
    # Step 5: Morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel, iterations=1)
    if debug: steps['morphological'] = morph.copy()
    
    # Step 6: Sharpen the result
    kernel_sharpen = np.array([[-1,-1,-1],
                               [-1, 9,-1],
                               [-1,-1,-1]])
    sharpened = cv2.filter2D(morph, -1, kernel_sharpen)
    if debug: steps['sharpened'] = sharpened.copy()
    
    if debug:
        return sharpened, steps
    return sharpened


def preprocess_for_trocr(image):
    """
    Preprocessing optimized for TrOCR transformer model
    Enhances engraved text while maintaining natural appearance
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Normalize
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    
    # Strong CLAHE
    clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(4, 4))
    enhanced = clahe.apply(gray)
    
    # Denoise while preserving text
    denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # Unsharp masking for crisp edges
    gaussian = cv2.GaussianBlur(denoised, (0, 0), 3.0)
    unsharp = cv2.addWeighted(denoised, 2.5, gaussian, -1.5, 0)
    
    # Ensure in valid range
    unsharp = np.clip(unsharp, 0, 255).astype(np.uint8)
    
    return unsharp


def preprocess_for_easyocr(image):
    """
    Preprocessing optimized for EasyOCR
    Creates high-contrast binary image
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Normalize
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    
    # CLAHE
    clahe = cv2.createCLAHE(clipLimit=6.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Bilateral filter
    bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Adaptive threshold
    binary = cv2.adaptiveThreshold(
        bilateral, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=25,
        C=3
    )
    
    # Invert if text is lighter than background
    mean_val = np.mean(gray)
    if mean_val < 127:
        binary = cv2.bitwise_not(binary)
    
    return binary


def preprocess_for_doctr(image):
    """
    Preprocessing optimized for docTR
    Balances contrast and clarity
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Normalize
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    
    # Strong CLAHE
    clahe = cv2.createCLAHE(clipLimit=8.0, tileGridSize=(6, 6))
    enhanced = clahe.apply(gray)
    
    # Gaussian blur then sharpen
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    sharpened = cv2.addWeighted(enhanced, 1.8, blurred, -0.8, 0)
    
    # Ensure valid range
    sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    
    return sharpened


def create_multiple_variants(image):
    """
    Create multiple preprocessing variants for ensemble OCR
    Returns a list of preprocessed images
    """
    variants = []
    
    # Variant 1: TrOCR optimized
    variants.append(('trocr', preprocess_for_trocr(image)))
    
    # Variant 2: EasyOCR optimized
    variants.append(('easyocr', preprocess_for_easyocr(image)))
    
    # Variant 3: docTR optimized
    variants.append(('doctr', preprocess_for_doctr(image)))
    
    # Variant 4: Original with mild enhancement
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    mild = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    mild = clahe.apply(mild)
    variants.append(('mild', mild))
    
    return variants


def enhance_for_specific_ic(image, ic_type='cypress'):
    """
    Apply preprocessing based on known IC manufacturer characteristics
    
    Args:
        image: Input image
        ic_type: 'cypress', 'ti', 'st', 'nxp', etc.
    """
    # Cypress chips often have laser-engraved markings on dark green/black
    if ic_type.lower() in ['cypress', 'infineon']:
        return preprocess_engraved_text(image)
    
    # Texas Instruments often uses white print on black
    elif ic_type.lower() in ['ti', 'texas_instruments']:
        return preprocess_for_easyocr(image)
    
    # Default: use engraved text preprocessing
    else:
        return preprocess_engraved_text(image)


def visualize_preprocessing_steps(image, save_path=None):
    """
    Generate visualization of all preprocessing steps
    Useful for debugging and parameter tuning
    """
    import matplotlib.pyplot as plt
    
    _, steps = preprocess_engraved_text(image, debug=True)
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle('Preprocessing Steps for Engraved IC Text', fontsize=16)
    
    step_names = ['original', 'normalized', 'clahe', 'bilateral', 
                  'adaptive', 'morphological', 'sharpened']
    
    for idx, (name, img) in enumerate([(k, steps[k]) for k in step_names if k in steps]):
        ax = axes[idx // 4, idx % 4]
        ax.imshow(img, cmap='gray')
        ax.set_title(name.title())
        ax.axis('off')
    
    # Hide unused subplot
    if len(step_names) < 8:
        axes[1, 3].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved preprocessing visualization to {save_path}")
    else:
        plt.show()
    
    return fig


if __name__ == "__main__":
    # Test preprocessing on sample image
    import sys
    
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"Error: Could not load image {img_path}")
            sys.exit(1)
        
        print(f"Processing: {img_path}")
        print(f"Image size: {img.shape[1]}x{img.shape[0]}")
        
        # Create visualization
        visualize_preprocessing_steps(img, save_path='preprocessing_steps.png')
        
        # Save all variants
        variants = create_multiple_variants(img)
        for name, variant in variants:
            output_path = f'variant_{name}.png'
            cv2.imwrite(output_path, variant)
            print(f"Saved: {output_path}")
        
        print("\n✓ Preprocessing complete!")
    else:
        print("Usage: python enhanced_preprocessing.py <image_path>")
