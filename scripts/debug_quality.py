"""
Debug quality scoring to understand why TrOCR is being selected over EasyOCR
"""
import cv2
from ocr_engine import OCREngine

def test_quality_scoring():
    print("=" * 80)
    print("DEBUGGING QUALITY SCORE CALCULATION")
    print("=" * 80)
    print()
    
    # Load image
    image = cv2.imread("test_images/type2.jpg")
    ocr = OCREngine()
    
    # Test texts we know were extracted
    test_texts = [
        ("EasyOCR variant 2", "4il143 AImEl ATMEGAS28P 20AU 0723", 0.4307),
        ("EasyOCR variant 3", "244434 Gi 'AtMee3328P ZOAU 0723 0 0", 0.5994),
        ("TrOCR", "CASHIER", 0.92),
        ("docTR", "((rce\nu\nf\n-\n- -\n- - I S\n-\n-\nI\n- iddidl", 0.88),
    ]
    
    print("Quality Assessment:")
    print("-" * 80)
    
    for name, text, ocr_conf in test_texts:
        quality = ocr._assess_result_quality(text)
        combined = (quality * 0.7) + (ocr_conf * 0.3)
        
        print(f"\n{name}:")
        print(f"  Text: {repr(text[:60])}")
        print(f"  OCR Confidence: {ocr_conf:.2%}")
        print(f"  Quality Score: {quality:.3f}")
        print(f"  Combined Score: {combined:.3f} (70% quality + 30% confidence)")
    
    print("\n" + "=" * 80)
    print("EXPECTED: EasyOCR variants should score highest due to IC-like content")
    print("=" * 80)

if __name__ == "__main__":
    test_quality_scoring()
