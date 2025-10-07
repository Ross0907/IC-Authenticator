import cv2
from pathlib import Path
from dynamic_yolo_ocr import DynamicYOLOOCR

test_dir = Path('test_images')
images = sorted(list(test_dir.glob('*.jpg')) + list(test_dir.glob('*.png')))

print(f'Testing {len(images)} images...')

ocr = DynamicYOLOOCR()

for img_path in images:
    print(f'\n{img_path.name}')
    image = cv2.imread(str(img_path))
    if image is None:
        print('  FAILED')
        continue
    result = ocr.extract_text_from_ic(image)
    text = result.get('final_text', '')
    conf = result.get('confidence', 0)
    if text:
        print(f'  TEXT: {text}')
        print(f'  CONF: {conf:.2f}')
    else:
        print(f'  NO TEXT (conf: {conf:.2f})')
