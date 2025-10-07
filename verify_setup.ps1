# Quick Verification Script
Write-Host "IC Authentication System - Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

& .\.venv\Scripts\Activate.ps1

$allPassed = $true

Write-Host "`n1. Checking File Structure..." -ForegroundColor Green
$requiredDirs = @("tests", "docs", "scripts", "legacy", "results")
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "   OK $dir/" -ForegroundColor White
    } else {
        Write-Host "   MISSING $dir/" -ForegroundColor Red
        $allPassed = $false
    }
}

Write-Host "`n2. Checking Core Files..." -ForegroundColor Green
$coreFiles = @("ic_authenticator.py", "verification_engine.py", "web_scraper.py", "dynamic_yolo_ocr.py")
foreach ($file in $coreFiles) {
    if (Test-Path $file) {
        Write-Host "   OK $file" -ForegroundColor White
    } else {
        Write-Host "   MISSING $file" -ForegroundColor Red
        $allPassed = $false
    }
}

Write-Host "`n3. Running Core Test..." -ForegroundColor Green
python tests\test_core_integration.py | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK Core integration test PASSED" -ForegroundColor White
} else {
    Write-Host "   FAILED Core integration test" -ForegroundColor Red
    $allPassed = $false
}

Write-Host "`n========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "SUCCESS: System is ready!" -ForegroundColor Green
    Write-Host "`nRun: .\run.ps1 to launch" -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Some checks failed" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan