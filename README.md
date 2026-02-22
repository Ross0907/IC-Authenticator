# IC Authenticator - v7.0.17

<div align="center">

![Version](https://img.shields.io/badge/version-7.0.17-blue.svg)
![Python](https://img.shields.io/badge/python-3.13.5-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![GPU](https://img.shields.io/badge/GPU-accelerated-orange.svg)

**A professional GPU-accelerated system for detecting counterfeit integrated circuits using intelligent OCR with auto-orientation, manufacturer marking validation, and datasheet verification.**

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
  - [GUI Interface](#gui-interface)
  - [Programmatic Use](#programmatic-use)
  - [Batch Processing](#batch-processing)
- [Authentication System](#-authentication-system)
- [Technical Details](#-technical-details)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Building the Installer](#-building-the-installer)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Research Foundation](#-research-foundation)
- [License](#-license)
- [Contributing](#-contributing)

---

## 🎯 Overview

This system analyzes IC (Integrated Circuit) chip images to determine authenticity by examining multiple factors including intelligent text extraction with automatic orientation detection, manufacturer markings, date codes, and datasheet verification. It employs GPU-accelerated OCR with multiple preprocessing methods and smart rotation detection to handle various IC marking types including laser-etched and engraved text.

### Key Capabilities

- **Intelligent OCR** - GPU-accelerated OCR with automatic orientation detection (0°, 90°, 180°, 270°) and 5+ preprocessing methods
- **Manufacturer Marking Validation** - Pattern-based verification using industry standards
- **Datasheet Verification** - Automatic lookup across 5+ trusted sources with PDF parsing and caching
- **Intelligent Counterfeit Detection** - Pattern recognition for misspellings, old date codes, and combined indicators
- **Comprehensive Scoring** - 100-point authentication system with detailed breakdown

## ✨ Features

### Intelligent OCR with Auto-Orientation
- **Automatic orientation detection** - Tests all 4 cardinal rotations (0°, 90°, 180°, 270°)
- **Smart rotation selection** - Chooses best orientation based on alphanumeric content
- **5+ preprocessing methods** with ensemble selection
- **Multi-scale enhancement** based on research papers (CLAHE, bilateral filtering, adaptive threshold)
- **GPU acceleration** - CUDA-enabled PyTorch and EasyOCR for 3-5x speed improvement
- **Automatic method selection** - Chooses best preprocessing variant per image

### Manufacturer Validation
- Pattern-based marking verification
- Date code validation (YYWW format)
- Lot code detection
- Manufacturer-specific format checking

### Datasheet Verification
- **PDF Caching** - Stores downloaded PDFs locally with proper file:// URI support
- **Smart URL Extraction** - Extracts PDF links from product pages automatically
- **PDF Parsing** - Downloads and extracts marking specifications from manufacturer PDFs
- Searches 10+ online sources:
  - **Manufacturer Sites**: Texas Instruments, Microchip, STMicroelectronics, NXP, Infineon, Analog Devices
  - **Distributors**: Digikey, Mouser, Octopart
  - **Databases**: AllDatasheet, DatasheetArchive
- Automatic part number extraction
- URL and source tracking
- Confidence scoring (high/medium/low)

### Intelligent Counterfeit Detection
- **Manufacturer Misspelling Detection** - Identifies common counterfeit indicators (ANEL, AMEL, ALMEL → ATMEL)
- **Old Date Code Detection** - Flags suspiciously old date codes (pre-2012 = 13+ years)
- **Smart Pattern Filtering** - Distinguishes real misspellings from OCR logo errors
- **WWYY/YYWW Format Recognition** - Correctly interprets ambiguous date codes
- **"2007" Pattern Detection** - Specific counterfeit indicator detection
- **Combined Indicator Analysis** - Escalates to CRITICAL when multiple suspicious patterns detected
- **Datasheet-Aware Verdicts** - More lenient when manufacturer datasheet verified
---

## 📋 Requirements

**Core Libraries:**
```
Python 3.13.5         - Programming language
PyQt5 5.15+           - GUI framework
PyTorch 2.0+          - Deep learning backend (with CUDA support)
EasyOCR 1.7+          - OCR engine
OpenCV 4.8+           - Image processing
NumPy 1.24+           - Numerical computing
Pillow 10.0+          - Image handling
tempfile              - Memory-optimized debug image storage (v7.0.17)
```

**Web Scraping:**
```
requests 2.31+        - HTTP library
beautifulsoup4 4.12+  - HTML parsing
lxml 4.9+             - XML/HTML parser
```

**Installation:**
```bash
pip install -r requirements.txt

# For GPU support (NVIDIA CUDA 11.8):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## 💻 Installation

#### Prerequisites

1. **NVIDIA GPU with CUDA support** (optional but recommended)
   ```
   Check GPU compatibility: https://developer.nvidia.com/cuda-gpus
   Install CUDA Toolkit 11.8: https://developer.nvidia.com/cuda-downloads
   ```
    note: python and other dependancies are installed by the installer automatically if not found.

#### Installation Steps

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/Ross0907/Ic_detection.git
   cd Ic_detection
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv .venv
   
   # Activate on Windows:
   .venv\Scripts\activate
   
   # Activate on Linux/Mac:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   # Install all dependencies
   pip install -r requirements.txt
   
   # For GPU support (NVIDIA CUDA 11.8):
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

4. **Run the application**
   ```bash
   python gui_classic_production.py
   ```

---

## 🚀 Quick Start

### GUI Application

1. Click **"Select IC Image"** and choose a clear photo of an IC chip
2. Click **"Authenticate IC"** to start analysis
3. View comprehensive results including:
---

## User Interface Guide

The IC Authenticator provides a comprehensive, professional interface with multiple tabs and visualization options. Below is a detailed walkthrough of each interface component.

### Main Interface - Analysis View

![Main Interface](README_imgs/image-1760146329471.png)

**Key Features:**
- **Image Preview Panel (Left)**: Displays the selected IC image with preview
- **Summary Tab**: Shows authentication verdict (LIKELY AUTHENTIC - 75%), confidence score, and key information
- **Part Number**: ATMEGA328P with manufacturer (Microchip) identification
- **Authentication Breakdown**: Shows counterfeit analysis and scoring details
- **Status Information**: Shows GPU detection, processing time, and memory usage (optimized in v7.0.17)

**How to Use:**
1. Click **"Select Image"** to choose an IC chip photo
2. The image appears in the preview panel
3. Check "Show Preprocessing" and "Show Text Boxes" for detailed visualization
4. Click **"Authenticate IC"** to start the analysis
5. Processing time typically ranges from 4-9 seconds depending on image complexity

---

### Raw Data Tab

![Raw Data](README_imgs/image-1760146396007.png)

**Purpose**: Provides complete JSON output for developers and advanced users

**Contains:**
- Full OCR extraction results with confidence scores for each text detection
- Bounding box coordinates for all detected text regions
- Complete authentication metadata including datasheet URLs and verification status
- Part number, manufacturer, and date code extraction details in JSON format

**Use Cases:**
- Debugging OCR accuracy issues
- Integrating with other systems via API
- Analyzing confidence scores across different preprocessing methods
- Exporting results for batch processing workflows

---

### Summary Tab - Authentication Results

![Summary Tab](README_imgs/image-1760146329471.png)

**Purpose**: Displays the final authentication verdict with comprehensive scoring

**Key Information:**
- **Verdict Banner**: Large green (✓ LIKELY AUTHENTIC) banner with confidence percentage
- **Overall Confidence**: Percentage score (0-100%) indicating authentication certainty
- **Part Number**: Extracted IC part number (e.g., ATMEGA328P)
- **Manufacturer**: Identified manufacturer (e.g., Microchip)
- **Date Code**: Manufacturing date code when present
- **Confidence Score**: Overall authentication confidence (e.g., 75%)
- **OCR Confidence**: Quality score for text extraction (e.g., 36.9%)
- **Datasheet Status**: Found with verified manufacturer source

**Scoring Breakdown:**
The system uses a 100-point scale with penalties for issues:
- Valid manufacturer markings (+40 points)
- Official datasheet found (+30 points)
- High OCR quality (+13 points)
- Valid date code (+10 bonus points)

---

### Detailed Analysis Tab

![Detailed Analysis](README_imgs/image-1760146347295.png)

**Purpose**: Shows in-depth validation and verification details

**Sections:**

1. **Marking Validation**
   - Manufacturer identification and validation status (e.g., Microchip)
   - Validation Status: ✗ FAILED when issues detected
   - Identified marking issues with explanations (e.g., "No issues found - Mostly are valid")
2. **OCR Extraction Details**
   - Complete extracted text from all preprocessing variants
   - Full Text: Shows all detected text (e.g., "ATMEL AT MEGA328P 20AU 0723")
   - Overall confidence percentage (e.g., 36.9%)
   - Individual detections table with confidence scores per text element

---
### Datasheet Verification Visualization

![Datashhet](README_imgs/image-1760146370334.png)
1. **Datasheet Information**
   - Datasheet verification status
   - Source: Local Cache or manufacturer website
   - Manufacturer URL: Direct link to official datasheet PDF
   - Local PDF path showing cached location

---

### Debug Images Tab - Text Detection Visualization

![Debug Images](README_imgs/image-1760146387684.png)

**Purpose**: Visualizes the OCR text detection process with bounding boxes
**Use Cases:**
- Verifying that all text on the IC was detected
- Diagnosing why certain markings weren't extracted
- Understanding OCR performance on different text styles
- Identifying overlapping or missed text regions

**The Preprocessing Variants:**

1. **CLAHE Enhanced**: Contrast Limited Adaptive Histogram Equalization for better contrast
2. **Bilateral Filter**: Noise reduction while preserving edges
3. **Adaptive Threshold**: High-contrast binary image for clear text separation

**Why Multiple Variants?**
- Different IC manufacturers use different marking techniques (laser etching, printing, engraving)
- Some text is easier to read after contrast enhancement, others after different filtering
- The system automatically selects the best result from all variants
- This ensemble approach dramatically improves accuracy (typically 85-95% success rate)

**Technical Details:**
- Each variant uses different preprocessing algorithms (CLAHE, bilateral filtering, adaptive thresholding)
- GPU acceleration processes all variants simultaneously in ~5 seconds
- The variant with highest confidence score is selected for final authentication

---



### Batch Processing Results

![Batch Processing](README_imgs/image-1760146476545.png)

**Purpose**: Process multiple IC images simultaneously and view aggregate results

**Workflow:**
1. Click **"Batch Process"** button
2. Select multiple IC images (Ctrl+Click or Shift+Click)
3. System processes all images automatically (memory-optimized in v7.0.17)
4. View aggregate results in the summary table
5. Click "View" on any row to see detailed analysis with counterfeit reasons
6. Export results using **"Save Report"** or **"Export All Debug Data"**

---

### Batch Result Details - Individual IC

![Individual Batch Result - Summary](README_imgs/image-1760146532332.png)

**Purpose**: Detailed view of a single IC from batch processing (LM358N example - 75% confidence)

**Navigation:**
- **Summary**: Quick overview (shown above)
- **Details**: Full marking validation and datasheet info
- **Debug Images**: Text detection visualization
- **Raw Data**: Complete JSON output

---

### Detailed OCR Analysis

![OCR Details](README_imgs/image-1760146570499.png)

**Purpose**: Shows exactly how the OCR system extracted and interpreted text (Details tab from batch result)

**Information Displayed:**
- **OCR Confidence**: Overall quality score (e.g., 27.4%)
- **Full Text**: Complete extracted text (e.g., "Fed4sJp LM 358N")
- **Processing Details**:
  - Processing time (e.g., 0.00s)
  - GPU acceleration status
  - Timestamp of analysis

**Understanding OCR Confidence:**
- **90-100%**: Excellent - Very clear text, high reliability
- **70-89%**: Good - Minor uncertainties, generally reliable
- **50-69%**: Fair - Some ambiguous characters, verify manually
- **Below 50%**: Poor - Low-quality image or difficult text, results may be inaccurate

---

### Debug Preprocessing Visualization

![Debug Preprocessing](README_imgs/image-1760146558557.png)

**Purpose**: See the actual preprocessing results that fed into the OCR engine - showing batch processing completion

- Monitor batch processing completion
- Access datasheets immediately after authentication
- Review processed images and their results
- Export debug data or save reports for documentation

---

### Datasheet Viewer

![Datasheet Viewer](README_imgs/image-1760146489439.png)

**Purpose**: Display manufacturer datasheets directly in the application

**Features:**
- **Embedded PDF Viewer**: Displays datasheet pages with zoom controls (100%, + -)
- **Page Navigation**: Shows current page (Page 1) and total pages (e.g., Total Pages: 651)
- **6-Level Error Handling**: Prevents crashes from corrupted PDFs (v3.0.6+)
- **200-Page Limit**: Prevents system overload from massive documents
- **Fallback Mechanisms**: System viewer → web browser if embedded fails
- **Caching System**: Downloads stored locally for offline access

**How It Works:**
1. System searches known URLs and manufacturer websites
2. Downloads PDF and caches in `datasheet_cache/`
3. Renders in embedded viewer with proper file:// URI support (shown: ATMEGA328P datasheet)
4. Automatic fallback if rendering fails

---

### Marking Validation - Counterfeit Detection Example

![Counterfeit Detection](README_imgs/image-1760146520936.png)

**Purpose**: Demonstrates how the system detects counterfeit indicators


---

## 📘 Usage

### GUI Interface

**Launch GUI Launcher** (choose between Classic or Modern interface):
```bash
python launch_gui.py
```

**Or launch directly:**
```bash
python gui_classic_production.py   # Classic tabbed interface
python gui_modern_production.py    # Modern card-based interface
```

#### Classic Interface Features
- Three-tab layout (Summary, Detailed Analysis, Raw Data)
- Traditional professional design
- Organized information display

#### Modern Interface Features
- Card-based design with metrics
- Three-column layout
- Contemporary aesthetics

#### Both Interfaces Include
- Dark/Light mode toggle
- Real-time processing with progress tracking
- Comprehensive results display
- Detailed marking validation
- Datasheet source and URL
- OCR extraction details
- Complete confidence score breakdown

### Programmatic Use

```python
from final_production_authenticator import FinalProductionAuthenticator

# Initialize authenticator
authenticator = FinalProductionAuthenticator()

# Authenticate an image
result = authenticator.authenticate("path/to/ic_image.jpg")

# Access results
print(f"Authentic: {result['is_authentic']}")
print(f"Confidence: {result['confidence']}%")
print(f"Part Number: {result['part_number']}")
print(f"Manufacturer: {result['manufacturer']}")
```

#### Accessing Detailed Information

```python
result = authenticator.authenticate("image.jpg")

# Marking validation details
marking = result.get('marking_validation', {})
print(f"Date Code: {marking.get('date_code')}")
print(f"Lot Code: {marking.get('lot_code')}")
print(f"Marking Issues: {marking.get('issues', [])}")

# Datasheet information
datasheet = result.get('datasheet', {})
print(f"Datasheet Found: {datasheet.get('found')}")
print(f"Source: {datasheet.get('source')}")
print(f"URL: {datasheet.get('url')}")

# OCR details
ocr = result.get('ocr_details', {})
print(f"OCR Confidence: {ocr.get('confidence')}%")
print(f"Preprocessing Method: {ocr.get('method')}")
print(f"Extracted Text: {ocr.get('text')}")

# Score breakdown
scores = result.get('score_breakdown', {})
print(f"Marking Score: {scores.get('marking_score', 0)}/40")
print(f"Datasheet Score: {scores.get('datasheet_score', 0)}/30")
print(f"OCR Score: {scores.get('ocr_score', 0)}/20")
print(f"Date Code Score: {scores.get('date_code_score', 0)}/10")
```

### Batch Processing

```python
import os
from final_production_authenticator import FinalProductionAuthenticator

authenticator = FinalProductionAuthenticator()

# Process all images in a directory
image_dir = "test_images"
results = []

for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.jpg', '.png', '.bmp')):
        image_path = os.path.join(image_dir, filename)
        result = authenticator.authenticate(image_path)
        results.append({
            'filename': filename,
            'authentic': result['is_authentic'],
            'confidence': result['confidence'],
            'part_number': result['part_number']
        })

# Print summary
for r in results:
    status = "✓" if r['authentic'] else "✗"
    print(f"{status} {r['filename']}: {r['confidence']}% - {r['part_number']}")
```

### Command Line Testing

```bash
python test_comprehensive.py
```

---

## 🔐 Authentication System

### Scoring System

The authentication uses a **100-point scoring system** divided into four components:

```
┌──────────────────────────────────────────────────────────────┐
│                 Authentication Scoring                       │
├─────────────────────────┬────────┬───────────────────────────┤
│ Component               │ Points │ Description               │
├─────────────────────────┼────────┼───────────────────────────┤
│ Marking Validation      │   40   │ Most critical component   │
│ • Date Code Format      │   15   │   YYWW pattern (2425)     │
│ • Lot Code Presence     │   15   │   Manufacturer lot code   │
│ • Marking Completeness  │   10   │   All expected fields     │
├─────────────────────────┼────────┼───────────────────────────┤
│ Datasheet Verification  │   30   │ Official documentation    │
│ • Found on Official Site│   30   │   Trusted source          │
│ • Not Found             │    0   │   Suspicious              │
├─────────────────────────┼────────┼───────────────────────────┤
│ OCR Quality             │   20   │ Text extraction quality   │
│ • High Confidence (>80%)│   20   │   Clear, readable text    │
│ • Medium (60-80%)       │   15   │   Some uncertainty        │
│ • Low (<60%)            │   10   │   Poor image quality      │
├─────────────────────────┼────────┼───────────────────────────┤
│ Date Code Presence      │   10   │ Manufacturing date found  │
│ • Valid Date Code       │   10   │   Proper format           │
│ • No Date Code          │    0   │   Missing or invalid      │
├─────────────────────────┼────────┼───────────────────────────┤
│ TOTAL                   │  100   │                           │
└──────────────────────────────────────────────────────────────┘

Authentication Decision:
• Score ≥ 70 AND valid markings → AUTHENTIC
• Score < 70 OR invalid markings → COUNTERFEIT
```

### Processing Pipeline

#### Stage 1: Intelligent Orientation Detection

```
Input Image
    │
    └─→ Try All 4 Cardinal Rotations
        ├─ 0° (original)
        ├─ 90° clockwise
        ├─ 180° 
        └─ 270° clockwise
        
        For each rotation:
          ├─ Apply CLAHE enhancement
          ├─ Run quick OCR test
          └─ Score alphanumeric content
        
        Select best orientation based on:
          ├─ Number of alphanumeric characters
          ├─ Ratio of alphanumeric to total
          └─ Overall quality score
```

#### Stage 2: Image Preprocessing

```
Best Oriented Image
    │
    ├─→ Variant 1: CLAHE Enhanced
    │   ├─ Normalize to [0, 255]
    │   ├─ CLAHE (clipLimit=3.0)
    │   └─ Contrast enhancement
    │
    ├─→ Variant 2: Bilateral Filtered
    │   ├─ Bilateral filter (edge-preserving)
    │   ├─ Noise reduction
    │   └─ Sharpness preservation
    │
    ├─→ Variant 3: Adaptive Threshold
    │   ├─ Adaptive thresholding
    │   ├─ Binarization
    │   └─ Text clarity optimization
    │
    ├─→ Variant 4: Unsharp Masked
    │   ├─ Gaussian blur
    │   ├─ Unsharp masking
    │   └─ Edge enhancement
    │
    └─→ Variant 5: OTSU Threshold
        ├─ Otsu's binarization
        └─ Automatic threshold selection
```

#### Stage 3: OCR Processing & Best Result Selection

```
5 Preprocessed Variants
    │
    ├─→ EasyOCR (GPU-Accelerated)
    │   ├─ Text Detection
    │   ├─ Text Recognition
    │   └─ Confidence Scoring
    │
    └─→ Select Best Result
        ├─ Quality Score = OCR Confidence + Text Quality
        ├─ Text quality considers:
        │   • Length (5-60 chars preferred)
        │   • Alphanumeric content
        │   • Special character ratio (<15%)
        │   • Known IC patterns
        └─ Select highest scoring variant
```

#### Stage 4: Parallel Analysis

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
    │   ├─ Search multiple sources
    │   └─ Calculate datasheet score
    │
    └─→ OCR Quality Check (20 pts)
        ├─ Evaluate confidence
        ├─ Check text characteristics
        └─ Calculate OCR score
```

#### Stage 5: Decision Engine

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
    └─→ Generate Results
        ├─ Verdict
        ├─ Confidence percentage
        ├─ Detailed breakdown
        ├─ Issues found
        └─ Recommendations
```

---

## 🔬 Technical Details

### Preprocessing Methods

This system implements **research-based techniques** from peer-reviewed papers with **automatic orientation detection**:

#### Step 0: Automatic Orientation Detection (NEW in v3.0.6)
**Purpose:** Ensure optimal text orientation before processing

**Process:**
- Tests all 4 cardinal rotations (0°, 90°, 180°, 270°)
- Applies CLAHE enhancement to each rotation
- Runs quick OCR test to detect alphanumeric characters
- Scores each rotation based on:
  - Number of alphanumeric characters found
  - Ratio of alphanumeric to total characters
  - Overall quality indicators
- Selects best orientation automatically

**Benefits:**
- Handles rotated IC images automatically
- No manual rotation needed
- Improves OCR accuracy for all orientations

#### 1. CLAHE Enhanced Preprocessing
**Purpose:** Enhance contrast for low-contrast markings

**Research:** Harrison et al. - Automated Laser Marking Analysis

**Steps:**
- Contrast Limited Adaptive Histogram Equalization (clipLimit=3.0)
- Tiled grid-based enhancement (8x8)
- Preserves local details while enhancing overall contrast

**Best For:** Laser-etched text, engraved markings, low-contrast ICs

#### 2. Bilateral Filtered Preprocessing
**Purpose:** Reduce noise while preserving edges

**Research:** Paper 3 - Morphological operations for features

**Steps:**
- Bilateral filter (preserves edges while reducing noise)
- Edge-aware smoothing
- Noise reduction without blurring text

**Best For:** Noisy images, poor lighting, grainy photos

#### 3. Adaptive Threshold Preprocessing
**Purpose:** Create high-contrast binary images

**Steps:**
- Adaptive threshold with Gaussian method
- Block-based thresholding
- Automatic brightness adjustment

**Best For:** Printed text, stamp markings, high-contrast ICs

#### 4. Unsharp Masked Preprocessing
**Purpose:** Enhance edge sharpness

**Steps:**
- Gaussian blur (kernel 5x5)
- Unsharp masking with weighted addition
- Edge enhancement

**Best For:** Blurry images, slightly out-of-focus photos

#### 5. OTSU Threshold Preprocessing
**Purpose:** Automatic optimal binarization

**Steps:**
- Otsu's method for automatic threshold calculation
- Optimal separation of foreground/background
- Binarization

**Best For:** Images with bimodal histograms, clear separation

### OCR Ensemble Selection

The system processes the image with **automatic orientation detection** and **5 preprocessing variants**, then selects the best result using:

```
Step 1: Orientation Detection
  - Test 4 rotations (0°, 90°, 180°, 270°)
  - Quick OCR on each rotation
  - Score alphanumeric content
  - Select best orientation

Step 2: Preprocessing Variants
  - Apply 5 different enhancement methods
  - CLAHE, Bilateral, Adaptive, Unsharp, OTSU
  - Early termination if high-confidence result found

Step 3: Best Result Selection
  Quality Score = OCR Confidence + Text Quality

Where Text Quality considers:
  • Text length (optimal: 5-60 characters)
  • Alphanumeric content (both letters and numbers preferred)
  • Special character ratio (< 15% preferred)
  • Pattern matching (known IC patterns score higher)
```

### GPU Acceleration

#### Performance Comparison

```
┌────────────────────────────────────────────────────────────┐
│              Processing Time Comparison                    │
├────────────────────────┬──────────────┬────────────────────┤
│ Hardware               │ Avg Time     │ Speedup vs CPU     │
├────────────────────────┼──────────────┼────────────────────┤
│ CPU (Intel i7-12700)   │ 4.5-8.0s     │ 1.0x (baseline)    │
│ GPU (RTX 3060)         │ 1.2-2.5s     │ 3.0-3.8x faster    │
│ GPU (RTX 4060)         │ 0.8-2.0s     │ 3.5-5.6x faster    │
│ GPU (RTX 4090)         │ 0.5-1.2s     │ 5.0-9.0x faster    │
└────────────────────────────────────────────────────────────┘
```

---

## 🏗️ System Architecture

### High-Level Architecture

 ```
       ┌─────────────────────────────────────────────┐
       │              GUI Layer (PyQt5)              │
       │  ┌───────────┐  ┌──────────┐  ┌──────────┐  │
       │  │  Summary  │  │ Detailed │  │ Raw Data │  │
       │  │   Tab     │  │ Analysis │  │   Tab    │  │
       │  └───────────┘  └──────────┘  └──────────┘  │
       └───────────────────────┬─────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────┐
│             Authentication Engine (Core Logic)            │
│        ┌─────────────────────────────────────────┐        │
│        │ Step 1: Automatic Orientation Detection │        │
│        │   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │        │
│        │   │  0°  │ │  90° │ │ 180° │ │ 270° │   │        │
│        │   └──────┘ └──────┘ └──────┘ └──────┘   │        │
│        └────────────────────┬────────────────────┘        │
│                             │                             │
│  ┌──────────────────────────▼──────────────────────────┐  │
│  │        Step 2: Enhanced Preprocessing Module        │  │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐  │  │
│  │  │ CLAHE │ │ Bilat.│ │ Adapt.│ │Unsharp│ │  OTSU │  │  │
│  │  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘  │  │
│  └───────────────────────────┬─────────────────────────┘  │
│                              │                            │
│     ┌────────────────────────▼──────────────────────┐     │
│     │     Step 3: GPU-Accelerated OCR (EasyOCR)     │     │
│     └────────────────────────┬──────────────────────┘     │
│                              │                            │
│      ┌───────────────────────▼─────────────────────┐      │
│      │      Step 4: Part Number Identification     │      │
│      └───────────────────────┬─────────────────────┘      │
│                              │                            │
│            ┌─────────────────▼───────────────┐            │
│            │   Step 5: Parallel Processing   │            │
│            │  ┌────────────┐  ┌───────────┐  │            │
│            │  │  Marking   │  │ Datasheet │  │            │
│            │  │ Validation │  │  Scraper  │  │            │
│            │  └────────────┘  └───────────┘  │            │
│            └────────────────┬────────────────┘            │
│                             │                             │
│     ┌───────────────────────▼───────────────────────┐     │
│     │  Step 6: Scoring & Decision Engine (100-point)│     │
│     └───────────────────────┬───────────────────────┘     │
└─────────────────────────────┼─────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                  Database Storage (SQLite)                  │
└─────────────────────────────────────────────────────────────┘
```
---

## 📁 Project Structure

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
│   ├── icon.ico                           # Windows icon
│   ├── icon.png                           # PNG icon
│   └── test_images/                       # Sample IC images
│       ├── ADC0831_0-300x300.png
│       ├── MC33774A-TOP.png
│       ├── sn74hc595n-shift-register...jpg
│       └── ...
│
├── Build Tools
│   ├── build_installer.ps1               # Automated installer builder
│   ├── create_launcher_exe.py            # Launcher creation script
│   └── installer.iss                     # Inno Setup configuration
│
├── Documentation
│   ├── README.md                          # This file
│   └── LICENSE.txt                        # MIT License
│
├── Dependencies
│   └── requirements_production.txt        # Python packages list
│
└── Output
    └── installer_output/
        └── ICAuthenticator_Setup_v3.0.exe  # Windows installer
```

---

## ⚙️ Configuration

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
        "variants": [
            "trocr",
            "easyocr",
            "doctr",
            "mild"
        ],
        "save_debug": false,
        "debug_path": "debug_preprocessing/"
    }
}
```

#### Datasheet Configuration
```json
{
    "datasheet": {
        "sources": [
            "https://www.microchip.com",
            "https://www.ti.com",
            "https://www.infineon.com",
            "https://octopart.com",
            "https://www.alldatasheet.com"
        ],
        "timeout": 10,
        "cache_enabled": true,
        "cache_path": "datasheet_cache/"
    }
}
```

#### Scoring Configuration
```json
{
    "scoring": {
        "marking_weight": 40,
        "datasheet_weight": 30,
        "ocr_weight": 20,
        "date_code_weight": 10,
        "threshold": 70,
        "require_markings": true
    }
}
```

#### GUI Configuration
```json
{
    "gui": {
        "theme": "dark",
        "window_size": [1800, 1000],
        "show_debug": false,
        "auto_save_results": true
    }
}
```

---

## 🔨 Building the Installer

### Prerequisites for Building

1. **Python 3.11+** with all dependencies installed
2. **PyInstaller** for creating the executable
   ```bash
   pip install pyinstaller
   ```
3. **Inno Setup 6** for creating the installer
   ```
   Download from: https://jrsoftware.org/isdl.php
   Install to default location: C:\Program Files (x86)\Inno Setup 6\
   ```

### Build Process

#### Automated Build (Recommended)

```powershell
# Run the build script
.\build_installer.ps1
```

**What the script does:**
1. Checks prerequisites (Python, PyInstaller, Inno Setup)
2. Cleans previous builds
3. Creates launcher executable (`ICAuthenticator.exe`)
4. Builds installer with Inno Setup
5. Packages all application files
6. Creates uninstaller
7. Verifies output

**Output:**
```
installer_output/ICAuthenticator_Setup_v3.0.exe (17.42 MB)
```

#### Manual Build Steps

If you prefer to build manually:

1. **Create the launcher executable**
   ```powershell
   python create_launcher_exe.py
   ```
   This creates `ICAuthenticator.exe` in the current directory.

2. **Build the installer**
   ```powershell
   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```
   This creates the installer in `installer_output/`

### Build Configuration

The build process is configured through three files:

- **`create_launcher_exe.py`** - Defines launcher executable creation
- **`installer.iss`** - Inno Setup configuration
- **`build_installer.ps1`** - Orchestrates the build process

---

## 📈 Performance

### Memory Performance (v7.0.17)

| Metric | Before v7.0.17 | After v7.0.17 | Improvement |
|--------|----------------|---------------|-------------|
| **LT1013 Image Memory** | 3,072 MB | 15 MB | **99.5% reduction** |
| **Average Image Memory** | 150-200 MB | 10-20 MB | **90% reduction** |
| **System Responsiveness** | Freezes after 2-3 min | Indefinite stability | **100% fix** |
| **UI Responsiveness** | Frequent freezing | Always responsive | **100% fix** |

### Processing Speed

| Operation | Time (GPU) | Time (CPU) |
|-----------|------------|------------|
| Image Loading | 0.1s | 0.1s |
| Preprocessing | 0.3s | 0.5s |
| OCR Extraction | 2-5s | 20-60s |
| Authentication | 0.2s | 0.2s |
| **Total** | **2.6-5.6s** | **20.8-60.8s** |

**GPU Speedup:** 3-10x faster than CPU-only processing

### Test Results

- **Average OCR Confidence:** 83.2%
- **Authentication Accuracy:** 83.3% (5/6 test images)
- **Processing Time:** 0.75-4.66s per image (with GPU)
- **GPU Speedup:** ~3-5x faster than CPU
- **Memory Usage (v7.0.17):** 
  - Idle: 80-100 MB
  - Processing: 100-180 MB (stable)
  - After 1 hour: 150-200 MB (periodic cleanup prevents bloat)

### Image Quality Requirements

```
┌────────────────────────────────────────────────────────────┐
│              Image Quality Guidelines                      │
├────────────────────────┬───────────────────────────────────┤
│ Property               │ Recommended                       │
├────────────────────────┼───────────────────────────────────┤
│ Resolution             │ 1000x1000 pixels minimum          │
│ Format                 │ JPG, PNG (lossless preferred)     │
│ Lighting               │ Diffuse, even illumination        │
│ Focus                  │ Sharp, no motion blur             │
│ Angle                  │ Perpendicular to chip surface     │
│ Background             │ Contrasting, solid color          │
│ Glare/Reflections      │ None or minimal                   │
└────────────────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: GPU Not Detected

**Symptoms:**
- Status shows "CPU Only"
- Processing is slow (4-8 seconds per image)

**Solutions:**
1. Check CUDA installation: `nvidia-smi`
2. Reinstall PyTorch with CUDA:
   ```bash
   pip uninstall torch torchvision
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
3. Update NVIDIA drivers from https://www.nvidia.com/Download/index.aspx

#### Issue: Low OCR Accuracy

**Solutions:**
1. Improve image quality (higher resolution, better lighting)
2. Ensure chip is parallel to camera
3. Clean chip surface before photographing
4. Enable debug options to review preprocessing variants

#### Issue: Datasheet Not Found

**Solutions:**
1. Check internet connection
2. Verify OCR extracted correct part number
3. Part may be obsolete - check manufacturer's legacy database

#### Issue: Application Crashes on Startup

**Solutions:**
1. Verify Python version: `python --version` (should be 3.11+)
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Check for missing files (config.json, icon files)
4. Run from command line to view error messages

#### Issue: Slow Processing

**Solutions:**
1. Enable GPU acceleration (see GPU Not Detected above)
2. Reduce image size to 1024x1024 or smaller
3. Disable debug options
4. Close other GPU-intensive applications

#### Issue: High Memory Usage or System Becomes Unresponsive (FIXED in v7.0.17)

**Symptoms:**
- RAM usage over 2GB after processing a few images
- System becomes "hitchey and laggy" after 2-3 minutes
- Application freezes when processing specific images

**Solution:**
- **Update to v7.0.17** - Critical memory leak fixed
- Memory usage reduced from 3GB+ to 15MB per image (99.5% reduction)
- If still experiencing issues, restart the application periodically

**Legacy workaround (if using older version):**
1. Restart application every 10-15 images
2. Process images in smaller batches
3. Close datasheet viewer after use

### Debug Mode

Enable detailed logging:

```python
# Add to beginning of gui_classic_production.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ic_auth_debug.log'
)
```

View log:
```powershell
Get-Content ic_auth_debug.log -Tail 50
```

---

## 📖 Research Foundation

This system implements techniques from peer-reviewed research papers:

1. **AutoDetect** - Novel Autoencoding Architecture for Counterfeit IC Detection
   - *Journal of Hardware and Systems Security, 2024*

2. **IC SynthLogo** - Synthetic Logo Dataset for Counterfeit Detection
   - *PCB Logo Classification*

3. **Harrison et al.** - Automated Laser Marking Analysis
   - *IEEE: Detection of Counterfeit Electronic Components*

4. **Deep Learning AOI** - Component Marks Detection System
   - *Analysis of Image Preprocessing and Binarization Methods for OCR-Based IC Detection*

5. **PCB Logo Classification** - Data Augmentation for Assurance
   - *Deep Learning-based AOI System for Detecting Component Marks*

All research papers are referenced in the implementation and available for review.

---

## 📜 License

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

See [LICENSE.txt](LICENSE.txt) for full details.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Test thoroughly with various IC images
4. Commit your changes (`git commit -m 'Add AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Add docstrings to all functions
- Test with both CPU and GPU configurations
- Update documentation for new features
- Include sample images if adding new IC type support

---

## 📧 Support

For issues or questions:

- **GitHub Issues:** [github.com/Ross0907/Ic_detection/issues](https://github.com/Ross0907/Ic_detection/issues)
- Check existing issues for similar problems
- Provide detailed information when creating new issues:
  - Python version
  - GPU information (if applicable)
  - Error messages (full traceback)
  - Sample image (if possible)
  - Operating system and version

---

## 📜 Version History

### v7.0.17 (January 2025) - CRITICAL MEMORY FIX ⚠️
- **Fixed critical memory leak**: 3GB+ → 15MB per image (99.5% reduction)
- Disk-based debug image storage using tempfile module
- Smart signal management (file paths only, not numpy arrays)
- Dynamic table column sizing (no text cutoff)
- Counterfeit reasons in batch results
- Periodic memory cleanup (QTimer every 30s)
- UI responsiveness improvements (processEvents integration)
- Indefinite stability (no more freezing after 2-3 minutes)

### v7.0.16 (January 2025)
- Added dynamic table columns
- Counterfeit reasons in batch processing
- Memory cleanup timer implementation
- LT1013 unresponsiveness fix attempt

### v3.0.6 (December 2024)
- PDF viewer crash prevention (6-level error handling)
- CY8C29666 datasheet fix
- Google search integration for datasheets
- Marking diagram validation
- 200-page PDF limit to prevent crashes

### v3.0.5 (December 2024)
- YOLO removal for simplified architecture
- Auto-orientation detection (0°, 90°, 180°, 270°)
- Smart rotation selection
- Faster processing with reduced memory footprint
- PDF datasheet support with proper file:// URIs

---

## 🎯 Future Enhancements

- [ ] **Linux/Mac Support** - Cross-platform compatibility
- [ ] **Parallel Batch Processing** - Multi-threading for 100+ images
- [ ] **Custom OCR Training** - Improved accuracy for specific manufacturers
- [ ] **Datasheet Parser** - Automatic spec extraction
- [ ] **API Mode** - REST API for system integration
- [ ] Web-based interface
- [ ] Mobile app support (iOS/Android)
- [ ] Additional IC manufacturer patterns
- [ ] Database of known counterfeit patterns
- [ ] Automated reporting system
- [ ] Integration with ERP systems
- [ ] Multi-language support
- [ ] Cloud-based processing option
- [ ] Real-time camera integration

---

<div align="center">

**Version 7.0.17** | **Last Updated:** January 2025

</div>

<!-- ```
       ┌─────────────────────────────────────────────┐
       │              GUI Layer (PyQt5)              │
       │  ┌───────────┐  ┌──────────┐  ┌──────────┐  │
       │  │  Summary  │  │ Detailed │  │ Raw Data │  │
       │  │   Tab     │  │ Analysis │  │   Tab    │  │
       │  └───────────┘  └──────────┘  └──────────┘  │
       └───────────────────────┬─────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────┐
│             Authentication Engine (Core Logic)            │
│        ┌─────────────────────────────────────────┐        │
│        │ Step 1: Automatic Orientation Detection │        │
│        │   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐   │        │
│        │   │  0°  │ │  90° │ │ 180° │ │ 270° │   │        │
│        │   └──────┘ └──────┘ └──────┘ └──────┘   │        │
│        └────────────────────┬────────────────────┘        │
│                             │                             │
│  ┌──────────────────────────▼──────────────────────────┐  │
│  │        Step 2: Enhanced Preprocessing Module        │  │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐  │  │
│  │  │ CLAHE │ │ Bilat.│ │ Adapt.│ │Unsharp│ │  OTSU │  │  │
│  │  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘  │  │
│  └───────────────────────────┬─────────────────────────┘  │
│                              │                            │
│     ┌────────────────────────▼──────────────────────┐     │
│     │     Step 3: GPU-Accelerated OCR (EasyOCR)     │     │
│     └────────────────────────┬──────────────────────┘     │
│                              │                            │
│      ┌───────────────────────▼─────────────────────┐      │
│      │      Step 4: Part Number Identification     │      │
│      └───────────────────────┬─────────────────────┘      │
│                              │                            │
│            ┌─────────────────▼───────────────┐            │
│            │   Step 5: Parallel Processing   │            │
│            │  ┌────────────┐  ┌───────────┐  │            │
│            │  │  Marking   │  │ Datasheet │  │            │
│            │  │ Validation │  │  Scraper  │  │            │
│            │  └────────────┘  └───────────┘  │            │
│            └────────────────┬────────────────┘            │
│                             │                             │
│     ┌───────────────────────▼───────────────────────┐     │
│     │  Step 6: Scoring & Decision Engine (100-point)│     │
│     └───────────────────────┬───────────────────────┘     │
└─────────────────────────────┼─────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                  Database Storage (SQLite)                  │
└─────────────────────────────────────────────────────────────┘
``` -->
