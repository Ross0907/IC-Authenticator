"""
Test UI Integration with Production Authenticator
Verifies the production system works correctly through the UI processing thread
"""

from PyQt5.QtCore import QCoreApplication
import sys
from ic_authenticator import ProcessingThread

def test_ui_integration():
    """Test that production authenticator works through UI"""
    
    print("="*100)
    print("🧪 TESTING UI INTEGRATION WITH PRODUCTION AUTHENTICATOR")
    print("="*100)
    
    # Create Qt application
    app = QCoreApplication(sys.argv)
    
    # Test settings (enable production authenticator)
    settings = {
        'use_production_auth': True,  # USE PRODUCTION AUTHENTICATOR
        'use_enhanced_yolo': True
    }
    
    test_images = [
        "test_images/type1.jpg",
        "test_images/type2.jpg"
    ]
    
    for img_path in test_images:
        print(f"\n{'='*100}")
        print(f"Testing: {img_path}")
        print('='*100)
        
        # Create processing thread (simulates UI)
        thread = ProcessingThread(img_path, settings)
        
        # Connect signals to print results
        def on_progress(value):
            print(f"  Progress: {value}%")
        
        def on_status(msg):
            print(f"  Status: {msg}")
        
        def on_result(result):
            print(f"\n  ✅ RESULT RECEIVED:")
            print(f"     Part Number: {result.get('part_number')}")
            print(f"     Date Code: {result.get('date_code')}")
            print(f"     OCR Confidence: {result.get('ocr_confidence', 0):.1f}%")
            print(f"     Datasheet Found: {result.get('datasheet_found')}")
            print(f"     Is Authentic: {result.get('is_authentic')}")
            print(f"     Confidence: {result.get('authenticity_confidence')}%")
            print(f"     Reasons: {result.get('authenticity_reasons')}")
            
            app.quit()
        
        def on_error(error_msg):
            print(f"  ❌ ERROR: {error_msg}")
            app.quit()
        
        thread.progress.connect(on_progress)
        thread.status.connect(on_status)
        thread.result.connect(on_result)
        
        # Run thread
        thread.start()
        
        # Wait for completion
        app.exec_()
    
    print(f"\n{'='*100}")
    print("✅ UI INTEGRATION TEST COMPLETE")
    print("="*100)

if __name__ == "__main__":
    test_ui_integration()
