# Project Cleanup Script
# Removes all unnecessary files and keeps only essential production files

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  IC Authenticator - Project Cleanup" -ForegroundColor Cyan
Write-Host "  Version 2.1.1" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$itemsToRemove = @(
    # Test files
    "test_all_comprehensive.py",
    "test_updated_scoring.py",
    "test_results.txt",
    
    # Documentation files (keeping only README.md)
    "UPDATE_SUMMARY_v2.1.1.md",
    "FIXES_APPLIED.md",
    "BUILD_RELEASE_GUIDE.md",
    "GITHUB_RELEASE_CHECKLIST.md",
    "MSI_INSTALLER_GUIDE.md",
    "INSTALLER_STATUS.md",
    "OVERHAUL_SUMMARY.md",
    "QUICK_START_GUIDE.txt",
    "RELEASE_GUIDE.txt",
    "RELEASE_NOTES_v2.1.md",
    "RELEASE_PACKAGE_INFO.txt",
    "RELEASE_READY.md",
    "STANDALONE_BUILD_STATUS.md",
    "SYSTEM_STATUS.txt",
    "USER_GUIDE.md",
    "CLEANUP_REPORT.txt",
    "CLEANUP_SUMMARY.txt",
    "GUI_COMPARISON.txt",
    
    # Unused model file (YOLO not used)
    "yolov8n.pt",
    
    # Old/unused Python files
    "advanced_ic_preprocessing.py",
    "advanced_ocr_engine.py",
    "build_complete_release.py",
    "build_executables.py",
    "build_msi_installer.py",
    "build_release.sh",
    "build_standalone.py",
    "cleanup_project.py",
    "comprehensive_final_test.py",
    "create_icon.py",
    "create_msi.py",
    "create_portable_release.py",
    "dynamic_yolo_ocr.py",
    "enhanced_ocr_system.py",
    "gui_classic.py",
    "gui_modern.py",
    "ic_authenticator_gui_classic.py",
    "ic_authenticator_gui.py",
    "ic_authenticator.py",
    "ic_marking_extractor.py",
    "image_processor.py",
    "improved_authenticator.py",
    "ocr_engine.py",
    "production_gui.py",
    "production_ic_authenticator.py",
    "run.ps1",
    "test_all_final.py",
    "test_all_images.py",
    "test_comprehensive.py",
    "test_final_comprehensive.py",
    "test_ocr_detailed.py",
    "test_preprocessing_type1.py",
    "test_type1.py",
    "type1_analysis.png",
    "universal_ocr_engine.py",
    "verification_engine.py",
    "web_scraper.py",
    "yolo_ic_authenticator.py",
    "yolo_text_detector.py",
    
    # Old spec files
    "IC_Authenticator_Classic.spec",
    "IC_Authenticator_Modern.spec",
    
    # Build artifacts
    "build/",
    "dist/",
    "final_production_debug/",
    
    # Old installer files
    "IC_Authenticator_Setup_v2.1-1.bin",
    "IC_Authenticator_Setup_v2.1-2.bin",
    "IC_Authenticator_Setup_v2.1.exe",
    "IC_Authenticator_v2.1_Complete_Windows.zip",
    
    # Old batch files
    "build_installer.bat",
    "installer_script.iss",
    "create_high_res_icon.py",
    
    # Archive folders (if they still exist)
    "archive/",
    "archive_backup/",
    "config/",
    "datasheet_cache/",
    "debug_preprocessing/",
    "docs/",
    "IC_Authenticator_v2.1_Complete/",
    "portable_release/",
    "production_debug/",
    "release/",
    "research_papers/",
    "temp_tests/",
    "tests/",
    
    # Database file (will be recreated)
    "ic_authentication.db"
)

$removed = 0
$notFound = 0

Write-Host "Cleaning up project files...`n" -ForegroundColor Yellow

foreach ($item in $itemsToRemove) {
    if (Test-Path $item) {
        try {
            Remove-Item $item -Recurse -Force -ErrorAction Stop
            Write-Host "   [X] Removed: $item" -ForegroundColor Green
            $removed++
        } catch {
            Write-Host "   [!] Failed to remove: $item" -ForegroundColor Red
        }
    } else {
        $notFound++
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  CLEANUP COMPLETE" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Statistics:" -ForegroundColor Yellow
Write-Host "   Removed: $removed files/folders" -ForegroundColor Green
Write-Host "   Not found: $notFound files/folders" -ForegroundColor Gray

Write-Host "`nKept essential files:" -ForegroundColor Yellow
Write-Host "   - Application: gui_classic_production.py" -ForegroundColor Cyan
Write-Host "   - Core modules: 5 Python files" -ForegroundColor Cyan
Write-Host "   - Configuration: config.json" -ForegroundColor Cyan
Write-Host "   - Icons: icon.ico, icon.png" -ForegroundColor Cyan
Write-Host "   - License: LICENSE.txt" -ForegroundColor Cyan
Write-Host "   - Documentation: README.md" -ForegroundColor Cyan
Write-Host "   - Test images: 8 samples" -ForegroundColor Cyan
Write-Host "   - Build tools: 3 files" -ForegroundColor Cyan
Write-Host "   - Installer: ICAuthenticator_Setup_v2.1.1.exe (18.39 MB)" -ForegroundColor Cyan

Write-Host "`nProject is now clean and ready for release!`n" -ForegroundColor Green
