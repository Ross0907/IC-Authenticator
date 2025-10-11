"""
Quick System Check - Verify GPU and core functionality
Run this to verify system is working correctly
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
    except:
        pass

def check_system():
    """Quick system health check"""
    print("\n" + "="*60)
    print("IC AUTHENTICATOR - SYSTEM CHECK")
    print("="*60)
    
    issues = []
    
    # Check GPU
    print("\n[1/4] Checking GPU...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  ✓ GPU: {torch.cuda.get_device_name(0)}")
            print(f"  ✓ CUDA: {torch.version.cuda}")
        else:
            print("  ⚠ GPU not available (using CPU mode)")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        issues.append("GPU check failed")
    
    # Check PDF viewer
    print("\n[2/4] Checking PDF viewer...")
    try:
        import fitz
        print(f"  ✓ PyMuPDF: {fitz.__version__}")
    except:
        print("  ✗ PyMuPDF not installed")
        issues.append("PDF viewer unavailable")
    
    # Check authenticator
    print("\n[3/4] Checking authenticator...")
    try:
        from smart_ic_authenticator import SmartICAuthenticator
        print("  ✓ Authenticator module loaded")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        issues.append("Authenticator failed to load")
    
    # Check datasheet cache
    print("\n[4/4] Checking datasheet cache...")
    try:
        cache_dir = os.path.join(os.path.dirname(__file__), 'datasheet_cache')
        if os.path.exists(cache_dir):
            pdfs = [f for f in os.listdir(cache_dir) if f.endswith('.pdf')]
            print(f"  ✓ Cache: {len(pdfs)} PDFs")
        else:
            print("  ℹ Cache directory will be created on first use")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        issues.append("Cache check failed")
    
    # Summary
    print("\n" + "="*60)
    if not issues:
        print("✓ ALL CHECKS PASSED - System ready!")
        print("="*60)
        return True
    else:
        print(f"⚠ {len(issues)} issue(s) found:")
        for issue in issues:
            print(f"  • {issue}")
        print("="*60)
        return False

if __name__ == "__main__":
    try:
        success = check_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)
