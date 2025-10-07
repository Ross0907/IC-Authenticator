# IC Authentication System - Main Launcher# IC Authentication System - Quick Start Script

# Automated Optical Inspection (AOI) for Counterfeit IC Detection# This script helps set up and run the IC authentication system



Write-Host "========================================" -ForegroundColor CyanWrite-Host "=====================================" -ForegroundColor Cyan

Write-Host "IC Authentication System - AOI Platform" -ForegroundColor CyanWrite-Host "IC Authentication System - Setup" -ForegroundColor Cyan

Write-Host "Enhanced YOLO-OCR | Internet-Only Verification" -ForegroundColor CyanWrite-Host "=====================================" -ForegroundColor Cyan

Write-Host "========================================" -ForegroundColor CyanWrite-Host ""

Write-Host ""

# Check Python installation

# Check if virtual environment existsWrite-Host "Checking Python installation..." -ForegroundColor Yellow

if (-Not (Test-Path ".\.venv\Scripts\Activate.ps1")) {$pythonVersion = python --version 2>&1

    Write-Host "❌ Virtual environment not found!" -ForegroundColor Redif ($LASTEXITCODE -eq 0) {

    Write-Host "   Please create it first:" -ForegroundColor Yellow    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green

    Write-Host "   python -m venv .venv" -ForegroundColor White} else {

    Write-Host "   & .\.venv\Scripts\Activate.ps1" -ForegroundColor White    Write-Host "✗ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red

    Write-Host "   pip install -r requirements.txt" -ForegroundColor White    exit 1

    exit 1}

}

# Check if virtual environment exists

# Activate virtual environmentWrite-Host ""

Write-Host "🔧 Activating virtual environment..." -ForegroundColor YellowWrite-Host "Checking virtual environment..." -ForegroundColor Yellow

& .\.venv\Scripts\Activate.ps1if (Test-Path "venv") {

    Write-Host "✓ Virtual environment found" -ForegroundColor Green

if ($LASTEXITCODE -ne 0) {    Write-Host "Activating virtual environment..." -ForegroundColor Yellow

    Write-Host "❌ Failed to activate virtual environment!" -ForegroundColor Red    .\venv\Scripts\Activate.ps1

    exit 1} else {

}    Write-Host "Creating virtual environment..." -ForegroundColor Yellow

    python -m venv venv

Write-Host "✅ Virtual environment activated" -ForegroundColor Green    Write-Host "✓ Virtual environment created" -ForegroundColor Green

Write-Host ""    Write-Host "Activating virtual environment..." -ForegroundColor Yellow

    .\venv\Scripts\Activate.ps1

# Display menu}

Write-Host "Select an option:" -ForegroundColor Cyan

Write-Host "  1. Run Main Application (GUI)" -ForegroundColor White# Check if dependencies are installed

Write-Host "  2. Run All Tests" -ForegroundColor WhiteWrite-Host ""

Write-Host "  3. Run Core Integration Test" -ForegroundColor WhiteWrite-Host "Checking dependencies..." -ForegroundColor Yellow

Write-Host "  4. Run Type 1 vs Type 2 Test" -ForegroundColor White$pipList = pip list 2>&1

Write-Host "  5. Run Final Integration Test" -ForegroundColor Whiteif ($pipList -match "opencv-python" -and $pipList -match "PyQt5") {

Write-Host "  6. View Project Structure" -ForegroundColor White    Write-Host "✓ Dependencies appear to be installed" -ForegroundColor Green

Write-Host "  7. View Documentation" -ForegroundColor White} else {

Write-Host "  8. Exit" -ForegroundColor White    Write-Host "Installing dependencies..." -ForegroundColor Yellow

Write-Host ""    Write-Host "(This may take several minutes...)" -ForegroundColor Gray

    pip install -r requirements.txt

$choice = Read-Host "Enter choice (1-8)"    if ($LASTEXITCODE -eq 0) {

        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green

switch ($choice) {    } else {

    "1" {        Write-Host "✗ Error installing dependencies" -ForegroundColor Red

        Write-Host ""        Write-Host "Please check requirements.txt and try manually:" -ForegroundColor Yellow

        Write-Host "🚀 Launching IC Authenticator GUI..." -ForegroundColor Green        Write-Host "  pip install -r requirements.txt" -ForegroundColor Gray

        Write-Host "   Enhanced Features:" -ForegroundColor Yellow        exit 1

        Write-Host "   • Dynamic YOLO-OCR with improved confidence" -ForegroundColor White    }

        Write-Host "   • Internet-only verification (legitimate sources)" -ForegroundColor White}

        Write-Host "   • Date code critical checking" -ForegroundColor White

        Write-Host "   • Type 1 (counterfeit) vs Type 2 (authentic) detection" -ForegroundColor White# Check for Tesseract

        Write-Host ""Write-Host ""

        python ic_authenticator.pyWrite-Host "Checking Tesseract OCR..." -ForegroundColor Yellow

    }$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"

    "2" {if (Test-Path $tesseractPath) {

        Write-Host ""    Write-Host "✓ Tesseract found at default location" -ForegroundColor Green

        Write-Host "🧪 Running All Tests..." -ForegroundColor Green} else {

        python run_tests.py    Write-Host "⚠ Tesseract not found at default location" -ForegroundColor Yellow

    }    Write-Host "  Download from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Gray

    "3" {    Write-Host "  (OCR will still work with other engines)" -ForegroundColor Gray

        Write-Host ""}

        Write-Host "🧪 Running Core Integration Test..." -ForegroundColor Green

        python tests\test_core_integration.py# Create necessary directories

    }Write-Host ""

    "4" {Write-Host "Creating directories..." -ForegroundColor Yellow

        Write-Host ""if (!(Test-Path "datasheet_cache")) {

        Write-Host "🧪 Running Type 1 vs Type 2 Test..." -ForegroundColor Green    New-Item -ItemType Directory -Path "datasheet_cache" | Out-Null

        python tests\test_type1_vs_type2.py    Write-Host "✓ Created datasheet_cache directory" -ForegroundColor Green

    }}

    "5" {if (!(Test-Path "reports")) {

        Write-Host ""    New-Item -ItemType Directory -Path "reports" | Out-Null

        Write-Host "🧪 Running Final Integration Test..." -ForegroundColor Green    Write-Host "✓ Created reports directory" -ForegroundColor Green

        python tests\test_final_integration.py}

    }

    "6" {# Ready to run

        Write-Host ""Write-Host ""

        if (Test-Path "PROJECT_STRUCTURE.md") {Write-Host "=====================================" -ForegroundColor Cyan

            Get-Content PROJECT_STRUCTURE.md | Select-Object -First 100Write-Host "Setup Complete!" -ForegroundColor Green

            Write-Host ""Write-Host "=====================================" -ForegroundColor Cyan

            Write-Host "📄 Full document: PROJECT_STRUCTURE.md" -ForegroundColor CyanWrite-Host ""

        } else {Write-Host "Starting IC Authentication System..." -ForegroundColor Yellow

            Write-Host "❌ PROJECT_STRUCTURE.md not found!" -ForegroundColor RedWrite-Host ""

        }

    }# Run the application

    "7" {python ic_authenticator.py

        Write-Host ""

        Write-Host "📚 Available Documentation:" -ForegroundColor Cyan# Keep window open if there's an error

        Write-Host ""if ($LASTEXITCODE -ne 0) {

        Write-Host "  Main Documentation:" -ForegroundColor Yellow    Write-Host ""

        Write-Host "    • README.md - Project overview" -ForegroundColor White    Write-Host "Application exited with error code: $LASTEXITCODE" -ForegroundColor Red

        Write-Host "    • PROJECT_STRUCTURE.md - File organization" -ForegroundColor White    Write-Host "Press any key to exit..." -ForegroundColor Gray

        Write-Host ""    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

        Write-Host "  In docs/ folder:" -ForegroundColor Yellow}

        Write-Host "    • ARCHITECTURE.md - System architecture" -ForegroundColor White
        Write-Host "    • USER_GUIDE.md - User manual" -ForegroundColor White
        Write-Host "    • INSTALL.md - Installation guide" -ForegroundColor White
        Write-Host "    • TROUBLESHOOTING.md - Problem solving" -ForegroundColor White
        Write-Host "    • MARKING_GUIDE.md - IC marking specs" -ForegroundColor White
        Write-Host ""
        Write-Host "  In tests/ folder:" -ForegroundColor Yellow
        Write-Host "    • tests\README.md - Testing guide" -ForegroundColor White
        Write-Host ""
    }
    "8" {
        Write-Host ""
        Write-Host "👋 Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host ""
        Write-Host "❌ Invalid choice! Please run again." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan