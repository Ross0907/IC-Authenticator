# Build IC Authenticator Executable
# Step 1: Create standalone executable with PyInstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  IC Authenticator Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clean previous builds
Write-Host "[1/2] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
Write-Host "   ✓ Cleaned" -ForegroundColor Green

# Build with PyInstaller
Write-Host "[2/2] Building executable..." -ForegroundColor Yellow
Write-Host "   This may take 5-10 minutes..." -ForegroundColor Gray
pyinstaller --clean ICAuthenticator.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "   ✓ Built" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find the executable
$exePath = "dist\ICAuthenticator\ICAuthenticator.exe"
if (Test-Path $exePath) {
    $exeInfo = Get-Item $exePath
    $folderSize = (Get-ChildItem "dist\ICAuthenticator" -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB
    
    Write-Host "Executable Location:" -ForegroundColor Yellow
    Write-Host "  dist\ICAuthenticator\ICAuthenticator.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "Total Size: $([math]::Round($folderSize, 2)) GB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To create MSI installer:" -ForegroundColor Yellow
    Write-Host "  1. Test the executable first: .\dist\ICAuthenticator\ICAuthenticator.exe" -ForegroundColor White
    Write-Host "  2. Use Advanced Installer or WiX to package as MSI" -ForegroundColor White
    Write-Host ""
    Write-Host "Ready for distribution!" -ForegroundColor Green
} else {
    Write-Host "✗ Executable not found!" -ForegroundColor Red
    exit 1
}
