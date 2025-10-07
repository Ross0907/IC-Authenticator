"""
MSI Installer Setup for IC Authenticator
Creates a professional Windows installer with all dependencies
"""

import sys
from cx_Freeze import setup, Executable
import os
import shutil
import torch

# Application metadata
APP_NAME = "IC Authenticator"
APP_VERSION = "2.1.0"
APP_DESCRIPTION = "Professional IC Authentication System with GPU Acceleration"
APP_AUTHOR = "Ross"
COMPANY_NAME = "IC Detection"

# Get PyTorch DLL path for CUDA support
torch_path = os.path.dirname(torch.__file__)
torch_dlls = os.path.join(torch_path, "lib")

# Build options
build_exe_options = {
    "packages": [
        "os", "sys", "torch", "torchvision", "cv2", "PIL", "numpy",
        "easyocr", "PyQt5", "requests", "bs4", "sqlite3", "json",
        "datetime", "typing", "pathlib", "re", "concurrent.futures",
        "urllib3", "charset_normalizer", "certifi", "idna"
    ],
    "includes": [
        "PyQt5.QtCore", "PyQt5.QtGui", "PyQt5.QtWidgets",
        "torch", "torchvision", "easyocr", "cv2", "numpy.core._methods",
        "numpy.lib.format"
    ],
    "excludes": [
        "tkinter", "matplotlib", "scipy", "pandas", "jupyter",
        "notebook", "IPython", "test", "unittest", "pydoc",
        "setuptools", "distutils", "lib2to3"
    ],
    "include_files": [
        ("icon.ico", "icon.ico"),
        ("icon.png", "icon.png"),
        ("yolov8n.pt", "yolov8n.pt"),
        ("LICENSE.txt", "LICENSE.txt"),
        ("README.md", "README.md"),
        ("test_images", "test_images"),
        ("config.json", "config.json"),
        (torch_dlls, "lib"),  # Include PyTorch CUDA DLLs
    ],
    "optimize": 2,
    "include_msvcr": True,
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],
}

# Executable configuration
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Hide console window

executable = Executable(
    script="gui_classic_production.py",
    base=base,
    target_name="ICAuthenticator.exe",
    icon="icon.ico",
    shortcut_name=APP_NAME,
    shortcut_dir="DesktopFolder",
)

# MSI-specific options
bdist_msi_options = {
    "upgrade_code": "{12345678-1234-1234-1234-123456789012}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\IC Authenticator",
    "install_icon": "icon.ico",
    "summary_data": {
        "author": APP_AUTHOR,
        "comments": APP_DESCRIPTION,
    },
}

# Setup configuration
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=[executable],
)
