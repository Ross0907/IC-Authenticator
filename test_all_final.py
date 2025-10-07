"""
Final comprehensive test of all test images
Validates the complete system with updated date code extraction
"""

from final_production_authenticator import FinalProductionAuthenticator
from pathlib import Path
import time

def test_all_images():
    """Test all images in test_images folder"""
    
    print("="*80)
    print("🧪 FINAL COMPREHENSIVE SYSTEM TEST")
    print("="*80)
    
    # Initialize
    auth = FinalProductionAuthenticator()
    
    # Get all test images
    test_folder = Path('test_images')
    images = list(test_folder.glob('*.jpg')) + list(test_folder.glob('*.png')) + list(test_folder.glob('*.avif'))
    
    print(f"\n📁 Found {len(images)} test images\n")
    
    results = []
    
    for img_path in images:
        print(f"\n{'='*80}")
        print(f"🔍 Testing: {img_path.name}")
        print("="*80)
        
        try:
            result = auth.authenticate(str(img_path))
            
            part = result.get('part_number', 'N/A')
            dates = result.get('date_codes', [])
            conf = result.get('confidence', 0)
            auth_status = '✅ AUTHENTIC' if result.get('is_authentic') else '❌ COUNTERFEIT'
            datasheet = '✅' if result.get('datasheet_found') else '❌'
            
            print(f"\n📊 Result: {auth_status} ({conf}%)")
            print(f"Part: {part}")
            print(f"Dates: {dates}")
            print(f"Datasheet: {datasheet}")
            
            results.append({
                'image': img_path.name,
                'part': part,
                'dates': dates,
                'confidence': conf,
                'authentic': result.get('is_authentic'),
                'datasheet': result.get('datasheet_found')
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                'image': img_path.name,
                'error': str(e)
            })
        
        time.sleep(0.5)
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 SUMMARY REPORT")
    print("="*80)
    
    print(f"\n{'Image':<40} {'Part':<15} {'Conf':<6} {'Auth':<10} {'DS':<5}")
    print("-"*80)
    
    for r in results:
        if 'error' in r:
            print(f"{r['image']:<40} ERROR")
        else:
            img_name = r['image'][:39]
            part_name = r['part'][:14]
            conf = f"{r['confidence']}%"
            auth = '✅' if r['authentic'] else '❌'
            ds = '✅' if r['datasheet'] else '❌'
            print(f"{img_name:<40} {part_name:<15} {conf:<6} {auth:<10} {ds:<5}")
    
    # Count stats
    total = len([r for r in results if 'error' not in r])
    authentic = len([r for r in results if r.get('authentic')])
    with_datasheet = len([r for r in results if r.get('datasheet')])
    
    print(f"\n{'='*80}")
    print(f"Total Tested: {total}")
    print(f"Authentic: {authentic}")
    print(f"Counterfeit/Suspicious: {total - authentic}")
    print(f"Datasheets Found: {with_datasheet}/{total}")
    print("="*80)

if __name__ == "__main__":
    test_all_images()
