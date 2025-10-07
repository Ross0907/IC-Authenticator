# Quick Installation Guide

## Prerequisites

1. **Python 3.8+** installed on your system
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Tesseract OCR** (optional but recommended)
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR`

## Installation Steps

### Method 1: Automated Setup (Recommended)

1. Open PowerShell in the project directory
2. Run the setup script:
   ```powershell
   .\run.ps1
   ```
3. The script will:
   - Create a virtual environment
   - Install all dependencies
   - Check for Tesseract
   - Launch the application

### Method 2: Manual Setup

1. **Create virtual environment**
   ```powershell
   python -m venv venv
   ```

2. **Activate virtual environment**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   If you get an execution policy error:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```
   
   This will install:
   - OpenCV for image processing
   - PyQt5 for the GUI
   - EasyOCR, PaddleOCR, Tesseract for OCR
   - Web scraping libraries
   - And other required packages

4. **Test installation**
   ```powershell
   python test_system.py
   ```

5. **Run the application**
   ```powershell
   python ic_authenticator.py
   ```

## Troubleshooting

### "pip is not recognized"
- Make sure Python is added to PATH
- Restart your terminal after installing Python

### "python is not recognized"
- Use `py` instead of `python`:
  ```powershell
  py -m venv venv
  ```

### PyQt5 installation fails
- Try installing Visual C++ Redistributable:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

### Tesseract not found
- The system will still work with EasyOCR and PaddleOCR
- To use Tesseract, install it and add to PATH
- Or update `ocr_engine.py` with the correct path

### Long installation time
- First-time installation may take 10-20 minutes
- Large packages like PyTorch (for EasyOCR) are being downloaded
- Subsequent runs will be much faster

### GPU acceleration
- If you have NVIDIA GPU and want to use it:
  ```powershell
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```

## Verify Installation

Run the test script to verify everything is working:
```powershell
python test_system.py
```

Expected output:
```
✓ OpenCV imported successfully
✓ NumPy imported successfully
✓ PyQt5 imported successfully
✓ ImageProcessor module loaded
✓ OCREngine module loaded
...
✓ All tests passed!
```

## First Run

1. Launch the application:
   ```powershell
   python ic_authenticator.py
   ```

2. Load a test image from `test_images` folder

3. Click "Analyze IC" button

4. View results in different tabs

## Next Steps

- Read `README.md` for detailed documentation
- Try `example_usage.py` for programmatic usage
- Adjust settings in `config.json` if needed

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Run `python test_system.py` to identify missing components
3. Review error messages carefully
4. Ensure all dependencies are installed correctly

## System Requirements

**Minimum:**
- Windows 10 or later
- 4GB RAM
- 2GB free disk space
- Dual-core CPU

**Recommended:**
- Windows 10/11
- 8GB+ RAM
- 5GB+ free disk space
- Quad-core CPU
- NVIDIA GPU (optional, for faster OCR)

## Disk Space Breakdown

- Python packages: ~2GB
- EasyOCR models: ~500MB
- PaddleOCR models: ~200MB
- Application: ~50MB
- Cache/Database: ~100MB

Total: ~3GB

## Support

For additional help, refer to:
- `README.md` - Comprehensive documentation
- `example_usage.py` - Usage examples
- Research PDFs - Technical background
