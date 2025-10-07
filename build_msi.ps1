# Build MSI Installer for IC Authenticator
# Run this script to create the installer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IC Authenticator MSI Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clean previous builds
Write-Host "[1/4] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
Write-Host "   ✓ Cleaned" -ForegroundColor Green

# Build the application
Write-Host "[2/4] Building application..." -ForegroundColor Yellow
python setup_msi.py build
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✓ Built" -ForegroundColor Green

# Create MSI installer
Write-Host "[3/4] Creating MSI installer..." -ForegroundColor Yellow
python setup_msi.py bdist_msi
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ MSI creation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "   ✓ MSI Created" -ForegroundColor Green

# Find and display the MSI file
Write-Host "[4/4] Locating installer..." -ForegroundColor Yellow
$msiFiles = Get-ChildItem -Path "dist" -Filter "*.msi" -Recurse
if ($msiFiles.Count -gt 0) {
    $msiFile = $msiFiles[0]
    Write-Host "   ✓ Found: $($msiFile.Name)" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installer Location:" -ForegroundColor Yellow
    Write-Host "  $($msiFile.FullName)" -ForegroundColor White
    Write-Host ""
    Write-Host "Size: $([math]::Round($msiFile.Length/1MB, 2)) MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ready to upload to GitHub Releases!" -ForegroundColor Green
} else {
    Write-Host "   ✗ MSI file not found!" -ForegroundColor Red
    exit 1
}
