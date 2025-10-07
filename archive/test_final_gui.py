"""
Quick GUI Test - Final Production Authenticator
Tests the integrated system through the UI
"""

from PyQt5.QtCore import QCoreApplication
import sys
from ic_authenticator import ProcessingThread

def test_gui_integration():
    print("="*100)
    print("🧪 TESTING GUI INTEGRATION - FINAL PRODUCTION AUTHENTICATOR")
    print("="*100)
    
    app = QCoreApplication(sys.argv)
    
    # Optimal settings (defaults)
    settings = {
        'use_final_production': True,  # ENABLED
        'date_code_critical': True,
        'internet_only_verification': True,
        'confidence_threshold': 0.7
    }
    
    test_images = [
        "test_images/type1.jpg",
        "test_images/type2.jpg"
    ]
    
    for img_path in test_images:
        print(f"\n{'='*100}")
        print(f"Testing: {img_path}")
        print('='*100)
        
        thread = ProcessingThread(img_path, settings)
        
        def on_status(msg):
            print(f"  Status: {msg}")
        
        def on_result(result):
            print(f"\n  ✅ RESULT:")
            print(f"     Part Number: {result.get('part_number')}")
            print(f"     Manufacturer: {result.get('manufacturer')}")
            print(f"     Date Code: {result.get('date_code')}")
            print(f"     OCR Confidence: {result.get('ocr_confidence', 0):.1f}%")
            print(f"     Datasheet: {result.get('datasheet_url')}")
            print(f"     Is Authentic: {result.get('is_authentic')}")
            print(f"     Confidence: {result.get('authenticity_confidence')}%")
            print(f"     GPU Used: {result.get('gpu_used', False)}")
            print(f"\n     Reasons:")
            reasons = result.get('authenticity_reasons', '')
            for line in reasons.split('\n'):
                print(f"       {line}")
            
            app.quit()
        
        def on_error(error_msg):
            print(f"  ❌ ERROR: {error_msg}")
            app.quit()
        
        thread.status.connect(on_status)
        thread.result.connect(on_result)
        
        thread.start()
        app.exec_()
    
    print(f"\n{'='*100}")
    print("✅ GUI INTEGRATION TEST COMPLETE")
    print("="*100)


if __name__ == "__main__":
    test_gui_integration()
