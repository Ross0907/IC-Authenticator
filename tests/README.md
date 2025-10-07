# IC Detection System - Tests

This directory contains all test files for the IC Detection System.

## Test Organization

All test files have been moved to this dedicated `tests/` folder for better organization and maintainability.

## Running Tests

### Run All Tests
```bash
# Activate virtual environment first
& .\.venv\Scripts\Activate.ps1

# Run all tests
python run_tests.py
```

### Run Specific Test
```bash
# Run a specific test by name (without test_ prefix and .py extension)
python run_tests.py core_integration
python run_tests.py final_integration
python run_tests.py type1_vs_type2
```

### Run Individual Test
```bash
# Run test directly
python tests\test_core_integration.py
python tests\test_final_integration.py
```

## Test Files

### Core Integration Tests
- `test_core_integration.py` - Tests core enhanced features without problematic dependencies
- `test_final_integration.py` - Comprehensive integration test of all enhanced features
- `test_enhanced_ui_integration.py` - UI integration verification

### Authentication Tests  
- `test_type1_vs_type2.py` - Type 1 (counterfeit) vs Type 2 (authentic) IC testing
- `test_verification_direct.py` - Direct verification engine testing

### YOLO & OCR Tests
- `test_yolo_integration.py` - YOLO-OCR integration testing
- `test_yolo_system.py` - YOLO system testing
- `test_ocr_methods.py` - OCR methods testing
- `test_advanced_preprocessing.py` - Advanced preprocessing testing

### Component Tests
- `test_atmega328p.py` - Specific ATMEGA328P testing
- `test_cypress_ic.py` - Cypress IC testing  
- `test_all_images.py` - All test images processing
- `test_complete_system.py` - Complete system testing
- `test_system.py` - General system testing
- `test_type2_focused.py` - Type 2 IC focused testing

## Test Environment

All tests automatically:
- Add the parent directory to Python path for imports
- Use the virtual environment when run from the main directory
- Test enhanced features like:
  - Dynamic YOLO-OCR with improved confidence
  - Internet-only verification with legitimate sources
  - Date code critical checking
  - Enhanced UI controls

## Expected Results

When tests pass, you should see:
- ✅ Enhanced YOLO and internet-only verification integrated
- ✅ System ready for production counterfeit detection
- 🎉 All enhanced features successfully integrated

## Troubleshooting

If tests fail:
1. Ensure virtual environment is activated: `& .\.venv\Scripts\Activate.ps1`
2. Install missing dependencies: `pip install -r requirements.txt`
3. Check that all enhanced features are properly integrated
4. Verify YOLO model and weights are available

## Test Runner Features

The `run_tests.py` script provides:
- Automatic test discovery
- Timeout protection (60 seconds per test)
- Summary reporting with pass/fail counts
- Individual test execution
- Comprehensive error reporting