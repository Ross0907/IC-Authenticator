# IC Authentication System# IC Authentication System# IC Authentication System# IC Authenticator - Production System v3.0



**Version 2.1.0** | Production-Ready | GPU-Accelerated



A professional system for detecting counterfeit integrated circuits through advanced optical character recognition, manufacturer marking validation, and datasheet verification.A professional GPU-accelerated system for detecting counterfeit integrated circuits using advanced OCR, manufacturer marking validation, and datasheet verification.



---



## Table of Contents## OverviewA professional GPU-accelerated system for detecting counterfeit integrated circuits using advanced OCR, manufacturer marking validation, and datasheet verification.Advanced counterfeit IC detection system based on multiple research papers and production-grade AI/CV techniques.



1. [Overview](#overview)

2. [System Architecture](#system-architecture)

3. [Installation](#installation)This system analyzes IC chip images to determine authenticity by:

4. [Building the Installer](#building-the-installer)

5. [Usage](#usage)- Extracting text using GPU-accelerated OCR with enhanced preprocessing

6. [Authentication Process](#authentication-process)

7. [Technical Details](#technical-details)- Validating manufacturer markings against industry standards## Overview## 🎯 Features

8. [Project Structure](#project-structure)

9. [Configuration](#configuration)- Verifying part numbers through multiple datasheet sources

10. [Troubleshooting](#troubleshooting)

11. [License](#license)- Scoring authenticity based on comprehensive criteria (0-100%)



---



## Overview## RequirementsThis system analyzes IC chip images to determine authenticity by:### Core Capabilities



### Purpose



This system analyzes IC (Integrated Circuit) chip images to determine authenticity by examining multiple factors including text extraction, manufacturer markings, date codes, and datasheet verification. It employs GPU-accelerated OCR with multiple preprocessing methods to handle various IC marking types including laser-etched and engraved text.```bash- Extracting text using GPU-accelerated OCR with enhanced preprocessing- **Advanced OCR**: 7+ preprocessing methods with ensemble selection



### Key Featurespip install -r requirements.txt



- **Multi-Variant OCR Processing**: Applies 4+ preprocessing techniques per image```- Validating manufacturer markings against industry standards- **Multi-scale Enhancement**: Based on research papers (3x upscaling, rotation augmentation)

- **GPU Acceleration**: CUDA-enabled PyTorch and EasyOCR for 3-5x speed improvement

- **Manufacturer Validation**: Pattern-based verification of IC markings

- **Datasheet Verification**: Automatic lookup across multiple online sources

- **Comprehensive Scoring**: 100-point authentication system with detailed breakdown**Key Dependencies:**- Verifying part numbers through multiple datasheet sources- **Manufacturer Validation**: Pattern-based marking verification

- **Professional GUI**: Dark/light themes with tabbed result display

- Python 3.8+

### System Requirements

- PyQt5 (GUI framework)- Scoring authenticity based on comprehensive criteria (0-100%)- **Datasheet Verification**: Searches 5+ online sources

**Minimum:**

- Windows 10/11 (64-bit)- opencv-python (Image processing)

- Python 3.11 or later

- 8 GB RAM- easyocr (Text recognition)- **Confidence Scoring**: Detailed breakdown with traceability

- 2 GB disk space

- torch (GPU acceleration - optional but recommended)

**Recommended:**

- NVIDIA GPU with CUDA support (RTX series)- numpy, scipy (Image analysis)## Requirements- **GPU Acceleration**: CUDA support for faster processing

- 16 GB RAM

- Internet connection for datasheet verification- beautifulsoup4, requests (Datasheet verification)



---



## System Architecture**Optional:**



### High-Level Architecture- CUDA-capable GPU for 4-5x faster processing```bash### Research-Based Techniques



```

┌─────────────────────────────────────────────────────────────────┐

│                         GUI Layer (PyQt5)                        │## Usagepip install -r requirements.txtThis system implements methods from:

│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │

│  │   Summary    │  │   Detailed   │  │   Raw Data   │          │

│  │     Tab      │  │  Analysis Tab│  │     Tab      │          │

│  └──────────────┘  └──────────────┘  └──────────────┘          │### GUI Interface```1. **AutoDetect** - Novel Autoencoding Architecture for Counterfeit IC Detection

└────────────────────────────┬────────────────────────────────────┘

                             │

┌────────────────────────────▼────────────────────────────────────┐

│              Authentication Engine (Core Logic)                  │**Launch GUI Launcher** (choose between Classic or Modern interface):2. **IC SynthLogo** - Synthetic Logo Dataset for Counterfeit Detection

│                                                                  │

│  ┌──────────────────────────────────────────────────────────┐  │```bash

│  │                    Image Input                            │  │

│  └─────────────────────────┬────────────────────────────────┘  │python launch_gui.py**Key Dependencies:**3. **Harrison et al.** - Automated Laser Marking Analysis

│                            │                                    │

│  ┌─────────────────────────▼────────────────────────────────┐  │```

│  │            Enhanced Preprocessing Module                  │  │

│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │- Python 3.8+4. **Deep Learning AOI** - Component Marks Detection System

│  │  │  TrOCR   │ │ EasyOCR  │ │  docTR   │ │   Mild   │   │  │

│  │  │ Variant  │ │ Variant  │ │ Variant  │ │ Variant  │   │  │**Or launch directly:**

│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │

│  └─────────────────────────┬────────────────────────────────┘  │```bash- PyQt5 (GUI framework)5. **PCB Logo Classification** - Data Augmentation for Assurance

│                            │                                    │

│  ┌─────────────────────────▼────────────────────────────────┐  │python gui_classic_production.py   # Classic tabbed interface

│  │              GPU-Accelerated OCR (EasyOCR)                │  │

│  └─────────────────────────┬────────────────────────────────┘  │python gui_modern_production.py    # Modern card-based interface- opencv-python (Image processing)

│                            │                                    │

│  ┌─────────────────────────▼────────────────────────────────┐  │```

│  │                  Parallel Processing                      │  │

│  │  ┌──────────────┐              ┌──────────────┐          │  │- easyocr (Text recognition)## 📋 Requirements

│  │  │   Marking    │              │  Datasheet   │          │  │

│  │  │  Validation  │              │  Scraper     │          │  │### Steps:

│  │  │   Module     │              │   Module     │          │  │

│  │  └──────────────┘              └──────────────┘          │  │1. Click "Select IC Image" and choose a clear photo of an IC chip- torch (GPU acceleration - optional but recommended)

│  └─────────────────────────┬────────────────────────────────┘  │

│                            │                                    │2. Click "Authenticate IC" to start analysis

│  ┌─────────────────────────▼────────────────────────────────┐  │

│  │              Scoring & Decision Engine                    │  │3. View comprehensive results including:- numpy, scipy (Image analysis)```

│  │       (100-point system with confidence metrics)          │  │

│  └─────────────────────────┬────────────────────────────────┘  │   - Authenticity verdict (Authentic/Counterfeit)

│                            │                                    │

│  ┌─────────────────────────▼────────────────────────────────┐  │   - Confidence score (0-100%)- beautifulsoup4, requests (Datasheet verification)Python 3.8+

│  │              Database Storage (SQLite)                    │  │

│  └───────────────────────────────────────────────────────────┘  │   - Part number identification

└──────────────────────────────────────────────────────────────────┘

```   - Manufacturer and date codesCUDA 11.8+ (optional, for GPU acceleration)



### Data Flow Diagram   - Datasheet verification



```   - Detailed marking validation**Optional:**```

┌──────────────┐

│ IC Image     │

│ (JPG/PNG)    │

└──────┬───────┘### Programmatic Use- CUDA-capable GPU for 4-5x faster processing

       │

       ▼

┌──────────────────────────────────────────────┐

│  Preprocessing Pipeline                      │```python### Dependencies

│  ┌─────────────────────────────────────────┐│

│  │ 1. Load & Normalize                     ││from final_production_authenticator import FinalProductionAuthenticator

│  │ 2. Generate 4 Variants:                 ││

│  │    - TrOCR optimized (CLAHE + denoise)  ││## Usage```

│  │    - EasyOCR optimized (binary)         ││

│  │    - docTR optimized (sharpened)        ││authenticator = FinalProductionAuthenticator()

│  │    - Mild enhancement (basic CLAHE)     ││

│  └─────────────────────────────────────────┘│result = authenticator.authenticate("path/to/ic_image.jpg")torch>=2.0.0

└──────┬───────────────────────────────────────┘

       │

       ▼

┌──────────────────────────────────────────────┐print(f"Authentic: {result['is_authentic']}")### GUI Interfaceeasyocr>=1.7.0

│  OCR Processing (GPU-Accelerated)            │

│  ┌─────────────────────────────────────────┐│print(f"Confidence: {result['confidence']}%")

│  │ Process each variant with EasyOCR       ││

│  │ Extract: Text + Confidence + Boxes      ││print(f"Part Number: {result['part_number']}")opencv-python>=4.8.0

│  └─────────────────────────────────────────┘│

└──────┬───────────────────────────────────────┘print(f"Manufacturer: {result['manufacturer']}")

       │

       ▼```**Launch GUI Launcher** (choose between Classic or Modern interface):numpy>=1.24.0

┌──────────────────────────────────────────────┐

│  Best Result Selection                       │

│  ┌─────────────────────────────────────────┐│

│  │ Compare all variants                    ││## Authentication Criteria```bashPillow>=10.0.0

│  │ Select highest confidence result        ││

│  └─────────────────────────────────────────┘│

└──────┬───────────────────────────────────────┘

       │The system uses a 100-point scoring system:python launch_gui.pyrequests>=2.31.0

       ├──────────────────┬──────────────────┐

       │                  │                  │

       ▼                  ▼                  ▼

┌──────────────┐   ┌─────────────┐   ┌─────────────┐- **40 points**: Manufacturer marking validation (CRITICAL)```beautifulsoup4>=4.12.0

│   Marking    │   │  Datasheet  │   │ OCR Quality │

│  Validation  │   │   Lookup    │   │   Scoring   │  - Date code format (YYWW pattern)

│  (40 pts)    │   │  (30 pts)   │   │  (20 pts)   │

└──────┬───────┘   └──────┬──────┘   └──────┬──────┘  - Lot code presence```

       │                  │                  │

       └──────────────────┼──────────────────┘  - Marking completeness

                          │

                          ▼  **Or launch directly:**

              ┌───────────────────────┐

              │  Scoring Engine       │- **30 points**: Datasheet verification

              │  Total: 100 points    │

              │  Threshold: 70+       │  - Searches multiple sources (Microchip, TI, Infineon, Octopart, AllDatasheet, etc.)```bashInstall all dependencies:

              └───────────┬───────────┘

                          │  

                          ▼

              ┌───────────────────────┐- **20 points**: OCR qualitypython gui_classic_production.py   # Classic tabbed interface```bash

              │  Authentication       │

              │  Result               │  - Text extraction confidence

              │  • Authentic/Fake     │

              │  • Confidence %       │  python gui_modern_production.py    # Modern card-based interfacepip install -r requirements.txt

              │  • Detailed Breakdown │

              └───────────────────────┘- **10 points**: Date code presence

```

``````

---

**Verdict**: 70+ points AND valid markings = Authentic

## Installation



### Method 1: End User Installation (Recommended)

## GUI Features

**For users who want to run the application:**

### Steps:## 🚀 Quick Start

1. Download `ICAuthenticator_Setup_v2.1.0.exe` from the releases page

2. Run the installer (requires administrator privileges)Both interfaces include:

3. Follow the installation wizard

4. Python and dependencies will be installed automatically if needed- Dark/Light mode toggle1. Click "Select IC Image" and choose a clear photo of an IC chip

5. Launch from desktop shortcut or Start menu

- Real-time processing with progress tracking

**What the installer does:**

- Checks for Python 3.11+ installation- Comprehensive results display2. Click "Authenticate IC" to start analysis### GUI Application

- Downloads and installs Python if not present

- Installs all required dependencies automatically- Detailed marking validation

- Creates desktop shortcut

- Adds Start menu entry- Datasheet source and URL3. View comprehensive results including:```bash

- Sets up uninstaller

- OCR extraction details

### Method 2: Developer Installation

- Complete confidence score breakdown   - Authenticity verdict (Authentic/Counterfeit)python production_gui.py

**For developers who want to modify the code:**



#### Prerequisites

### Classic Interface   - Confidence score (0-100%)```

1. **Python 3.11 or later**

   ```- Three-tab layout (Summary, Detailed Analysis, Raw Data)

   Download from: https://www.python.org/downloads/

   During installation: Check "Add Python to PATH"- Traditional professional design   - Part number identification

   ```

- Organized information display

2. **Git** (optional, for cloning)

   ```   - Manufacturer and date codes### Command Line

   Download from: https://git-scm.com/downloads

   ```### Modern Interface



3. **NVIDIA GPU with CUDA support** (optional but recommended)- Card-based design with metrics   - Datasheet verification```python

   ```

   Check GPU compatibility: https://developer.nvidia.com/cuda-gpus- Three-column layout

   Install CUDA Toolkit 11.8: https://developer.nvidia.com/cuda-downloads

   ```- Contemporary aesthetics   - Detailed marking validationfrom production_ic_authenticator import ProductionICAuthenticator



#### Installation Steps



1. **Clone or download the repository**## Image Guidelines

   ```bash

   git clone https://github.com/Ross0907/Ic_detection.git

   cd Ic_detection

   ```For best results:### Programmatic Useauthenticator = ProductionICAuthenticator()



2. **Create virtual environment** (recommended)- ✅ Clear, focused images

   ```bash

   python -m venv .venv- ✅ Even lighting without glareresult = authenticator.authenticate("path/to/ic_image.jpg")

   

   # Activate on Windows:- ✅ High resolution (1000px+)

   .venv\Scripts\activate

   - ✅ Direct overhead angle```python

   # Activate on Linux/Mac:

   source .venv/bin/activate- ❌ Avoid blurry, shadowed, or low-resolution images

   ```

from final_production_authenticator import FinalProductionAuthenticatorprint(f"Part: {result.part_number}")

3. **Install dependencies**

   ```bash## Project Structure

   # Install all dependencies

   pip install -r requirements.txtprint(f"Authentic: {result.is_authentic}")

   

   # For GPU support (NVIDIA CUDA 11.8):```

   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

   ```.authenticator = FinalProductionAuthenticator()print(f"Confidence: {result.confidence}%")



4. **Verify installation**├── final_production_authenticator.py  # Core authentication engine

   ```bash

   # Check Python version├── enhanced_preprocessing.py          # Image preprocessingresult = authenticator.authenticate("path/to/ic_image.jpg")```

   python --version

   ├── marking_validator.py               # Manufacturer marking validation

   # Check if CUDA is available

   python -c "import torch; print('CUDA available:', torch.cuda.is_available())"├── working_web_scraper.py            # Datasheet verification

   

   # Check GPU name├── database_manager.py                # Analysis history storage

   python -c "import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

   ```├── gui_classic_production.py         # Classic GUIprint(f"Authentic: {result['is_authentic']}")### Batch Testing



5. **Run the application**├── gui_modern_production.py          # Modern GUI

   ```bash

   python gui_classic_production.py├── launch_gui.py                     # GUI launcherprint(f"Confidence: {result['confidence']}%")```bash

   ```

├── requirements.txt                   # Python dependencies

---

├── test_images/                       # Sample IC imagesprint(f"Part Number: {result['part_number']}")python test_comprehensive.py

## Building the Installer

└── research_papers/                   # Academic references

### Prerequisites for Building

```print(f"Manufacturer: {result['manufacturer']}")```

1. **Python 3.11+** with all dependencies installed

2. **PyInstaller** for creating the executable

   ```bash

   pip install pyinstaller## Technical Details```

   ```

3. **Inno Setup 6** for creating the installer

   ```

   Download from: https://jrsoftware.org/isdl.php**Text Extraction:**## 📊 System Architecture

   Install to default location: C:\Program Files (x86)\Inno Setup 6\

   ```- Multi-variant preprocessing (8+ methods including CLAHE, bilateral filtering, upscaling)



### Build Process- GPU-accelerated EasyOCR## Authentication Criteria



The project includes an automated build script that handles the entire process:- Automatic error correction and normalization



#### Automated Build (Recommended)### Preprocessing Pipeline



```powershell**Marking Validation:**

# Run the build script

.\build_installer.ps1- Based on IEEE research and manufacturer specificationsThe system uses a 100-point scoring system:```

```

- Validates date codes, lot codes, and marking patterns

**What the script does:**

- Detects common counterfeit indicatorsInput Image

1. **Checks prerequisites**

   - Verifies Python installation

   - Checks for PyInstaller

   - Verifies Inno Setup installation**Performance:**- **40 points**: Manufacturer marking validation (CRITICAL)    ↓



2. **Cleans previous builds**- Processing time: 0.5-5 seconds per image (GPU)

   - Removes old build/ directory

   - Removes old dist/ directory- Memory usage: ~2GB with GPU  - Date code format (YYWW pattern)Multi-Method Preprocessing (7 variants):

   - Removes old installer_output/ directory

- Supported formats: JPG, PNG, BMP

3. **Creates launcher executable**

   - Generates ICAuthenticator.exe (~10 MB)  - Lot code presence  1. Upscale + CLAHE + Unsharp Mask

   - Includes dependency checker

   - Adds user-friendly error dialogs## License



4. **Builds installer**  - Marking completeness  2. Morphological Gradient

   - Compiles with Inno Setup

   - Packages all application filesSee LICENSE.txt for details.

   - Adds Python installer (downloads if needed)

   - Creates uninstaller    3. Bilateral Filter + CLAHE



5. **Verifies output**## Research Foundation

   - Checks installer was created

   - Displays file size and location- **30 points**: Datasheet verification  4. Rotation Augmentation (-5°, 0°, +5°)



**Output:**This system implements techniques from peer-reviewed research papers available in the `research_papers/` directory, including:

```

installer_output/ICAuthenticator_Setup_v2.1.0.exe (17.42 MB)- IEEE: "Detection of Counterfeit Electronic Components"  - Searches multiple sources (Microchip, TI, Infineon, Octopart, AllDatasheet, etc.)  5. Sauvola Adaptive Thresholding

```

- "Analysis of Image Preprocessing and Binarization Methods for OCR-Based IC Detection"

#### Manual Build Steps

- "Deep Learning-based AOI System for Detecting Component Marks"    6. Sample-wise Standardization

If you prefer to build manually:



1. **Create the launcher executable**

   ```powershell---- **20 points**: OCR quality    ↓

   python create_launcher_exe.py

   ```

   This creates `ICAuthenticator.exe` in the current directory.

**Version**: 2.1    - Text extraction confidenceEnsemble OCR Selection

2. **Build the installer**

   ```powershell**Status**: Production Ready

   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

   ```      ↓

   This creates the installer in `installer_output/`

- **10 points**: Date code presenceBest Result (by confidence + quality)

### Build Configuration

```

The build process is configured through three files:

**Verdict**: 70+ points AND valid markings = Authentic

#### 1. `create_launcher_exe.py`

Defines how the launcher executable is created:### Authentication Scoring

- Python dependency checking

- User-friendly error dialogs## GUI Features

- Silent package installation

- Application launch logic| Component | Points | Description |



#### 2. `installer.iss`Both interfaces include:|-----------|--------|-------------|

Inno Setup configuration defining:

- Application metadata (name, version, publisher)- Dark/Light mode toggle| **Marking Validation** | 40 | Most critical - manufacturer marking patterns |

- Installation directory

- Files to include- Real-time processing with progress tracking| **Datasheet Found** | 30 | Official documentation from trusted sources |

- Shortcuts to create

- Uninstaller behavior- Comprehensive results display| **OCR Quality** | 20 | Text extraction confidence |

- Python auto-download and installation

- Detailed marking validation| **Date Code Present** | 10 | Manufacturing date verification |

#### 3. `build_installer.ps1`

PowerShell script that orchestrates the build:- Datasheet source and URL

- Prerequisite checking

- Build folder cleanup- OCR extraction details**Threshold**: 70+ points AND valid markings = AUTHENTIC

- Sequential build steps

- Error handling- Complete confidence score breakdown

- Output verification

## 🔬 Technical Details

### Customizing the Build

### Classic Interface

#### Change Application Version

- Three-tab layout (Summary, Detailed Analysis, Raw Data)### Preprocessing Methods

Edit `installer.iss` line 7:

```pascal- Traditional professional design

#define MyAppVersion "2.1.0"  // Change version number

```- Organized information display#### 1. Upscale + CLAHE + Unsharp Mask



#### Modify Files Included- **Research**: Paper 3 (Median blur for noise removal)



Edit `installer.iss` [Files] section:### Modern Interface- **Purpose**: Enhance engraved/laser-etched text

```pascal

[Files]- Card-based design with metrics- **Steps**:

Source: "your_file.py"; DestDir: "{app}"; Flags: ignoreversion

```- Three-column layout  - 3x cubic interpolation upscaling



#### Change Installation Directory- Contemporary aesthetics  - Median blur (removes salt & pepper noise)



Edit `installer.iss` line 23:  - CLAHE with clipLimit=8.0

```pascal

DefaultDirName={autopf}\{#MyAppName}  // Program Files by default## Image Guidelines  - Unsharp masking for edge enhancement

```



#### Add Build Steps

For best results:#### 2. Morphological Gradient

Edit `build_installer.ps1` and add steps between sections:

```powershell- ✅ Clear, focused images- **Research**: Paper 3 (Morphological operations for features)

# Add your custom build step here

Write-Host "[X/Y] Custom step..." -ForegroundColor Yellow- ✅ Even lighting without glare- **Purpose**: Detect text edges and boundaries

# Your commands

```- ✅ High resolution (1000px+)- **Steps**:



### Troubleshooting Build Issues- ✅ Direct overhead angle  - 2x upscaling



**Issue: PyInstaller not found**- ❌ Avoid blurry, shadowed, or low-resolution images  - CLAHE enhancement

```powershell

pip install --upgrade pyinstaller  - Morphological gradient with 3x3 kernel

```

## Project Structure  - Weighted combination with enhanced image

**Issue: Inno Setup not found**

- Install from: https://jrsoftware.org/isdl.php

- Or update path in build_installer.ps1

```#### 3. Rotation Augmentation

**Issue: Build fails with missing modules**

```powershell.- **Research**: Paper 2 (Data augmentation techniques)

pip install -r requirements.txt

```├── final_production_authenticator.py  # Core authentication engine- **Purpose**: Handle tilted/rotated chips



**Issue: Installer too large**├── enhanced_preprocessing.py          # Image preprocessing- **Steps**:

- Current design: 17.42 MB (downloads Python dynamically)

- Dependencies installed at runtime├── marking_validator.py               # Manufacturer marking validation  - Test angles: -5°, 0°, +5°

- To reduce size, remove test_images/ from installer.iss

├── working_web_scraper.py            # Datasheet verification  - Maintain image quality with cubic interpolation

---

├── database_manager.py                # Analysis history storage  - CLAHE on each variant

## Usage

├── gui_classic_production.py         # Classic GUI

### GUI Application

├── gui_modern_production.py          # Modern GUI#### 4. Sauvola Adaptive Thresholding

#### Starting the Application

├── launch_gui.py                     # GUI launcher- **Research**: Sauvola & Pietikäinen (2000)

**From Installer:**

- Double-click desktop shortcut├── requirements.txt                   # Python dependencies- **Purpose**: Handle uneven illumination

- Or: Start Menu > IC Authenticator

├── test_images/                       # Sample IC images- **Formula**: `T(x,y) = m(x,y) * (1 + k * ((s(x,y) / r) - 1))`

**From Source:**

```bash└── research_papers/                   # Academic references- **Parameters**: window_size=25, k=0.2, r=128

python gui_classic_production.py

``````



#### Interface Overview#### 5. Sample-wise Standardization



```## Technical Details- **Research**: Paper 4 (Preprocessing normalization)

┌──────────────────────────────────────────────────────────────────┐

│  IC Authentication System                         [☀ Light Mode] │- **Purpose**: Normalize brightness variations

├─────────────────────────┬────────────────────────────────────────┤

│                         │  ┌─ Summary ──────────────────────┐   │**Text Extraction:**- **Steps**:

│  [📁 Select Image]      │  │                                 │   │

│  [                    ] │  │  Part Number: [Detected]        │   │- Multi-variant preprocessing (8+ methods including CLAHE, bilateral filtering, upscaling)  - Normalize to [0, 1]

│   No image selected     │  │  Manufacturer: [Name]           │   │

│                         │  │  Verdict: AUTHENTIC             │   │- GPU-accelerated EasyOCR  - Center around mean

│  Image Preview:         │  │  Confidence: 85%                │   │

│  ┌──────────────────┐   │  │                                 │   │- Automatic error correction and normalization  - Standardize by std deviation

│  │                  │   │  └─────────────────────────────────┘   │

│  │   [IC Image]     │   │  ┌─ Detailed Analysis ────────────┐   │  - Rescale to [0, 255]

│  │                  │   │  │                                 │   │

│  └──────────────────┘   │  │  Marking Validation:            │   │**Marking Validation:**

│                         │  │  • Date Code: Valid (2425)      │   │

│  Debug Options:         │  │  • Lot Code: Present            │   │- Based on IEEE research and manufacturer specifications### OCR Ensemble Selection

│  ☑ Show Preprocessing  │  │  • Format: Correct              │   │

│  ☑ Show Text Boxes     │  │                                 │   │- Validates date codes, lot codes, and marking patterns

│                         │  │  Datasheet:                     │   │

│  [🔍 Authenticate IC]   │  │  • Source: Microchip            │   │- Detects common counterfeit indicatorsThe system runs OCR on all preprocessing variants and selects the best result based on:

│  ────────────────────── │  │  • Status: Found                │   │

│                         │  │  • URL: [Link]                  │   │

│  Status Information     │  │                                 │   │

│                         │  │  OCR Details:                   │   │**Performance:****Quality Score = (OCR Confidence × 0.6) + (Text Quality × 0.4)**

│  Ready - Select image   │  │  • Confidence: 87.3%            │   │

│                         │  │  • Method: enhanced_easyocr     │   │- Processing time: 0.5-5 seconds per image (GPU)

│  GPU: ✓ RTX 4060       │  │  • Text: [Extracted]            │   │

│  Time: 2.34s            │  └─────────────────────────────────┘   │- Memory usage: ~2GB with GPUText quality factors:

│  Size: 1024x768         │  ┌─ Raw Data ──────────────────────┐   │

└─────────────────────────┴──┴─────────────────────────────────────┘- Supported formats: JPG, PNG, BMP- Length (5-60 chars preferred)

```

- Alphanumeric content (both letters and numbers)

#### Step-by-Step Workflow

## License- Special character ratio (<15% preferred)

1. **Select Image**

   - Click "Select Image" button- Known IC pattern matching

   - Choose a clear photo of an IC chip

   - Supported formats: JPG, PNG, BMPSee LICENSE.txt for details.

   - Image preview appears in left panel

## 📈 Performance

2. **Configure Options** (optional)

   - Check "Show Preprocessing" to see preprocessing variants in Debug tab## Research Foundation

   - Check "Show Text Boxes" to see OCR detection boxes in Debug tab

### Test Results

3. **Start Authentication**

   - Click "Authenticate IC" buttonThis system implements techniques from peer-reviewed research papers available in the `research_papers/` directory, including:- **Average OCR Confidence**: 83.2%

   - Progress bar shows processing status

   - Status messages update in real-time- IEEE: "Detection of Counterfeit Electronic Components"- **Authentication Accuracy**: 5/6 images (83.3%)



4. **View Results**- "Analysis of Image Preprocessing and Binarization Methods for OCR-Based IC Detection"- **Processing Time**: 0.75-4.66s per image

   - **Summary Tab**: Quick overview with verdict and key information

   - **Detailed Analysis Tab**: Complete breakdown of all checks- "Deep Learning-based AOI System for Detecting Component Marks"- **GPU Speedup**: ~3-5x faster than CPU

   - **Raw Data Tab**: Technical details in JSON format

   - **Debug Images Tab**: Preprocessing variants and OCR visualization (if enabled)



5. **Theme Toggle**---### Supported IC Types

   - Click "Light Mode" or "Dark Mode" button in top-right

   - Interface colors update immediately- Microcontrollers (ATMEGA, STM32, PIC, etc.)

   - Preference is saved for next session

**Version**: 2.1  - Logic ICs (SN74 series, 4000 series)

#### Understanding Results

**Status**: Production Ready- ADCs/DACs (ADC0831, DAC0800, etc.)

**Summary Tab:**

- **Verdict**: AUTHENTIC or COUNTERFEIT- Memory chips (24C, 25C series)

- **Confidence**: 0-100% based on all factors- Processors (Cypress, Infineon, etc.)

- **Part Number**: Extracted IC part number

- **Manufacturer**: Identified chip manufacturer## 📝 Output Information

- **Date Code**: Manufacturing date (YYWW format)

### Detailed Results Include:

**Detailed Analysis Tab:**- ✅ **Image Information**: Name, path, dimensions, processing time

- **Marking Validation**: Expected vs actual format, issues found- ✅ **Part Details**: Part number, manufacturer, date codes

- **Datasheet Information**: Source, URL, found status- ✅ **OCR Details**: Extracted text, confidence, method used, preprocessing variant

- **OCR Details**: Confidence score, method used, preprocessing variant- ✅ **Marking Validation**: Expected vs detected format, issues found

- **Score Breakdown**: Points awarded for each component (40+30+20+10)- ✅ **Datasheet Info**: Found status, source, URL

- ✅ **Score Breakdown**: Points per component, final score

**Raw Data Tab:**- ✅ **Technical Info**: GPU usage, processing time

- Complete JSON output with all technical details

- Can be copied for logging or further analysis## 🛠️ Project Structure

- Includes debug information if options enabled

```

**Debug Images Tab** (if debug options enabled):Ic_detection/

- OCR visualization with bounding boxes├── production_ic_authenticator.py  # Main authenticator

- All 4 preprocessing variants├── production_gui.py                # GUI application

- Useful for troubleshooting OCR issues├── marking_validator.py             # Marking validation

├── working_web_scraper.py           # Datasheet scraper

### Programmatic Usage├── database_manager.py              # Database operations

├── test_comprehensive.py            # Testing script

#### Basic Authentication├── cleanup_project.py               # Cleanup utility

├── config.json                      # Configuration

```python├── requirements.txt                 # Dependencies

from final_production_authenticator import FinalProductionAuthenticator├── README.md                        # This file

├── test_images/                     # Test images

# Initialize authenticator├── research_papers/                 # Reference papers

authenticator = FinalProductionAuthenticator()├── datasheet_cache/                 # Cached datasheets

└── production_debug/                # Debug output

# Authenticate an image```

result = authenticator.authenticate("path/to/ic_image.jpg")

## 🧹 Project Cleanup

# Access results

print(f"Authentic: {result['is_authentic']}")To clean up old/obsolete files:

print(f"Confidence: {result['confidence']}%")```bash

print(f"Part Number: {result['part_number']}")python cleanup_project.py

print(f"Manufacturer: {result['manufacturer']}")```

```

This will:

#### Batch Processing- Archive obsolete files to `archive_backup/`

- Remove __pycache__ directories

```python- Keep only essential production files

import os- Generate cleanup report

from final_production_authenticator import FinalProductionAuthenticator

## 🔍 Troubleshooting

authenticator = FinalProductionAuthenticator()

### Low OCR Accuracy

# Process all images in a directory- Ensure image is well-lit and in focus

image_dir = "test_images"- Try higher resolution images (min 300x300)

results = []- Check for glare or reflections on chip surface



for filename in os.listdir(image_dir):### GPU Not Detected

    if filename.lower().endswith(('.jpg', '.png', '.bmp')):- Install CUDA 11.8+ from NVIDIA

        image_path = os.path.join(image_dir, filename)- Ensure PyTorch is installed with CUDA support:

        result = authenticator.authenticate(image_path)  ```bash

        results.append({  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

            'filename': filename,  ```

            'authentic': result['is_authentic'],

            'confidence': result['confidence'],### Datasheet Not Found

            'part_number': result['part_number']- Check internet connection

        })- Part number may be obsolete or uncommon

- Try manufacturer's website directly

# Print summary

for r in results:## 📖 Research Papers

    status = "✓" if r['authentic'] else "✗"

    print(f"{status} {r['filename']}: {r['confidence']}% - {r['part_number']}")All research papers referenced in this system are available in the `research_papers/` directory:

```

1. AutoDetect (Journal of Hardware and Systems Security, 2024)

#### Accessing Detailed Information2. IC SynthLogo (PCB Logo Classification)

3. Harrison et al. (Automated Laser Marking Analysis)

```python4. Deep Learning AOI (Component Marks Detection)

result = authenticator.authenticate("image.jpg")5. PCB Logo Classification (Data Augmentation)



# Marking validation details## 📜 License

marking = result.get('marking_validation', {})

print(f"Date Code: {marking.get('date_code')}")This project is licensed under the MIT License - see LICENSE.txt for details.

print(f"Lot Code: {marking.get('lot_code')}")

print(f"Marking Issues: {marking.get('issues', [])}")## 🤝 Contributing



# Datasheet informationContributions are welcome! Please:

datasheet = result.get('datasheet', {})1. Fork the repository

print(f"Datasheet Found: {datasheet.get('found')}")2. Create a feature branch

print(f"Source: {datasheet.get('source')}")3. Test thoroughly

print(f"URL: {datasheet.get('url')}")4. Submit a pull request



# OCR details## 📧 Support

ocr = result.get('ocr_details', {})

print(f"OCR Confidence: {ocr.get('confidence')}%")For issues or questions:

print(f"Preprocessing Method: {ocr.get('method')}")- Open an issue on GitHub

print(f"Extracted Text: {ocr.get('text')}")- Check research papers for technical details

- Review test_comprehensive.py for usage examples

# Score breakdown

scores = result.get('score_breakdown', {})## 🎯 Future Enhancements

print(f"Marking Score: {scores.get('marking_score', 0)}/40")

print(f"Datasheet Score: {scores.get('datasheet_score', 0)}/30")- [ ] Web-based interface

print(f"OCR Score: {scores.get('ocr_score', 0)}/20")- [ ] Mobile app support

print(f"Date Code Score: {scores.get('date_code_score', 0)}/10")- [ ] Additional IC manufacturer patterns

```- [ ] Database of known counterfeit patterns

- [ ] Automated reporting system

---- [ ] Integration with ERP systems



## Authentication Process---



### Scoring System**Version**: 3.0  

**Last Updated**: October 2025  

The authentication uses a 100-point scoring system divided into four components:**Status**: Production Ready ✅


```
┌──────────────────────────────────────────────────────────────┐
│                 Authentication Scoring                        │
├──────────────────────────────────────────────────────────────┤
│  Component               │ Points │ Description               │
├─────────────────────────┼────────┼──────────────────────────┤
│ Marking Validation       │   40   │ Most critical component  │
│ • Date Code Format       │   15   │   YYWW pattern (2425)    │
│ • Lot Code Presence      │   15   │   Manufacturer lot code  │
│ • Marking Completeness   │   10   │   All expected fields    │
├─────────────────────────┼────────┼──────────────────────────┤
│ Datasheet Verification   │   30   │ Official documentation   │
│ • Found on Official Site │   30   │   Trusted source         │
│ • Not Found              │    0   │   Suspicious             │
├─────────────────────────┼────────┼──────────────────────────┤
│ OCR Quality              │   20   │ Text extraction quality  │
│ • High Confidence (>80%) │   20   │   Clear, readable text   │
│ • Medium (60-80%)        │   15   │   Some uncertainty       │
│ • Low (<60%)             │   10   │   Poor image quality     │
├─────────────────────────┼────────┼──────────────────────────┤
│ Date Code Presence       │   10   │ Manufacturing date found │
│ • Valid Date Code        │   10   │   Proper format          │
│ • No Date Code           │    0   │   Missing or invalid     │
├─────────────────────────┼────────┼──────────────────────────┤
│ TOTAL                    │  100   │                          │
└──────────────────────────────────────────────────────────────┘

Authentication Decision:
• Score ≥ 70 AND valid markings → AUTHENTIC
• Score < 70 OR invalid markings → COUNTERFEIT
```

### Processing Pipeline

#### Stage 1: Image Preprocessing

```
Input Image
    │
    ├─→ Variant 1: TrOCR Optimized
    │   ├─ Normalize to [0, 255]
    │   ├─ Strong CLAHE (clipLimit=10.0)
    │   ├─ Denoise with fastNlMeans
    │   └─ Unsharp masking
    │
    ├─→ Variant 2: EasyOCR Optimized
    │   ├─ Normalize to [0, 255]
    │   ├─ CLAHE (clipLimit=6.0)
    │   ├─ Bilateral filter
    │   ├─ Adaptive threshold
    │   └─ Invert if needed
    │
    ├─→ Variant 3: docTR Optimized
    │   ├─ Normalize to [0, 255]
    │   ├─ Strong CLAHE (clipLimit=8.0)
    │   ├─ Gaussian blur
    │   └─ Sharpen
    │
    └─→ Variant 4: Mild Enhancement
        ├─ Normalize to [0, 255]
        └─ Mild CLAHE (clipLimit=3.0)
```

#### Stage 2: OCR Processing

```
4 Preprocessed Variants
    │
    ├─→ EasyOCR (GPU-Accelerated)
    │   ├─ Text Detection
    │   ├─ Text Recognition
    │   └─ Confidence Scoring
    │
    ├─→ Select Best Result
    │   ├─ Compare all variants
    │   ├─ Evaluate confidence scores
    │   └─ Select highest quality output
    │
    └─→ Text Extraction
        ├─ Raw text
        ├─ Bounding boxes
        └─ Confidence scores
```

#### Stage 3: Parallel Analysis

```
Extracted Text
    │
    ├─→ Marking Validation (40 pts)
    │   ├─ Parse text for patterns
    │   ├─ Extract date code (YYWW)
    │   ├─ Extract lot code
    │   ├─ Validate manufacturer format
    │   └─ Calculate marking score
    │
    ├─→ Datasheet Search (30 pts)
    │   ├─ Extract part number
    │   ├─ Search Microchip.com
    │   ├─ Search Texas Instruments
    │   ├─ Search Infineon
    │   ├─ Search Octopart
    │   ├─ Search AllDatasheet
    │   └─ Calculate datasheet score
    │
    └─→ OCR Quality Check (20 pts)
        ├─ Evaluate confidence
        ├─ Check text length
        ├─ Verify alphanumeric content
        └─ Calculate OCR score
```

#### Stage 4: Decision Engine

```
All Scores Collected
    │
    ├─→ Calculate Total Score
    │   Sum: Marking (40) + Datasheet (30) + OCR (20) + Date (10)
    │
    ├─→ Apply Decision Rules
    │   IF score ≥ 70 AND markings_valid:
    │       verdict = AUTHENTIC
    │   ELSE:
    │       verdict = COUNTERFEIT
    │
    ├─→ Generate Confidence
    │   confidence = (total_score / 100) * 100
    │
    └─→ Compile Results
        ├─ Verdict
        ├─ Confidence percentage
        ├─ Detailed breakdown
        ├─ Issues found
        └─ Recommendations
```

### Preprocessing Techniques

#### TrOCR Optimized Preprocessing

**Purpose**: Enhance engraved text while maintaining natural appearance

**Process**:
1. Normalize image to [0, 255] range
2. Apply strong CLAHE (Contrast Limited Adaptive Histogram Equalization)
   - clipLimit: 10.0
   - tileGridSize: (4, 4)
3. Denoise with fastNlMeansDenoising
   - h: 10 (filter strength)
   - templateWindowSize: 7
   - searchWindowSize: 21
4. Apply unsharp masking for crisp edges
   - Gaussian blur with sigma=3.0
   - Weight: 2.5 (enhanced) - 1.5 (blurred)

**Best For**: Laser-etched text, engraved markings, low-contrast ICs

#### EasyOCR Optimized Preprocessing

**Purpose**: Create high-contrast binary image

**Process**:
1. Normalize image to [0, 255] range
2. Apply moderate CLAHE
   - clipLimit: 6.0
   - tileGridSize: (8, 8)
3. Bilateral filter to reduce noise while preserving edges
   - d: 9 (neighborhood diameter)
   - sigmaColor: 75
   - sigmaSpace: 75
4. Adaptive threshold
   - Method: ADAPTIVE_THRESH_GAUSSIAN_C
   - blockSize: 25
   - C: 3
5. Auto-invert based on mean brightness

**Best For**: Printed text, stamp markings, high-contrast ICs

#### docTR Optimized Preprocessing

**Purpose**: Balance contrast and clarity

**Process**:
1. Normalize image to [0, 255] range
2. Apply strong CLAHE
   - clipLimit: 8.0
   - tileGridSize: (6, 6)
3. Gaussian blur with kernel (3, 3)
4. Sharpen using weighted addition
   - Weight: 1.8 (enhanced) - 0.8 (blurred)
5. Clip to valid range [0, 255]

**Best For**: Mixed marking types, variable lighting

#### Mild Enhancement Preprocessing

**Purpose**: Gentle enhancement for already-clear images

**Process**:
1. Normalize image to [0, 255] range
2. Apply mild CLAHE
   - clipLimit: 3.0
   - tileGridSize: (8, 8)

**Best For**: High-quality images, well-lit photos, clear markings

### OCR Best Result Selection

The system processes the image with all 4 preprocessing variants and selects the best result using a weighted quality score:

```
Quality Score = (OCR Confidence × 0.6) + (Text Quality × 0.4)

Where Text Quality considers:
• Text length (optimal: 5-60 characters)
• Alphanumeric content (both letters and numbers preferred)
• Special character ratio (< 15% preferred)
• Pattern matching (known IC patterns score higher)
```

---

## Technical Details

### Dependencies

#### Core Libraries

```
Python 3.11+          - Programming language
PyQt5 5.15+           - GUI framework
PyTorch 2.0+          - Deep learning backend
EasyOCR 1.7+          - OCR engine
OpenCV 4.8+           - Image processing
NumPy 1.24+           - Numerical computing
Pillow 10.0+          - Image handling
```

#### Web Scraping

```
requests 2.31+        - HTTP library
beautifulsoup4 4.12+  - HTML parsing
lxml 4.9+             - XML/HTML parser
```

#### Additional Tools

```
Ultralytics 8.0+      - YOLO object detection
python-Levenshtein    - String similarity
SQLite 3              - Database (built-in)
```

### GPU Acceleration

#### CUDA Support

The application automatically detects and uses NVIDIA CUDA GPUs when available:

```python
import torch

if torch.cuda.is_available():
    device = 'cuda'
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
else:
    device = 'cpu'
```

#### Performance Comparison

```
┌────────────────────────────────────────────────────────────────┐
│                Processing Time Comparison                      │
├────────────────────────┬──────────────┬────────────────────────┤
│ Hardware               │ Avg Time     │ Speedup vs CPU         │
├────────────────────────┼──────────────┼────────────────────────┤
│ CPU (Intel i7-12700)   │ 4.5-8.0s     │ 1.0x (baseline)        │
│ GPU (RTX 3060)         │ 1.2-2.5s     │ 3.0-3.8x faster        │
│ GPU (RTX 4060)         │ 0.8-2.0s     │ 3.5-5.6x faster        │
│ GPU (RTX 4090)         │ 0.5-1.2s     │ 5.0-9.0x faster        │
└────────────────────────────────────────────────────────────────┘
```

### Image Requirements

#### Recommended Specifications

```
┌────────────────────────────────────────────────────────────────┐
│                 Image Quality Guidelines                       │
├────────────────────────┬───────────────────────────────────────┤
│ Property               │ Recommended                           │
├────────────────────────┼───────────────────────────────────────┤
│ Resolution             │ 1000x1000 pixels minimum              │
│ Format                 │ JPG, PNG (lossless preferred)         │
│ Lighting               │ Diffuse, even illumination            │
│ Focus                  │ Sharp, no motion blur                 │
│ Angle                  │ Perpendicular to chip surface         │
│ Background             │ Contrasting, solid color              │
│ Chip Visibility        │ Full marking area visible             │
│ Glare/Reflections      │ None or minimal                       │
└────────────────────────────────────────────────────────────────┘
```

#### Common Issues and Solutions

```
Issue: Blurry text
Solution: Use tripod or stable surface, ensure proper focus

Issue: Uneven lighting
Solution: Use diffused light source, avoid direct overhead lighting

Issue: Glare on chip surface
Solution: Adjust light angle, use polarizing filter

Issue: Low resolution
Solution: Use higher quality camera or zoom in closer

Issue: Tilted chip
Solution: Ensure chip is flat and parallel to camera
```

### Database Schema

The application stores authentication results in an SQLite database:

```sql
CREATE TABLE authentication_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    image_path TEXT NOT NULL,
    part_number TEXT,
    manufacturer TEXT,
    is_authentic INTEGER,
    confidence REAL,
    marking_score INTEGER,
    datasheet_score INTEGER,
    ocr_score INTEGER,
    date_code_score INTEGER,
    total_score INTEGER,
    ocr_text TEXT,
    ocr_confidence REAL,
    datasheet_found INTEGER,
    datasheet_source TEXT,
    date_code TEXT,
    lot_code TEXT,
    issues TEXT,
    processing_time REAL,
    gpu_used INTEGER
);
```

### Configuration File

Application settings are stored in `config.json`:

```json
{
    "ocr": {
        "gpu": true,
        "languages": ["en"],
        "min_confidence": 0.5
    },
    "preprocessing": {
        "variants": ["trocr", "easyocr", "doctr", "mild"],
        "save_debug": false
    },
    "datasheet": {
        "sources": [
            "https://www.microchip.com",
            "https://www.ti.com",
            "https://www.infineon.com",
            "https://octopart.com",
            "https://www.alldatasheet.com"
        ],
        "timeout": 10,
        "cache_enabled": true
    },
    "scoring": {
        "marking_weight": 40,
        "datasheet_weight": 30,
        "ocr_weight": 20,
        "date_code_weight": 10,
        "threshold": 70
    },
    "gui": {
        "theme": "dark",
        "window_size": [1800, 1000],
        "show_debug": false
    }
}
```

---

## Project Structure

```
Ic_detection/
│
├── Application Files
│   ├── gui_classic_production.py          # Main GUI application
│   ├── final_production_authenticator.py  # Core authentication engine
│   ├── enhanced_preprocessing.py          # Image preprocessing module
│   ├── database_manager.py                # SQLite database operations
│   ├── marking_validator.py               # IC marking validation
│   └── working_web_scraper.py             # Datasheet scraping
│
├── Assets
│   ├── config.json                        # Configuration settings
│   ├── yolov8n.pt                         # YOLO model weights
│   ├── icon.ico                           # Windows icon
│   ├── icon.png                           # PNG icon
│   └── test_images/                       # Sample IC images
│
├── Build Tools
│   ├── build_installer.ps1               # Automated installer builder
│   ├── create_launcher_exe.py            # Launcher creation script
│   └── installer.iss                     # Inno Setup configuration
│
├── Documentation
│   ├── README.md                          # This file
│   ├── LICENSE.txt                        # MIT License
│   └── FIXES_APPLIED.md                   # Recent changes log
│
├── Dependencies
│   └── requirements.txt                   # Python packages list
│
└── Output
    └── installer_output/
        └── ICAuthenticator_Setup_v2.1.0.exe  # Windows installer
```

---

## Configuration

### Application Settings

Edit `config.json` to customize behavior:

#### OCR Configuration

```json
{
    "ocr": {
        "gpu": true,              // Enable GPU acceleration
        "languages": ["en"],      // OCR languages (English)
        "min_confidence": 0.5,    // Minimum OCR confidence threshold
        "detail_level": 1         // Text detection detail (0=low, 1=high)
    }
}
```

#### Preprocessing Configuration

```json
{
    "preprocessing": {
        "variants": [             // Preprocessing methods to use
            "trocr",              // TrOCR optimized
            "easyocr",            // EasyOCR optimized
            "doctr",              // docTR optimized
            "mild"                // Mild enhancement
        ],
        "save_debug": false,      // Save preprocessing images
        "debug_path": "debug_preprocessing/"
    }
}
```

#### Datasheet Configuration

```json
{
    "datasheet": {
        "sources": [              // Datasheet search sources
            "https://www.microchip.com",
            "https://www.ti.com",
            "https://www.infineon.com",
            "https://octopart.com",
            "https://www.alldatasheet.com"
        ],
        "timeout": 10,            // Request timeout (seconds)
        "cache_enabled": true,    // Enable datasheet caching
        "cache_path": "datasheet_cache/"
    }
}
```

#### Scoring Configuration

```json
{
    "scoring": {
        "marking_weight": 40,     // Marking validation points
        "datasheet_weight": 30,   // Datasheet verification points
        "ocr_weight": 20,         // OCR quality points
        "date_code_weight": 10,   // Date code presence points
        "threshold": 70,          // Authentication threshold
        "require_markings": true  // Require valid markings
    }
}
```

#### GUI Configuration

```json
{
    "gui": {
        "theme": "dark",          // Default theme (dark/light)
        "window_size": [1800, 1000],  // Window dimensions
        "show_debug": false,      // Show debug options by default
        "auto_save_results": true // Automatically save to database
    }
}
```

### Environment Variables

Optional environment variables for advanced configuration:

```bash
# CUDA device selection (for multi-GPU systems)
CUDA_VISIBLE_DEVICES=0

# Disable GPU (force CPU mode)
CUDA_VISIBLE_DEVICES=""

# EasyOCR model directory
EASYOCR_MODEL_DIR=./models

# Database location
IC_AUTH_DB_PATH=./ic_authentication.db

# Logging level
IC_AUTH_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

---

## Troubleshooting

### Common Issues

#### Issue: GPU Not Detected

**Symptoms:**
- Status shows "CPU Only"
- Processing is slow (4-8 seconds per image)
- GPU field shows red X

**Solutions:**

1. **Check CUDA Installation**
   ```bash
   # Verify CUDA is installed
   nvidia-smi
   
   # Should show GPU information and CUDA version
   ```

2. **Reinstall PyTorch with CUDA**
   ```bash
   pip uninstall torch torchvision
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Verify CUDA Version Compatibility**
   - CUDA 11.8 recommended
   - Download from: https://developer.nvidia.com/cuda-11-8-0-download-archive

4. **Check GPU Drivers**
   - Update to latest NVIDIA drivers
   - Download from: https://www.nvidia.com/Download/index.aspx

#### Issue: Low OCR Accuracy

**Symptoms:**
- Incorrect text extraction
- Low confidence scores
- Missing characters

**Solutions:**

1. **Improve Image Quality**
   - Use higher resolution camera
   - Ensure proper focus
   - Add more lighting
   - Avoid glare and reflections

2. **Adjust Image**
   - Ensure chip is parallel to camera
   - Fill frame with chip (not too zoomed out)
   - Clean chip surface before photographing

3. **Enable Debug Options**
   - Check "Show Preprocessing" in GUI
   - Review preprocessing variants
   - Identify which variant works best

4. **Manual Review**
   - Check Debug Images tab
   - Look at OCR bounding boxes
   - Verify text is actually visible in image

#### Issue: Datasheet Not Found

**Symptoms:**
- "Datasheet: Not Found" in results
- 0 points for datasheet verification
- No URL provided

**Solutions:**

1. **Check Internet Connection**
   ```bash
   # Test connectivity
   ping google.com
   ```

2. **Verify Part Number**
   - Ensure OCR extracted correct part number
   - Check for OCR errors (O vs 0, I vs 1, etc.)
   - Manually search part number online

3. **Try Alternative Sources**
   - Search directly on manufacturer website
   - Use Octopart.com
   - Check AllDatasheet.com

4. **Part May Be Obsolete**
   - Old ICs may not have online datasheets
   - Check manufacturer's legacy product database

#### Issue: Application Crashes on Startup

**Symptoms:**
- Application window doesn't appear
- Error dialog on launch
- Process exits immediately

**Solutions:**

1. **Check Python Version**
   ```bash
   python --version
   # Should be 3.11 or later
   ```

2. **Verify Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Check for Missing Files**
   - Ensure all application files are present
   - Verify config.json exists
   - Check yolov8n.pt model file exists

4. **Run from Command Line**
   ```bash
   python gui_classic_production.py
   # View error messages
   ```

5. **Check Logs**
   - Look for error messages in console
   - Check Windows Event Viewer
   - Review Python error traceback

#### Issue: Slow Processing

**Symptoms:**
- Processing takes > 10 seconds
- Application freezes during processing
- High CPU usage

**Solutions:**

1. **Enable GPU Acceleration** (see GPU Not Detected above)

2. **Reduce Image Size**
   - Resize images to 1024x1024 or smaller
   - Use JPG with reasonable compression

3. **Disable Debug Options**
   - Uncheck "Show Preprocessing"
   - Uncheck "Show Text Boxes"

4. **Close Other Applications**
   - Free up RAM and CPU
   - Close other GPU-intensive programs

#### Issue: Installer Won't Run

**Symptoms:**
- "Windows protected your PC" message
- Installer won't start
- Security warning

**Solutions:**

1. **Allow Unknown Publisher**
   - Click "More info"
   - Click "Run anyway"

2. **Run as Administrator**
   - Right-click installer
   - Select "Run as administrator"

3. **Check Antivirus**
   - Temporarily disable antivirus
   - Add exception for installer

4. **Verify Download**
   - Re-download installer
   - Check file size (should be 17.42 MB)
   - Verify from official source

### Debug Mode

Enable detailed logging for troubleshooting:

```python
# Add to beginning of gui_classic_production.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ic_auth_debug.log'
)
```

View log file:
```bash
Get-Content ic_auth_debug.log -Tail 50
```

### Getting Help

**Before asking for help, collect:**
1. Python version (`python --version`)
2. GPU information (`nvidia-smi` output)
3. Error messages (full traceback)
4. Sample image (if possible)
5. Operating system and version

**Support channels:**
- GitHub Issues: https://github.com/Ross0907/Ic_detection/issues
- Check existing issues for similar problems
- Provide detailed information when creating new issue

---

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 Ross

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

See [LICENSE.txt](LICENSE.txt) for full license text.

---

**Version:** 2.1.0  
**Last Updated:** January 2025  
**Status:** Production Ready  
**Repository:** https://github.com/Ross0907/Ic_detection
