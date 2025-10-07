# IC Authenticator - Create Portable Release
# Creates a standalone folder that can be zipped for distribution

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IC Authenticator - Portable Release" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$releaseName = "IC_Authenticator_v2.1_Portable"
$releaseDir = "dist\$releaseName"

# Create release directory
Write-Host "[1/5] Creating release directory..." -ForegroundColor Yellow
if (Test-Path $releaseDir) { Remove-Item -Recurse -Force $releaseDir }
New-Item -ItemType Directory -Path $releaseDir | Out-Null
Write-Host "   ✓ Created" -ForegroundColor Green

# Copy essential files
Write-Host "[2/5] Copying application files..." -ForegroundColor Yellow
Copy-Item "gui_classic_production.py" "$releaseDir\"
Copy-Item "final_production_authenticator.py" "$releaseDir\"
Copy-Item "database_manager.py" "$releaseDir\"
Copy-Item "marking_validator.py" "$releaseDir\"
Copy-Item "working_web_scraper.py" "$releaseDir\"
Copy-Item "yolov8n.pt" "$releaseDir\"
Copy-Item "icon.ico" "$releaseDir\"
Copy-Item "icon.png" "$releaseDir\"
Copy-Item "config.json" "$releaseDir\"
Copy-Item "LICENSE.txt" "$releaseDir\"
Copy-Item "README.md" "$releaseDir\"
Copy-Item "requirements_production.txt" "$releaseDir\requirements.txt"
Copy-Item -Recurse "test_images" "$releaseDir\test_images"
Write-Host "   ✓ Copied" -ForegroundColor Green

# Create launcher script
Write-Host "[3/5] Creating launcher..." -ForegroundColor Yellow
$launcherContent = @"
@echo off
title IC Authenticator
echo ========================================
echo   IC Authenticator v2.1
echo ========================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import torch, cv2, easyocr, PyQt5" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing dependencies... This may take 5-10 minutes.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo.
echo Starting IC Authenticator...
python gui_classic_production.py
if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start!
    pause
)
"@
Set-Content -Path "$releaseDir\ICAuthenticator.bat" -Value $launcherContent
Write-Host "   ✓ Created" -ForegroundColor Green

# Create README for users
Write-Host "[4/5] Creating user guide..." -ForegroundColor Yellow
$userReadme = @"
# IC Authenticator v2.1 - Portable Edition

## Quick Start

### Requirements
- Windows 10/11 (64-bit)
- Python 3.8+ installed (download from https://python.org)
- NVIDIA GPU with latest drivers (optional, for GPU acceleration)
- Internet connection (for first-time dependency installation)

### Installation

1. **Install Python** (if not already installed):
   - Download from https://python.org
   - During installation, CHECK "Add Python to PATH"

2. **Run the Application**:
   - Double-click `ICAuthenticator.bat`
   - First run will install dependencies automatically (~5-10 minutes)
   - Subsequent runs will start immediately

### Features

✅ **GPU Acceleration** - Automatic CUDA support for NVIDIA GPUs  
✅ **Advanced OCR** - Multi-variant text extraction with EasyOCR  
✅ **Datasheet Verification** - Automatic datasheet lookup and validation  
✅ **Test Images Included** - Sample IC images in `test_images` folder  
✅ **Comprehensive Analysis** - Date code validation, manufacturer verification  

### Usage

1. Launch the application using `ICAuthenticator.bat`
2. Click "Select IC Image" to load an image
3. Wait for analysis to complete (~1-3 seconds with GPU)
4. Review results in the tabbed interface:
   - **Result**: Overall authentication verdict
   - **Details**: Extracted markings and validation
   - **Datasheet**: Official documentation verification
   - **Debug**: OCR visualization and variants
   - **Raw Data**: JSON-formatted analysis results

### Troubleshooting

**"Python not found"**:
- Install Python from https://python.org
- Make sure "Add to PATH" was checked during installation

**"Failed to install dependencies"**:
- Open Command Prompt as Administrator
- Navigate to this folder
- Run: `pip install -r requirements.txt`

**GPU not detected**:
- Update NVIDIA drivers to latest version
- Reinstall PyTorch with CUDA: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`

**Slow performance**:
- Check GPU status in the Status tab
- CPU mode is 10-50x slower than GPU mode

### Files

```
IC_Authenticator_v2.1_Portable/
├── ICAuthenticator.bat        (Double-click to run)
├── gui_classic_production.py  (Main GUI application)
├── final_production_authenticator.py
├── database_manager.py
├── marking_validator.py
├── working_web_scraper.py
├── requirements.txt           (Python dependencies)
├── yolov8n.pt                (YOLO model)
├── icon.ico / icon.png       (Application icons)
├── config.json               (Configuration)
├── LICENSE.txt               (MIT License)
├── README.md                 (This file)
└── test_images/              (Sample IC images)
```

### Support

For issues or questions, visit the GitHub repository.

### License

MIT License - See LICENSE.txt for details

### Version Information

- Version: 2.1.0
- Release Date: October 2025
- Python: 3.8+
- CUDA: 11.8 (for GPU support)
"@
Set-Content -Path "$releaseDir\README.md" -Value $userReadme
Write-Host "   ✓ Created" -ForegroundColor Green

# Create ZIP file
Write-Host "[5/5] Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = "dist\$releaseName.zip"
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
Compress-Archive -Path $releaseDir -DestinationPath $zipPath -CompressionLevel Optimal
$zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
Write-Host "   ✓ Created" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Portable Release:" -ForegroundColor Yellow
Write-Host "  $zipPath" -ForegroundColor White
Write-Host ""
Write-Host "Size: $zipSize MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "To distribute:" -ForegroundColor Yellow
Write-Host "  1. Upload $releaseName.zip to GitHub Releases" -ForegroundColor White
Write-Host "  2. Users extract and run ICAuthenticator.bat" -ForegroundColor White
Write-Host "  3. Dependencies installed automatically on first run" -ForegroundColor White
Write-Host ""
Write-Host "Ready for GitHub Release!" -ForegroundColor Green
