# IC Authentication System# IC Authentication System# IC Authenticator - Production System v3.0



A professional GPU-accelerated system for detecting counterfeit integrated circuits using advanced OCR, manufacturer marking validation, and datasheet verification.



## OverviewA professional GPU-accelerated system for detecting counterfeit integrated circuits using advanced OCR, manufacturer marking validation, and datasheet verification.Advanced counterfeit IC detection system based on multiple research papers and production-grade AI/CV techniques.



This system analyzes IC chip images to determine authenticity by:

- Extracting text using GPU-accelerated OCR with enhanced preprocessing

- Validating manufacturer markings against industry standards## Overview## 🎯 Features

- Verifying part numbers through multiple datasheet sources

- Scoring authenticity based on comprehensive criteria (0-100%)



## RequirementsThis system analyzes IC chip images to determine authenticity by:### Core Capabilities



```bash- Extracting text using GPU-accelerated OCR with enhanced preprocessing- **Advanced OCR**: 7+ preprocessing methods with ensemble selection

pip install -r requirements.txt

```- Validating manufacturer markings against industry standards- **Multi-scale Enhancement**: Based on research papers (3x upscaling, rotation augmentation)



**Key Dependencies:**- Verifying part numbers through multiple datasheet sources- **Manufacturer Validation**: Pattern-based marking verification

- Python 3.8+

- PyQt5 (GUI framework)- Scoring authenticity based on comprehensive criteria (0-100%)- **Datasheet Verification**: Searches 5+ online sources

- opencv-python (Image processing)

- easyocr (Text recognition)- **Confidence Scoring**: Detailed breakdown with traceability

- torch (GPU acceleration - optional but recommended)

- numpy, scipy (Image analysis)## Requirements- **GPU Acceleration**: CUDA support for faster processing

- beautifulsoup4, requests (Datasheet verification)



**Optional:**

- CUDA-capable GPU for 4-5x faster processing```bash### Research-Based Techniques



## Usagepip install -r requirements.txtThis system implements methods from:



### GUI Interface```1. **AutoDetect** - Novel Autoencoding Architecture for Counterfeit IC Detection



**Launch GUI Launcher** (choose between Classic or Modern interface):2. **IC SynthLogo** - Synthetic Logo Dataset for Counterfeit Detection

```bash

python launch_gui.py**Key Dependencies:**3. **Harrison et al.** - Automated Laser Marking Analysis

```

- Python 3.8+4. **Deep Learning AOI** - Component Marks Detection System

**Or launch directly:**

```bash- PyQt5 (GUI framework)5. **PCB Logo Classification** - Data Augmentation for Assurance

python gui_classic_production.py   # Classic tabbed interface

python gui_modern_production.py    # Modern card-based interface- opencv-python (Image processing)

```

- easyocr (Text recognition)## 📋 Requirements

### Steps:

1. Click "Select IC Image" and choose a clear photo of an IC chip- torch (GPU acceleration - optional but recommended)

2. Click "Authenticate IC" to start analysis

3. View comprehensive results including:- numpy, scipy (Image analysis)```

   - Authenticity verdict (Authentic/Counterfeit)

   - Confidence score (0-100%)- beautifulsoup4, requests (Datasheet verification)Python 3.8+

   - Part number identification

   - Manufacturer and date codesCUDA 11.8+ (optional, for GPU acceleration)

   - Datasheet verification

   - Detailed marking validation**Optional:**```



### Programmatic Use- CUDA-capable GPU for 4-5x faster processing



```python### Dependencies

from final_production_authenticator import FinalProductionAuthenticator

## Usage```

authenticator = FinalProductionAuthenticator()

result = authenticator.authenticate("path/to/ic_image.jpg")torch>=2.0.0



print(f"Authentic: {result['is_authentic']}")### GUI Interfaceeasyocr>=1.7.0

print(f"Confidence: {result['confidence']}%")

print(f"Part Number: {result['part_number']}")opencv-python>=4.8.0

print(f"Manufacturer: {result['manufacturer']}")

```**Launch GUI Launcher** (choose between Classic or Modern interface):numpy>=1.24.0



## Authentication Criteria```bashPillow>=10.0.0



The system uses a 100-point scoring system:python launch_gui.pyrequests>=2.31.0



- **40 points**: Manufacturer marking validation (CRITICAL)```beautifulsoup4>=4.12.0

  - Date code format (YYWW pattern)

  - Lot code presence```

  - Marking completeness

  **Or launch directly:**

- **30 points**: Datasheet verification

  - Searches multiple sources (Microchip, TI, Infineon, Octopart, AllDatasheet, etc.)```bashInstall all dependencies:

  

- **20 points**: OCR qualitypython gui_classic_production.py   # Classic tabbed interface```bash

  - Text extraction confidence

  python gui_modern_production.py    # Modern card-based interfacepip install -r requirements.txt

- **10 points**: Date code presence

``````

**Verdict**: 70+ points AND valid markings = Authentic



## GUI Features

### Steps:## 🚀 Quick Start

Both interfaces include:

- Dark/Light mode toggle1. Click "Select IC Image" and choose a clear photo of an IC chip

- Real-time processing with progress tracking

- Comprehensive results display2. Click "Authenticate IC" to start analysis### GUI Application

- Detailed marking validation

- Datasheet source and URL3. View comprehensive results including:```bash

- OCR extraction details

- Complete confidence score breakdown   - Authenticity verdict (Authentic/Counterfeit)python production_gui.py



### Classic Interface   - Confidence score (0-100%)```

- Three-tab layout (Summary, Detailed Analysis, Raw Data)

- Traditional professional design   - Part number identification

- Organized information display

   - Manufacturer and date codes### Command Line

### Modern Interface

- Card-based design with metrics   - Datasheet verification```python

- Three-column layout

- Contemporary aesthetics   - Detailed marking validationfrom production_ic_authenticator import ProductionICAuthenticator



## Image Guidelines



For best results:### Programmatic Useauthenticator = ProductionICAuthenticator()

- ✅ Clear, focused images

- ✅ Even lighting without glareresult = authenticator.authenticate("path/to/ic_image.jpg")

- ✅ High resolution (1000px+)

- ✅ Direct overhead angle```python

- ❌ Avoid blurry, shadowed, or low-resolution images

from final_production_authenticator import FinalProductionAuthenticatorprint(f"Part: {result.part_number}")

## Project Structure

print(f"Authentic: {result.is_authentic}")

```

.authenticator = FinalProductionAuthenticator()print(f"Confidence: {result.confidence}%")

├── final_production_authenticator.py  # Core authentication engine

├── enhanced_preprocessing.py          # Image preprocessingresult = authenticator.authenticate("path/to/ic_image.jpg")```

├── marking_validator.py               # Manufacturer marking validation

├── working_web_scraper.py            # Datasheet verification

├── database_manager.py                # Analysis history storage

├── gui_classic_production.py         # Classic GUIprint(f"Authentic: {result['is_authentic']}")### Batch Testing

├── gui_modern_production.py          # Modern GUI

├── launch_gui.py                     # GUI launcherprint(f"Confidence: {result['confidence']}%")```bash

├── requirements.txt                   # Python dependencies

├── test_images/                       # Sample IC imagesprint(f"Part Number: {result['part_number']}")python test_comprehensive.py

└── research_papers/                   # Academic references

```print(f"Manufacturer: {result['manufacturer']}")```



## Technical Details```



**Text Extraction:**## 📊 System Architecture

- Multi-variant preprocessing (8+ methods including CLAHE, bilateral filtering, upscaling)

- GPU-accelerated EasyOCR## Authentication Criteria

- Automatic error correction and normalization

### Preprocessing Pipeline

**Marking Validation:**

- Based on IEEE research and manufacturer specificationsThe system uses a 100-point scoring system:```

- Validates date codes, lot codes, and marking patterns

- Detects common counterfeit indicatorsInput Image



**Performance:**- **40 points**: Manufacturer marking validation (CRITICAL)    ↓

- Processing time: 0.5-5 seconds per image (GPU)

- Memory usage: ~2GB with GPU  - Date code format (YYWW pattern)Multi-Method Preprocessing (7 variants):

- Supported formats: JPG, PNG, BMP

  - Lot code presence  1. Upscale + CLAHE + Unsharp Mask

## License

  - Marking completeness  2. Morphological Gradient

See LICENSE.txt for details.

    3. Bilateral Filter + CLAHE

## Research Foundation

- **30 points**: Datasheet verification  4. Rotation Augmentation (-5°, 0°, +5°)

This system implements techniques from peer-reviewed research papers available in the `research_papers/` directory, including:

- IEEE: "Detection of Counterfeit Electronic Components"  - Searches multiple sources (Microchip, TI, Infineon, Octopart, AllDatasheet, etc.)  5. Sauvola Adaptive Thresholding

- "Analysis of Image Preprocessing and Binarization Methods for OCR-Based IC Detection"

- "Deep Learning-based AOI System for Detecting Component Marks"    6. Sample-wise Standardization



---- **20 points**: OCR quality    ↓



**Version**: 2.1    - Text extraction confidenceEnsemble OCR Selection

**Status**: Production Ready

      ↓

- **10 points**: Date code presenceBest Result (by confidence + quality)

```

**Verdict**: 70+ points AND valid markings = Authentic

### Authentication Scoring

## GUI Features

| Component | Points | Description |

Both interfaces include:|-----------|--------|-------------|

- Dark/Light mode toggle| **Marking Validation** | 40 | Most critical - manufacturer marking patterns |

- Real-time processing with progress tracking| **Datasheet Found** | 30 | Official documentation from trusted sources |

- Comprehensive results display| **OCR Quality** | 20 | Text extraction confidence |

- Detailed marking validation| **Date Code Present** | 10 | Manufacturing date verification |

- Datasheet source and URL

- OCR extraction details**Threshold**: 70+ points AND valid markings = AUTHENTIC

- Complete confidence score breakdown

## 🔬 Technical Details

### Classic Interface

- Three-tab layout (Summary, Detailed Analysis, Raw Data)### Preprocessing Methods

- Traditional professional design

- Organized information display#### 1. Upscale + CLAHE + Unsharp Mask

- **Research**: Paper 3 (Median blur for noise removal)

### Modern Interface- **Purpose**: Enhance engraved/laser-etched text

- Card-based design with metrics- **Steps**:

- Three-column layout  - 3x cubic interpolation upscaling

- Contemporary aesthetics  - Median blur (removes salt & pepper noise)

  - CLAHE with clipLimit=8.0

## Image Guidelines  - Unsharp masking for edge enhancement



For best results:#### 2. Morphological Gradient

- ✅ Clear, focused images- **Research**: Paper 3 (Morphological operations for features)

- ✅ Even lighting without glare- **Purpose**: Detect text edges and boundaries

- ✅ High resolution (1000px+)- **Steps**:

- ✅ Direct overhead angle  - 2x upscaling

- ❌ Avoid blurry, shadowed, or low-resolution images  - CLAHE enhancement

  - Morphological gradient with 3x3 kernel

## Project Structure  - Weighted combination with enhanced image



```#### 3. Rotation Augmentation

.- **Research**: Paper 2 (Data augmentation techniques)

├── final_production_authenticator.py  # Core authentication engine- **Purpose**: Handle tilted/rotated chips

├── enhanced_preprocessing.py          # Image preprocessing- **Steps**:

├── marking_validator.py               # Manufacturer marking validation  - Test angles: -5°, 0°, +5°

├── working_web_scraper.py            # Datasheet verification  - Maintain image quality with cubic interpolation

├── database_manager.py                # Analysis history storage  - CLAHE on each variant

├── gui_classic_production.py         # Classic GUI

├── gui_modern_production.py          # Modern GUI#### 4. Sauvola Adaptive Thresholding

├── launch_gui.py                     # GUI launcher- **Research**: Sauvola & Pietikäinen (2000)

├── requirements.txt                   # Python dependencies- **Purpose**: Handle uneven illumination

├── test_images/                       # Sample IC images- **Formula**: `T(x,y) = m(x,y) * (1 + k * ((s(x,y) / r) - 1))`

└── research_papers/                   # Academic references- **Parameters**: window_size=25, k=0.2, r=128

```

#### 5. Sample-wise Standardization

## Technical Details- **Research**: Paper 4 (Preprocessing normalization)

- **Purpose**: Normalize brightness variations

**Text Extraction:**- **Steps**:

- Multi-variant preprocessing (8+ methods including CLAHE, bilateral filtering, upscaling)  - Normalize to [0, 1]

- GPU-accelerated EasyOCR  - Center around mean

- Automatic error correction and normalization  - Standardize by std deviation

  - Rescale to [0, 255]

**Marking Validation:**

- Based on IEEE research and manufacturer specifications### OCR Ensemble Selection

- Validates date codes, lot codes, and marking patterns

- Detects common counterfeit indicatorsThe system runs OCR on all preprocessing variants and selects the best result based on:



**Performance:****Quality Score = (OCR Confidence × 0.6) + (Text Quality × 0.4)**

- Processing time: 0.5-5 seconds per image (GPU)

- Memory usage: ~2GB with GPUText quality factors:

- Supported formats: JPG, PNG, BMP- Length (5-60 chars preferred)

- Alphanumeric content (both letters and numbers)

## License- Special character ratio (<15% preferred)

- Known IC pattern matching

See LICENSE.txt for details.

## 📈 Performance

## Research Foundation

### Test Results

This system implements techniques from peer-reviewed research papers available in the `research_papers/` directory, including:- **Average OCR Confidence**: 83.2%

- IEEE: "Detection of Counterfeit Electronic Components"- **Authentication Accuracy**: 5/6 images (83.3%)

- "Analysis of Image Preprocessing and Binarization Methods for OCR-Based IC Detection"- **Processing Time**: 0.75-4.66s per image

- "Deep Learning-based AOI System for Detecting Component Marks"- **GPU Speedup**: ~3-5x faster than CPU



---### Supported IC Types

- Microcontrollers (ATMEGA, STM32, PIC, etc.)

**Version**: 2.1  - Logic ICs (SN74 series, 4000 series)

**Status**: Production Ready- ADCs/DACs (ADC0831, DAC0800, etc.)

- Memory chips (24C, 25C series)
- Processors (Cypress, Infineon, etc.)

## 📝 Output Information

### Detailed Results Include:
- ✅ **Image Information**: Name, path, dimensions, processing time
- ✅ **Part Details**: Part number, manufacturer, date codes
- ✅ **OCR Details**: Extracted text, confidence, method used, preprocessing variant
- ✅ **Marking Validation**: Expected vs detected format, issues found
- ✅ **Datasheet Info**: Found status, source, URL
- ✅ **Score Breakdown**: Points per component, final score
- ✅ **Technical Info**: GPU usage, processing time

## 🛠️ Project Structure

```
Ic_detection/
├── production_ic_authenticator.py  # Main authenticator
├── production_gui.py                # GUI application
├── marking_validator.py             # Marking validation
├── working_web_scraper.py           # Datasheet scraper
├── database_manager.py              # Database operations
├── test_comprehensive.py            # Testing script
├── cleanup_project.py               # Cleanup utility
├── config.json                      # Configuration
├── requirements.txt                 # Dependencies
├── README.md                        # This file
├── test_images/                     # Test images
├── research_papers/                 # Reference papers
├── datasheet_cache/                 # Cached datasheets
└── production_debug/                # Debug output
```

## 🧹 Project Cleanup

To clean up old/obsolete files:
```bash
python cleanup_project.py
```

This will:
- Archive obsolete files to `archive_backup/`
- Remove __pycache__ directories
- Keep only essential production files
- Generate cleanup report

## 🔍 Troubleshooting

### Low OCR Accuracy
- Ensure image is well-lit and in focus
- Try higher resolution images (min 300x300)
- Check for glare or reflections on chip surface

### GPU Not Detected
- Install CUDA 11.8+ from NVIDIA
- Ensure PyTorch is installed with CUDA support:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```

### Datasheet Not Found
- Check internet connection
- Part number may be obsolete or uncommon
- Try manufacturer's website directly

## 📖 Research Papers

All research papers referenced in this system are available in the `research_papers/` directory:

1. AutoDetect (Journal of Hardware and Systems Security, 2024)
2. IC SynthLogo (PCB Logo Classification)
3. Harrison et al. (Automated Laser Marking Analysis)
4. Deep Learning AOI (Component Marks Detection)
5. PCB Logo Classification (Data Augmentation)

## 📜 License

This project is licensed under the MIT License - see LICENSE.txt for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check research papers for technical details
- Review test_comprehensive.py for usage examples

## 🎯 Future Enhancements

- [ ] Web-based interface
- [ ] Mobile app support
- [ ] Additional IC manufacturer patterns
- [ ] Database of known counterfeit patterns
- [ ] Automated reporting system
- [ ] Integration with ERP systems

---

**Version**: 3.0  
**Last Updated**: October 2025  
**Status**: Production Ready ✅
