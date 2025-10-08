"""
IC Authenticator - Dependency Installer
Robust dependency installation with error handling and progress tracking
"""
import sys
import subprocess
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')
    except:
        pass

def run_pip_command(command, description, retry_count=3):
    """Run pip command with retry logic"""
    print(f"\n{'='*60}")
    print(f"Installing: {description}")
    print(f"{'='*60}")
    
    for attempt in range(retry_count):
        try:
            if attempt > 0:
                print(f"\nRetry attempt {attempt + 1}/{retry_count}...")
                time.sleep(2)
            
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            print(f"[OK] {description} installed successfully")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"[ERROR] Timeout installing {description}")
            if attempt < retry_count - 1:
                print("  Retrying with longer timeout...")
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error installing {description}:")
            print(f"  {e.stderr[:500]}")  # Print first 500 chars of error
            if attempt < retry_count - 1:
                print("  Retrying...")
        
        except Exception as e:
            print(f"[ERROR] Unexpected error: {str(e)}")
            if attempt < retry_count - 1:
                print("  Retrying...")
    
    print(f"\n[FAILED] Failed to install {description} after {retry_count} attempts")
    return False

def main():
    """Main installation routine"""
    print("\n" + "="*60)
    print("IC AUTHENTICATOR - DEPENDENCY INSTALLER")
    print("="*60)
    print("\nThis will install all required dependencies.")
    print("Installation may take 10-20 minutes depending on internet speed.")
    print("\nPlease be patient and do not close this window.")
    print("="*60)
    
    # Get Python executable
    python_exe = sys.executable
    print(f"\nUsing Python: {python_exe}")
    
    # Check pip
    print("\nChecking pip...")
    try:
        subprocess.run([python_exe, "-m", "pip", "--version"], check=True, capture_output=True)
        print("[OK] pip is available")
    except:
        print("[ERROR] pip not found!")
        print("\nPlease ensure Python is installed correctly with pip.")
        return False
    
    # Track failures
    failed_packages = []
    
    # Step 1: Upgrade pip
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
        "Core Tools (pip, setuptools, wheel)"
    ):
        print("\n[WARNING] Could not upgrade pip, continuing anyway...")
    
    # Step 2: Install NumPy first (many packages depend on it)
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", "numpy>=1.24.0"],
        "NumPy (numerical computing)"
    ):
        failed_packages.append("numpy")
    
    # Step 3: Install OpenCV (headless version - no GUI dependencies)
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", "opencv-python-headless>=4.8.0"],
        "OpenCV (computer vision)"
    ):
        # Try regular opencv-python as fallback
        print("\nTrying regular opencv-python as fallback...")
        if not run_pip_command(
            [python_exe, "-m", "pip", "install", "opencv-python>=4.8.0"],
            "OpenCV (regular version)"
        ):
            failed_packages.append("opencv-python")
    
    # Step 4: Install Pillow
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", "Pillow>=10.0.0"],
        "Pillow (image processing)"
    ):
        failed_packages.append("Pillow")
    
    # Step 5: Install PyQt5
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", "PyQt5>=5.15.0"],
        "PyQt5 (GUI framework)"
    ):
        failed_packages.append("PyQt5")
    
    # Step 6: Install scipy and scikit-image
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", "scipy>=1.11.0", "scikit-image>=0.21.0"],
        "Scientific Computing (SciPy, scikit-image)"
    ):
        failed_packages.append("scipy/scikit-image")
    
    # Step 7: Install PyTorch with CUDA
    print("\n" + "="*60)
    print("Installing PyTorch with CUDA support...")
    print("This is a large download (2-3 GB) and may take several minutes")
    print("="*60)
    
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", 
         "torch>=2.0.0", "torchvision>=0.15.0",
         "--index-url", "https://download.pytorch.org/whl/cu118"],
        "PyTorch with CUDA 11.8"
    ):
        # Try CPU version as fallback
        print("\nCUDA version failed, trying CPU version...")
        if not run_pip_command(
            [python_exe, "-m", "pip", "install", "torch>=2.0.0", "torchvision>=0.15.0"],
            "PyTorch (CPU version)"
        ):
            failed_packages.append("torch")
    
    # Step 8: Install EasyOCR (requires torch)
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", "easyocr>=1.7.0"],
        "EasyOCR (text recognition)"
    ):
        failed_packages.append("easyocr")
    
    # Step 9: Install web scraping tools
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", 
         "requests>=2.31.0", "beautifulsoup4>=4.12.0", "lxml>=4.9.0"],
        "Web Scraping Tools (requests, beautifulsoup4, lxml)"
    ):
        failed_packages.append("web scraping tools")
    
    # Step 10: Install YOLO
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", "ultralytics>=8.0.0"],
        "Ultralytics YOLO (object detection)"
    ):
        failed_packages.append("ultralytics")
    
    # Step 11: Install string matching
    if not run_pip_command(
        [python_exe, "-m", "pip", "install", 
         "python-Levenshtein>=0.21.0", "rapidfuzz>=3.0.0"],
        "String Matching (Levenshtein, RapidFuzz)"
    ):
        failed_packages.append("string matching")
    
    # Summary
    print("\n" + "="*60)
    print("INSTALLATION SUMMARY")
    print("="*60)
    
    if not failed_packages:
        print("\n[SUCCESS] ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
        print("\nIC Authenticator is ready to use.")
        return True
    else:
        print("\n[WARNING] INSTALLATION COMPLETED WITH WARNINGS")
        print("\nThe following packages failed to install:")
        for pkg in failed_packages:
            print(f"  [X] {pkg}")
        print("\nThe application may not work correctly.")
        print("Please check your internet connection and try running the installer again.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        
        print("\n" + "="*60)
        input("\nPress ENTER to close this window...")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FATAL ERROR] {str(e)}")
        print("\nPlease report this error to the developer.")
        input("\nPress ENTER to close this window...")
        sys.exit(1)
