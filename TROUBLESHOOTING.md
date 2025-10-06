# Troubleshooting Guide - IC Authentication System

## Common Issues and Solutions

### 1. PowerShell Script Errors

**Issue:** `Missing closing '}' in statement block`
**Solution:**
```powershell
# If run.ps1 has errors, use manual approach:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python ic_authenticator.py
```

**Issue:** `Execution policy prevents script from running`
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 2. JSON Serialization Errors

**Issue:** `TypeError: Object of type bool is not JSON serializable`
**Status:** ✅ FIXED - The system now automatically converts NumPy types to native Python types

**What was the problem:**
- NumPy boolean/integer/float types aren't directly JSON serializable
- Verification engine was returning `np.bool_` instead of Python `bool`

**The fix:**
- Added `_convert_to_serializable()` method to handle type conversion
- Automatically converts all NumPy types before JSON serialization

---

### 3. OCR Warnings

**Issue:** `Tesseract error: tesseract is not installed or it's not in your PATH`

**Solution 1: Install Tesseract (Recommended)**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (use default location: `C:\Program Files\Tesseract-OCR`)
3. Restart application

**Solution 2: Use without Tesseract**
- System will automatically fall back to EasyOCR and PaddleOCR
- Select "EasyOCR" or "PaddleOCR" from dropdown (not "Ensemble")
- Performance will be similar, just without Tesseract's contribution

**To verify Tesseract is working:**
```powershell
tesseract --version
```

---

### 4. Network Connection Issues

**Issue:** `Failed to resolve 'www.datasheetcatalog.com'`

**Causes:**
- No internet connection
- Firewall blocking Python
- DNS resolution issues
- Website temporarily down

**Solutions:**

**A. Check Internet Connection:**
```powershell
ping google.com
```

**B. Allow Python through Firewall:**
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add Python.exe from your installation

**C. Use Offline Mode:**
- The system will work with cached data
- Analysis will proceed without datasheet lookup
- Confidence scores may be lower without official specs

**D. Configure Proxy (if behind corporate firewall):**
Edit `web_scraper.py` and add proxy settings:
```python
self.proxies = {
    'http': 'http://proxy.company.com:8080',
    'https': 'http://proxy.company.com:8080',
}
```

Then in requests:
```python
response = requests.get(url, headers=self.headers, proxies=self.proxies)
```

---

### 5. EasyOCR Model Download

**Issue:** `Downloading detection model, please wait...` (takes long time)

**Explanation:**
- First run downloads ~500MB of models
- Normal behavior, only happens once
- Models cached in `~/.EasyOCR/model/`

**Solutions:**

**A. Be Patient:**
- Initial download may take 5-15 minutes depending on connection
- Progress bar shows completion status
- Subsequent runs will be much faster

**B. Pre-download Models:**
```python
import easyocr
reader = easyocr.Reader(['en'], gpu=False)
```

**C. Use Alternative OCR:**
- Select "PaddleOCR" instead (smaller models)
- Or "Tesseract" (no download needed if installed)

---

### 6. GPU Warnings

**Issue:** `Using CPU. Note: This module is much faster with a GPU.`

**Explanation:**
- EasyOCR detects no CUDA-capable GPU
- Will use CPU (slower but works fine)
- Not an error, just informational

**Solutions:**

**A. Accept CPU Performance:**
- Adds 10-20 seconds to processing
- Perfectly functional for normal use
- No action needed

**B. Enable GPU (if you have NVIDIA GPU):**
```powershell
# Uninstall CPU PyTorch
pip uninstall torch torchvision

# Install GPU version
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**C. Use Faster OCR:**
- Select "PaddleOCR" (faster on CPU)
- Or "Tesseract" (no GPU needed)

---

### 7. Import Errors

**Issue:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall all dependencies
pip install -r requirements.txt

# Verify installation
python test_system.py
```

**Common missing modules:**
- `opencv-python` → `pip install opencv-python`
- `PyQt5` → `pip install PyQt5`
- `easyocr` → `pip install easyocr`

---

### 8. Image Loading Issues

**Issue:** Image won't load or displays as black

**Solutions:**

**A. Check Image Format:**
- Supported: PNG, JPG, JPEG, BMP, TIFF
- Not supported: GIF, WebP, HEIC

**B. Check Image Path:**
- No special characters in path
- No spaces in folder names (or use quotes)

**C. Check Image Size:**
- Minimum: 640x480 pixels
- Maximum: Limited by RAM (usually < 10MB)

**D. Convert Image:**
```python
from PIL import Image
img = Image.open('input.webp')
img.save('output.png')
```

---

### 9. Poor OCR Results

**Issue:** System extracts incorrect text or gibberish

**Solutions:**

**A. Improve Image Quality:**
- Increase resolution (1280x960 or higher)
- Better lighting (diffuse, even)
- Sharp focus on IC markings
- Remove glare/reflections

**B. Try Different OCR Methods:**
1. Start with "Ensemble" (most accurate)
2. If slow, try "EasyOCR" (good for difficult text)
3. Try "PaddleOCR" (fast and accurate)
4. Try "Tesseract" (good for standard fonts)

**C. Preprocess Image:**
```python
import cv2
img = cv2.imread('ic_image.jpg')
# Increase contrast
img = cv2.convertScaleAbs(img, alpha=1.5, beta=0)
cv2.imwrite('enhanced.jpg', img)
```

**D. Check Debug Layers:**
1. Go to "Debug Layers" tab
2. Check "Enhanced" layer - should have good contrast
3. Check "Text Segmentation" - should show text boxes
4. If text not detected, image needs improvement

---

### 10. Low Confidence Scores

**Issue:** System reports low confidence even though IC looks authentic

**Possible Causes:**
1. Datasheet not found online
2. Part number not extracted correctly
3. Manufacturer not recognized
4. Poor image quality
5. Unusual IC marking format

**Solutions:**

**A. Manual Verification:**
- Review extracted text in Results tab
- Compare with actual IC markings
- If extraction is correct, proceed with acceptance

**B. Improve Detection:**
- Better image quality
- Try different OCR method
- Clean IC surface before imaging

**C. Add Manufacturer to Database:**
Edit `config.json` and add manufacturer patterns:
```json
"manufacturers": {
  "patterns": {
    "YourManufacturer": ["ABBREV", "FULL NAME"]
  }
}
```

**D. Check Individual Scores:**
- Go to Verification tab
- Review detailed scores
- Identify which check failed
- Address specific issue

---

### 11. Application Crashes

**Issue:** Application closes unexpectedly

**Solutions:**

**A. Run from Terminal:**
```powershell
python ic_authenticator.py
```
This will show error messages

**B. Check Logs:**
Look for error messages in terminal output

**C. Test System:**
```powershell
python test_system.py
```

**D. Common Causes:**
- Out of memory (close other apps)
- Corrupted image file
- Missing dependencies

---

### 12. Batch Processing Issues

**Issue:** Batch processing fails or stops

**Solutions:**

**A. Process Smaller Batches:**
- Process 5-10 images at a time
- System needs RAM for each image

**B. Close Other Applications:**
- Free up system resources
- Especially RAM-intensive apps

**C. Use Example Script:**
```powershell
python example_usage.py
# Select option 2 for batch processing
```

---

### 13. Export Report Errors

**Issue:** Cannot export reports

**Solutions:**

**A. Check Permissions:**
- Ensure write access to target folder
- Try saving to Documents folder

**B. Use Different Format:**
- If JSON fails, try TXT
- If TXT fails, try JSON

**C. Manual Export:**
- Copy text from Results tab
- Paste into text editor
- Save manually

---

### 14. Database Errors

**Issue:** `Error saving to database`

**Solutions:**

**A. Check Database File:**
```powershell
# Delete corrupted database
Remove-Item ic_authentication.db

# Restart application (will create new database)
python ic_authenticator.py
```

**B. Check Disk Space:**
- Ensure sufficient disk space
- Database grows with each analysis

---

### 15. Slow Performance

**Issue:** Analysis takes too long (> 2 minutes)

**Solutions:**

**A. Disable Debug Options:**
- Uncheck all debug visualization boxes
- Saves processing time

**B. Use Single OCR Method:**
- Select "PaddleOCR" (fastest)
- Avoid "Ensemble" for speed

**C. Reduce Image Resolution:**
```python
import cv2
img = cv2.imread('large_image.jpg')
img = cv2.resize(img, (1280, 960))
cv2.imwrite('resized.jpg', img)
```

**D. Close Other Applications:**
- Free up CPU and RAM
- Close browser tabs, etc.

---

## Quick Diagnostic Commands

### Test Installation
```powershell
python test_system.py
```

### Check Python Version
```powershell
python --version  # Should be 3.8 or higher
```

### Verify Dependencies
```powershell
pip list | Select-String "opencv|PyQt5|easyocr|paddleocr"
```

### Test Tesseract
```powershell
tesseract --version
```

### Check Network
```powershell
ping google.com
```

### Free Disk Space
```powershell
Get-PSDrive C
```

---

## Getting Help

If issues persist:

1. **Check Documentation:**
   - README.md
   - USER_GUIDE.md
   - This troubleshooting guide

2. **Run Diagnostics:**
   ```powershell
   python test_system.py
   ```

3. **Review Debug Layers:**
   - Enable all debug options
   - Check each processing layer
   - Identify where process fails

4. **Collect Information:**
   - Python version
   - Error messages (full traceback)
   - Test image that fails
   - Steps to reproduce

5. **Try Example Script:**
   ```powershell
   python example_usage.py
   ```
   If this works, issue is GUI-related

---

## Prevention Best Practices

1. **Keep System Updated:**
   ```powershell
   pip install --upgrade -r requirements.txt
   ```

2. **Regular Testing:**
   - Run test_system.py monthly
   - Verify with known good images

3. **Backup Database:**
   ```powershell
   Copy-Item ic_authentication.db ic_authentication.backup.db
   ```

4. **Monitor Performance:**
   - Track analysis times
   - Note confidence score trends
   - Review failed analyses

5. **Image Quality Standards:**
   - Maintain consistent lighting setup
   - Use fixed camera position
   - Document imaging procedure

---

**Last Updated:** October 7, 2025
**System Version:** 1.0.0
