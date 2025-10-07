"""Test GUI extraction path"""
import cv2
from dynamic_yolo_ocr import DynamicYOLOOCR
from ic_marking_extractor import ICMarkingExtractor

# Load test image
img = cv2.imread('test_images/type2.jpg')

# Step 1: Extract text using YOLO-OCR
print("Step 1: YOLO-OCR extraction")
yolo_ocr = DynamicYOLOOCR()
yolo_results = yolo_ocr.extract_text_from_ic(img)

print(f"  Extracted: {yolo_results['final_text']}")
print(f"  Confidence: {yolo_results['confidence']:.3f}")

# Step 2: Parse patterns
print("\nStep 2: Parse patterns")
extractor = ICMarkingExtractor()
pattern_results = extractor.parse_ic_marking(yolo_results['final_text'])

print(f"  Part number: {pattern_results.get('part_number')}")
print(f"  Manufacturer: {pattern_results.get('manufacturer')}")
print(f"  Date code: {pattern_results.get('date_code')}")

# Step 3: Create extracted_result (GUI format)
print("\nStep 3: GUI format conversion")
extracted_result = {
    'raw_text': yolo_results['final_text'],
    'confidence': yolo_results['confidence'],
    'manufacturer': pattern_results.get('manufacturer', 'Unknown'),
    'part_number': pattern_results.get('part_number', 'Unknown'),
    'date_code': pattern_results.get('date_code', 'Unknown'),
    'method': 'enhanced_yolo',
    'regions_detected': yolo_results['metadata']['num_regions']
}

# Step 4: Extract text (GUI path)
print("\nStep 4: GUI text extraction")
if 'raw_text' in extracted_result:
    extracted_text = extracted_result.get('raw_text', '')
else:
    extracted_text = extracted_result.get('text', '')

print(f"  Extracted text: '{extracted_text}'")

# Step 5: Parse for verification
print("\nStep 5: Parse for verification")
from ocr_engine import OCREngine
ocr = OCREngine()
parsed_data = ocr.parse_marking_structure(extracted_text)

print(f"  Part number: {parsed_data.get('part_number')}")
print(f"  Manufacturer: {parsed_data.get('manufacturer')}")
print(f"  Date code: {parsed_data.get('date_code')}")
print(f"  Raw text: {parsed_data.get('raw_text')}")

# Step 6: Verify multi-part search
print("\nStep 6: Multi-part number search")
all_parts = extractor.extract_all_part_numbers(extracted_text)
print(f"  All part numbers: {all_parts}")

print("\n✅ GUI path test complete!")
