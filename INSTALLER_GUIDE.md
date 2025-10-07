# IC Authenticator - MSI Installer

## Quick Build Instructions

### Step 1: Build the MSI Installer

Simply run the PowerShell build script:

```powershell
.\build_msi.ps1
```

This will:
- Clean previous builds
- Build the application with all dependencies
- Create the MSI installer
- Display the installer location

### Step 2: Find Your Installer

After successful build, the MSI installer will be located in:
```
dist\IC Authenticator-2.1.0-win64.msi
```

### Step 3: Upload to GitHub Releases

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Upload the MSI file from the `dist` folder
4. Add release notes describing the features

---

## What's Included in the Installer

✅ **Application**: ICAuthenticator.exe  
✅ **GPU Support**: CUDA-enabled PyTorch for RTX 4060  
✅ **Test Images**: Sample IC images in `test_images` folder  
✅ **All Dependencies**: No additional installation needed  
✅ **Desktop Shortcut**: Automatically created during installation  

---

## Installation for End Users

### Requirements
- Windows 10/11 (64-bit)
- NVIDIA GPU with latest drivers (for GPU acceleration)
- ~2 GB disk space

### Installation Steps

1. **Download** the MSI installer from GitHub Releases
2. **Double-click** the MSI file
3. **Follow** the installation wizard
4. **Launch** from Desktop shortcut or Start Menu

That's it! No Python installation or manual dependency setup required.

---

## Installation Locations

**Program Files**: `C:\Program Files\IC Authenticator\`
```
├── ICAuthenticator.exe    (Main application)
├── test_images/           (Sample IC images)
├── yolov8n.pt            (YOLO model)
├── icon.ico              (Application icon)
├── LICENSE.txt           (License information)
├── README.md             (Documentation)
└── lib/                  (Python libraries & DLLs)
```

**Desktop**: Shortcut to ICAuthenticator.exe

---

## Troubleshooting Build Issues

### If build fails with "Module not found"
```powershell
pip install -r requirements_production.txt
```

### If MSI creation fails
Make sure you have:
- Python 3.8+ (64-bit)
- cx_Freeze installed: `pip install cx_Freeze`
- All dependencies: `pip install -r requirements_production.txt`

### If file is too large
The MSI will be ~1-2 GB due to PyTorch CUDA libraries. This is normal.

---

## Manual Build Commands

If the script doesn't work, use these manual commands:

```powershell
# Clean
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Build
python setup_msi.py build

# Create MSI
python setup_msi.py bdist_msi
```

---

## File Cleanup Performed

The following unnecessary files have been removed:
- ❌ Modern GUI files (gui_modern.py, gui_modern_production.py)
- ❌ Test files (test_*.py)
- ❌ Debug directories (final_production_debug, __pycache__)
- ❌ Documentation files (*.md except README.md)
- ❌ Temporary files and caches

Only essential production files remain.

---

## Testing the MSI

After building, test the installer:

1. Install on a clean Windows machine (or VM)
2. Launch the application from Desktop shortcut
3. Select a test image from the `test_images` folder
4. Verify GPU is detected (should show RTX 4060)
5. Confirm authentication works correctly

---

## Version Information

**Application**: IC Authenticator  
**Version**: 2.1.0  
**Architecture**: 64-bit  
**Python**: Embedded (no user installation needed)  
**GPU**: CUDA 11.8 (RTX 4060 optimized)  

---

## Support

For issues or questions, open an issue on GitHub.
