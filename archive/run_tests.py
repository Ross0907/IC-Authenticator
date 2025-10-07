#!/usr/bin/env python3
"""
Test Runner for IC Detection System
Runs all tests in the tests/ directory
"""

import os
import sys
import subprocess
from pathlib import Path

def run_all_tests():
    """Run all test files in the tests directory"""
    print("🧪 IC Detection System - Test Runner")
    print("=" * 50)
    
    tests_dir = Path(__file__).parent / "tests"
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found in tests/ directory")
        return False
    
    print(f"📋 Found {len(test_files)} test files:")
    for test_file in sorted(test_files):
        print(f"   • {test_file.name}")
    
    print("\n🚀 Running tests...")
    print("-" * 30)
    
    passed = 0
    failed = 0
    
    for test_file in sorted(test_files):
        print(f"\n▶️  Running {test_file.name}...")
        try:
            result = subprocess.run([
                sys.executable, str(test_file)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✅ {test_file.name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_file.name} - FAILED")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
                failed += 1
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file.name} - TIMEOUT")
            failed += 1
        except Exception as e:
            print(f"💥 {test_file.name} - ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results Summary:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "   📈 Success Rate: 0%")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check output above for details.")
        return False

def run_specific_test(test_name):
    """Run a specific test file"""
    tests_dir = Path(__file__).parent / "tests"
    test_file = tests_dir / f"test_{test_name}.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"🚀 Running {test_file.name}...")
    try:
        result = subprocess.run([sys.executable, str(test_file)], timeout=60)
        return result.returncode == 0
    except Exception as e:
        print(f"💥 Error running test: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    sys.exit(0 if success else 1)