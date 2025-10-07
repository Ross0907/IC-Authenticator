# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for IC Authenticator
Creates a standalone executable with all dependencies
"""

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect data files
datas = [
    ('icon.ico', '.'),
    ('icon.png', '.'),
    ('yolov8n.pt', '.'),
    ('LICENSE.txt', '.'),
    ('README.md', '.'),
    ('test_images', 'test_images'),
    ('config.json', '.'),
]

# Collect EasyOCR data
datas += collect_data_files('easyocr')

# Hidden imports - only essential ones
hiddenimports = [
    'torch',
    'torchvision',
    'easyocr',
    'cv2',
    'PIL',
    'numpy',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'requests',
    'bs4',
    'sqlite3',
]

a = Analysis(
    ['gui_classic_production.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'pandas', 'jupyter', 'notebook', 'IPython',
        'scipy', 'sklearn', 'pytest', 'onnx', 'transformers',
        'tkinter', 'sympy', 'networkx', 'tqdm.contrib'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ICAuthenticator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='ICAuthenticator',
)
