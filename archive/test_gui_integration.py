"""Test GUI integration with final production authenticator"""

import sys
import os

# Suppress Qt warnings
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ic_authenticator import ICAuthenticatorGUI, ProcessingThread

def test_gui_authentication():
    """Test GUI authentication with type1 image"""
    print("=" * 80)
    print("🧪 TESTING GUI INTEGRATION")
    print("=" * 80)
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = ICAuthenticatorGUI()
    
    # Test with type1.jpg
    test_image = "test_images/type1.jpg"
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return
    
    print(f"\n📸 Testing with: {test_image}")
    print("   Expected: ATMEGA328P, ATMEL manufacturer, date 1004")
    
    # Set up settings
    settings = {
        'ocr_method': 'enhanced_yolo',
        'use_enhanced_yolo': True,
        'preprocessing_method': 'Auto',
        'internet_only_verification': True,
        'date_code_critical': True,
        'use_final_production': True,
        'show_debug': True,
        'confidence_threshold': 0.7
    }
    
    # Create processing thread
    thread = ProcessingThread(test_image, settings)
    
    # Connect result signal
    result_received = []
    
    def on_result(result):
        result_received.append(result)
        print("\n" + "=" * 80)
        print("📊 RESULT RECEIVED")
        print("=" * 80)
        
        extracted = result.get('extracted_markings', {})
        print(f"\n🔬 Extracted Markings:")
        print(f"   Part Number: {extracted.get('part_number')}")
        print(f"   Manufacturer: {extracted.get('manufacturer')}")
        print(f"   Date Code: {extracted.get('date_code')}")
        
        ocr = result.get('ocr_details', {})
        print(f"\n📝 OCR Details:")
        print(f"   Method: {ocr.get('method')}")
        print(f"   Confidence: {ocr.get('confidence', 0):.1%}")
        
        print(f"\n🎯 Authentication:")
        print(f"   Authentic: {result.get('is_authentic')}")
        print(f"   Confidence: {result.get('confidence_score')}%")
        
        verification = result.get('verification', {})
        marking_val = verification.get('marking_validation', {})
        if marking_val:
            print(f"\n🏭 Manufacturer Validation:")
            print(f"   Manufacturer: {marking_val.get('manufacturer')}")
            print(f"   Validation Passed: {marking_val.get('validation_passed')}")
            
            issues = marking_val.get('issues', [])
            if issues:
                print(f"   Issues: {len(issues)}")
                for issue in issues:
                    print(f"      - [{issue.get('severity')}] {issue.get('message')}")
        
        anomalies = result.get('anomalies')
        if anomalies:
            print(f"\n⚠️  Anomalies: {len(anomalies)}")
            for anomaly in anomalies[:3]:
                print(f"   - {anomaly}")
        
        print(f"\n✅ Recommendation:")
        print(f"   {result.get('recommendation')}")
        
        # Verify expected results
        print("\n" + "=" * 80)
        print("✅ VERIFICATION")
        print("=" * 80)
        
        checks = []
        checks.append(("Part number", extracted.get('part_number') == 'ATMEGA328P'))
        checks.append(("Manufacturer", extracted.get('manufacturer') == 'ATMEL'))
        checks.append(("Date code present", '1004' in extracted.get('date_code', '')))
        checks.append(("Datasheet found", result.get('datasheet_found')))
        checks.append(("Result formatted", 'timestamp' in result))
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        all_passed = all(c[1] for c in checks)
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ ALL CHECKS PASSED - GUI INTEGRATION SUCCESSFUL!")
        else:
            print("❌ SOME CHECKS FAILED")
        print("=" * 80)
        
        QTimer.singleShot(100, app.quit)
    
    thread.result.connect(on_result)
    
    # Start processing
    thread.start()
    
    # Run app event loop with timeout
    QTimer.singleShot(30000, app.quit)  # 30 second timeout
    app.exec_()
    
    if not result_received:
        print("\n❌ No result received (timeout or error)")
        return False
    
    return True

if __name__ == "__main__":
    success = test_gui_authentication()
    sys.exit(0 if success else 1)
