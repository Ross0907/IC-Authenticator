@echo off
echo ============================================================
echo Installing PyTorch with CUDA 11.8 support for RTX 4060
echo ============================================================

echo.
echo Uninstalling existing PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo Installing PyTorch with CUDA 11.8...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo.
echo ============================================================
echo Installation complete! Testing CUDA availability...
echo ============================================================
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

echo.
pause
