# System Architecture - IC Authentication System

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                     (ic_authenticator.py)                        │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Control   │  │    Image     │  │    Debug     │           │
│  │   Panel     │  │   Display    │  │   Layers     │           │
│  └─────────────┘  └──────────────┘  └──────────────┘           │
│  ┌─────────────┐  ┌──────────────┐                              │
│  │   Results   │  │ Verification │                              │
│  │   Display   │  │    Panel     │                              │
│  └─────────────┘  └──────────────┘                              │
└────────────────┬──────────────────────────────┬─────────────────┘
                 │                              │
        ┌────────▼────────┐            ┌────────▼────────┐
        │  Processing     │            │   Database      │
        │    Thread       │            │   Manager       │
        └────────┬────────┘            └─────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│ Image  │  │  OCR   │  │  Web   │
│Process │  │ Engine │  │Scraper │
└───┬────┘  └───┬────┘  └───┬────┘
    │           │           │
    └───────────┼───────────┘
                │
        ┌───────▼────────┐
        │  Verification  │
        │     Engine     │
        └────────────────┘
```

## Component Details

### 1. User Interface Layer (PyQt5)
```
┌─────────────────────────────────────────┐
│         Main Window (QMainWindow)        │
├─────────────────────────────────────────┤
│                                          │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │ Control Panel│  │  Display Area   │  │
│  ├──────────────┤  ├─────────────────┤  │
│  │ • Load Image │  │ Tab Widget:     │  │
│  │ • OCR Select │  │  - Image        │  │
│  │ • Debug Opts │  │  - Debug        │  │
│  │ • Analyze    │  │  - Results      │  │
│  │ • Progress   │  │  - Verification │  │
│  │ • Batch      │  │                 │  │
│  │ • History    │  │                 │  │
│  │ • Export     │  │                 │  │
│  └──────────────┘  └─────────────────┘  │
│                                          │
└─────────────────────────────────────────┘
```

### 2. Image Processing Pipeline
```
Input Image
    │
    ▼
┌─────────────────┐
│   Load Image    │
│  (cv2.imread)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Grayscale     │
│  Conversion     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Denoising     │
│ (Non-local      │
│   Means)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Enhancement   │
│    (CLAHE)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Edge Detection  │
│    (Canny)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Morphological  │
│   Operations    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IC Detection   │
│   (Contours)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ROI Extraction  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Text        │
│  Segmentation   │
└────────┬────────┘
         │
         ▼
    OCR Engine
```

### 3. OCR Engine Architecture
```
┌──────────────────────────────────────┐
│          OCR Engine                   │
├──────────────────────────────────────┤
│                                       │
│  ┌──────────┐  ┌──────────┐         │
│  │ EasyOCR  │  │ PaddleOCR│         │
│  │ (Deep    │  │ (Fast    │         │
│  │Learning) │  │ Accurate)│         │
│  └────┬─────┘  └────┬─────┘         │
│       │             │                │
│       └──────┬──────┘                │
│              │                       │
│       ┌──────▼──────┐                │
│       │ Tesseract   │                │
│       │(Traditional)│                │
│       └──────┬──────┘                │
│              │                       │
│       ┌──────▼──────┐                │
│       │  Ensemble   │                │
│       │  Combiner   │                │
│       └──────┬──────┘                │
│              │                       │
│       ┌──────▼──────┐                │
│       │   Parser    │                │
│       │(Structure)  │                │
│       └──────┬──────┘                │
│              │                       │
│              ▼                       │
│      Structured Data                 │
│      • Part Number                   │
│      • Manufacturer                  │
│      • Date Code                     │
│      • Country                       │
│      • Lot Code                      │
└──────────────────────────────────────┘
```

### 4. Web Scraper Flow
```
┌────────────────────────────────────────┐
│         Web Scraper                     │
├────────────────────────────────────────┤
│                                         │
│  Input: Part Number + Manufacturer     │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │      Check Cache                 │  │
│  │  (30-day expiry)                 │  │
│  └─────────┬────────────────────────┘  │
│            │ Not Found                 │
│            ▼                            │
│  ┌──────────────────────────────────┐  │
│  │  Manufacturer Website Search     │  │
│  │  (Official source priority)      │  │
│  └─────────┬────────────────────────┘  │
│            │ Not Found                 │
│            ▼                            │
│  ┌──────────────────────────────────┐  │
│  │  Datasheet Database Search       │  │
│  │  • AllDatasheet.com              │  │
│  │  • DatasheetCatalog.com          │  │
│  │  • Octopart.com                  │  │
│  └─────────┬────────────────────────┘  │
│            │ Not Found                 │
│            ▼                            │
│  ┌──────────────────────────────────┐  │
│  │     Google Search                │  │
│  │  (Fallback)                      │  │
│  └─────────┬────────────────────────┘  │
│            │                            │
│            ▼                            │
│  ┌──────────────────────────────────┐  │
│  │   Download PDF/Webpage           │  │
│  └─────────┬────────────────────────┘  │
│            │                            │
│            ▼                            │
│  ┌──────────────────────────────────┐  │
│  │  Extract Marking Specs           │  │
│  │  • Part marking format           │  │
│  │  • Date code format              │  │
│  │  • Country codes                 │  │
│  │  • Package marking               │  │
│  └─────────┬────────────────────────┘  │
│            │                            │
│            ▼                            │
│  ┌──────────────────────────────────┐  │
│  │     Cache Results                │  │
│  └──────────────────────────────────┘  │
│                                         │
│  Output: Official Specifications       │
└────────────────────────────────────────┘
```

### 5. Verification Engine
```
┌──────────────────────────────────────────────┐
│          Verification Engine                  │
├──────────────────────────────────────────────┤
│                                               │
│  Inputs:                                      │
│  • Extracted Data (from OCR)                 │
│  • Official Data (from Datasheet)            │
│  • Image Data (quality metrics)              │
│                                               │
│  ┌─────────────────────────────────────┐     │
│  │  Check 1: Part Number               │     │
│  │  Weight: 30%                         │     │
│  │  Method: Fuzzy matching              │     │
│  └──────────────┬──────────────────────┘     │
│                 │                             │
│  ┌──────────────▼──────────────────────┐     │
│  │  Check 2: Manufacturer              │     │
│  │  Weight: 20%                         │     │
│  │  Method: Pattern matching            │     │
│  └──────────────┬──────────────────────┘     │
│                 │                             │
│  ┌──────────────▼──────────────────────┐     │
│  │  Check 3: Date Code                 │     │
│  │  Weight: 15%                         │     │
│  │  Method: Format & age validation    │     │
│  └──────────────┬──────────────────────┘     │
│                 │                             │
│  ┌──────────────▼──────────────────────┐     │
│  │  Check 4: Country of Origin         │     │
│  │  Weight: 10%                         │     │
│  │  Method: Code matching               │     │
│  └──────────────┬──────────────────────┘     │
│                 │                             │
│  ┌──────────────▼──────────────────────┐     │
│  │  Check 5: Print Quality             │     │
│  │  Weight: 15%                         │     │
│  │  Method: Image analysis              │     │
│  │  • Sharpness                         │     │
│  │  • Contrast                          │     │
│  │  • Noise level                       │     │
│  │  • Edge density                      │     │
│  └──────────────┬──────────────────────┘     │
│                 │                             │
│  ┌──────────────▼──────────────────────┐     │
│  │  Check 6: Marking Format            │     │
│  │  Weight: 10%                         │     │
│  │  Method: Structure validation       │     │
│  └──────────────┬──────────────────────┘     │
│                 │                             │
│  ┌──────────────▼──────────────────────┐     │
│  │    Calculate Confidence             │     │
│  │    (Weighted average)                │     │
│  └──────────────┬──────────────────────┘     │
│                 │                             │
│  ┌──────────────▼──────────────────────┐     │
│  │  Determine Authenticity             │     │
│  │  Pass rate ≥70% AND                 │     │
│  │  Confidence ≥65%                     │     │
│  └──────────────┬──────────────────────┘     │
│                 │                             │
│                 ▼                             │
│  Output:                                      │
│  • is_authentic: True/False                  │
│  • confidence: 0-100%                        │
│  • checks_passed: []                         │
│  • checks_failed: []                         │
│  • anomalies: []                             │
│  • recommendation: string                    │
└──────────────────────────────────────────────┘
```

### 6. Database Schema
```
┌────────────────────────────────────────┐
│         Database (SQLite)               │
├────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   analyses Table                 │  │
│  ├──────────────────────────────────┤  │
│  │  id (PK)                         │  │
│  │  timestamp                       │  │
│  │  image_path                      │  │
│  │  part_number                     │  │
│  │  manufacturer                    │  │
│  │  is_authentic                    │  │
│  │  confidence                      │  │
│  │  extracted_data (JSON)           │  │
│  │  official_data (JSON)            │  │
│  │  verification_results (JSON)     │  │
│  │  recommendation                  │  │
│  │  created_at                      │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   statistics Table               │  │
│  ├──────────────────────────────────┤  │
│  │  id (PK)                         │  │
│  │  date                            │  │
│  │  total_analyses                  │  │
│  │  authentic_count                 │  │
│  │  counterfeit_count               │  │
│  │  avg_confidence                  │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

## Data Flow

### Complete Analysis Flow
```
User
 │
 ├─ Load Image ──────────────────────────────────┐
 │                                                │
 ├─ Select Settings ──────────────────────────┐  │
 │                                             │  │
 └─ Click Analyze ─────────┐                  │  │
                           │                  │  │
                           ▼                  ▼  ▼
                    ┌──────────────────────────────┐
                    │   Processing Thread          │
                    ├──────────────────────────────┤
                    │                              │
                    │  1. Image Processor          │
                    │     └─► Processed Images     │
                    │                              │
                    │  2. IC Detection             │
                    │     └─► IC Regions           │
                    │                              │
                    │  3. ROI Extraction           │
                    │     └─► Marking Images       │
                    │                              │
                    │  4. OCR Engine               │
                    │     └─► Extracted Text       │
                    │                              │
                    │  5. Structure Parser         │
                    │     └─► Parsed Data          │
                    │                              │
                    │  6. Web Scraper              │
                    │     └─► Official Specs       │
                    │                              │
                    │  7. Verification Engine      │
                    │     └─► Verification Result  │
                    │                              │
                    └──────────┬───────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌───────────┐  ┌────────────┐  ┌──────────┐
        │ Display   │  │  Database  │  │  Cache   │
        │ Results   │  │   Save     │  │  Update  │
        └───────────┘  └────────────┘  └──────────┘
                │
                ▼
             User Reviews
                │
         ┌──────┴──────┐
         │             │
         ▼             ▼
    Accept        Export Report
```

## Threading Model
```
Main Thread (GUI)
    │
    ├─► UI Updates
    │   └─► Progress Bar
    │   └─► Status Text
    │   └─► Button States
    │
    └─► Processing Thread
        │
        ├─► Image Processing
        ├─► OCR
        ├─► Web Scraping
        └─► Verification
        │
        └─► Signals to Main Thread
            ├─► progress(int)
            ├─► status(str)
            ├─► result(dict)
            └─► debug_images(dict)
```

## Module Dependencies
```
ic_authenticator.py
    ├── PyQt5 (GUI)
    ├── image_processor.py
    │   ├── OpenCV
    │   ├── NumPy
    │   └── scikit-image
    ├── ocr_engine.py
    │   ├── EasyOCR
    │   ├── PaddleOCR
    │   ├── Tesseract
    │   └── fuzzywuzzy
    ├── web_scraper.py
    │   ├── requests
    │   ├── BeautifulSoup
    │   ├── PyPDF2
    │   └── pdfplumber
    ├── verification_engine.py
    │   ├── NumPy
    │   ├── OpenCV
    │   └── fuzzywuzzy
    └── database_manager.py
        └── sqlite3
```

## Configuration Flow
```
config.json
    │
    ├─► System Settings
    │   ├─ cache_dir
    │   ├─ reports_dir
    │   └─ database
    │
    ├─► OCR Settings
    │   ├─ default_method
    │   └─ thresholds
    │
    ├─► Image Processing
    │   ├─ CLAHE params
    │   └─ Detection params
    │
    ├─► Verification
    │   ├─ weights
    │   └─ thresholds
    │
    └─► Web Scraper
        ├─ cache_expiry
        └─ sources
```

## Performance Considerations
```
Bottlenecks:
1. OCR Processing (30-40s)
   └─► Mitigation: Use single method for speed
   
2. Web Scraping (10-20s)
   └─► Mitigation: Cache results
   
3. Image Processing (5-10s)
   └─► Mitigation: Optimize resolution

Total Time: ~30-60 seconds per image
```

---

**System Architecture v1.0.0**
*Modular, Scalable, Production-Ready*
