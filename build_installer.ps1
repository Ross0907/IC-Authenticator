# IC Authenticator - MSI Installer Builder
# Creates a professional Windows installer

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  IC Authenticator - Installer Builder" -ForegroundColor Cyan
Write-Host "  Version 3.0.1" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Prerequisites
Write-Host "[1/5] Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   OK Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ERROR Python not found!" -ForegroundColor Red
    Write-Host "   Please install Python 3.11 or later" -ForegroundColor Red
    exit 1
}

# Check PyInstaller
$pipShow = python -m pip show pyinstaller 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK PyInstaller installed" -ForegroundColor Green
} else {
    Write-Host "   Installing PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    Write-Host "   OK PyInstaller installed" -ForegroundColor Green
}

# Check Inno Setup
$innoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $innoSetupPath)) {
    Write-Host "   ERROR Inno Setup not found!" -ForegroundColor Red
    Write-Host "   Please download and install Inno Setup 6 from:" -ForegroundColor Yellow
    Write-Host "   https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   After installation, run this script again." -ForegroundColor Yellow
    exit 1
}
Write-Host "   OK Inno Setup found" -ForegroundColor Green

Write-Host ""

# Step 2: Clean previous builds
Write-Host "[2/5] Cleaning previous builds..." -ForegroundColor Yellow
$foldersToClean = @("build", "dist", "installer_output", "__pycache__")
foreach ($folder in $foldersToClean) {
    if (Test-Path $folder) {
        Remove-Item -Recurse -Force $folder -ErrorAction SilentlyContinue
        Write-Host "   OK Removed $folder" -ForegroundColor Green
    }
}
Write-Host ""

# Step 3: Create launcher executable
Write-Host "[3/5] Creating launcher executable..." -ForegroundColor Yellow
Write-Host "   This may take a minute..." -ForegroundColor Cyan

python create_launcher_exe.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR Failed to create launcher!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "ICAuthenticator.exe")) {
    Write-Host "   ERROR ICAuthenticator.exe not found!" -ForegroundColor Red
    exit 1
}

Write-Host "   OK Launcher created" -ForegroundColor Green
Write-Host ""

# Step 4: Build installer with Inno Setup
Write-Host "[4/5] Building installer..." -ForegroundColor Yellow
Write-Host "   Compiling with Inno Setup..." -ForegroundColor Cyan

& $innoSetupPath "installer.iss"

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR Installer build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "   OK Installer built" -ForegroundColor Green
Write-Host ""

# Step 5: Verify and display results
Write-Host "[5/5] Verifying installer..." -ForegroundColor Yellow

$installerFiles = Get-ChildItem -Path "installer_output" -Filter "*.exe" -ErrorAction SilentlyContinue

if ($installerFiles.Count -eq 0) {
    Write-Host "   ERROR Installer not found!" -ForegroundColor Red
    exit 1
}

$installer = $installerFiles[0]
$sizeGB = [math]::Round($installer.Length/1GB, 2)
$sizeMB = [math]::Round($installer.Length/1MB, 2)

Write-Host "   OK Installer verified" -ForegroundColor Green
Write-Host ""

# Success message
Write-Host "============================================" -ForegroundColor Green
Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installer Details:" -ForegroundColor Cyan
Write-Host "  Name    : $($installer.Name)" -ForegroundColor White
Write-Host "  Location: $($installer.FullName)" -ForegroundColor White
if ($sizeGB -ge 1) {
    Write-Host "  Size    : $sizeGB GB" -ForegroundColor White
} else {
    Write-Host "  Size    : $sizeMB MB" -ForegroundColor White
}
Write-Host ""
Write-Host "Features:" -ForegroundColor Cyan
Write-Host "  OK Automatic Python installation" -ForegroundColor Green
Write-Host "  OK Automatic dependency installation" -ForegroundColor Green
Write-Host "  OK Desktop shortcut" -ForegroundColor Green
Write-Host "  OK Start menu entry" -ForegroundColor Green
Write-Host "  OK Test images included" -ForegroundColor Green
Write-Host "  OK Uninstaller included" -ForegroundColor Green
Write-Host ""
Write-Host "Ready to distribute!" -ForegroundColor Green
Write-Host ""

# Optional: Open folder
$response = Read-Host "Open installer folder? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    explorer.exe "installer_output"
}
