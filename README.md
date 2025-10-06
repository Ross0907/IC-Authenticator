# IC Authentication System - AOI Platform

Advanced Automated Optical Inspection (AOI) system for detecting counterfeit integrated circuits based on marking analysis and datasheet verification.

## Features

### Core Functionality
- **Multi-Method OCR**: EasyOCR, PaddleOCR, Tesseract, and ensemble methods
- **Intelligent Image Processing**: Advanced preprocessing with CLAHE, denoising, and edge detection
- **IC Detection**: Automatic component detection and marking extraction
- **Web Scraping**: Automated datasheet search and marking specification extraction
- **Verification Engine**: Multi-factor authentication analysis
- **Quality Analysis**: Print quality assessment for counterfeit detection

### User Interface
- Modern PyQt5 GUI with tabbed interface
- Real-time processing with progress indication
- Debug visualization layers for image processing steps
- Comprehensive results display
- Analysis history and statistics tracking
- Batch processing support
- Export reports (JSON, PDF, TXT)

### Verification Methods
1. **Part Number Verification**: Fuzzy matching against official specifications
2. **Manufacturer Identification**: Recognition of major IC manufacturers
3. **Date Code Validation**: Format checking and age verification
4. **Country of Origin**: Verification against expected manufacturing locations
5. **Print Quality Analysis**: Sharpness, contrast, noise assessment
6. **Marking Format Consistency**: Structure and format validation
7. **Laser Marking Detection**: Distinguishing authentic laser-etched markings

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) CUDA for GPU acceleration

### Setup Steps

1. **Clone or download the project**
```powershell
cd C:\Users\Ross\Downloads\Ic_detection
```

2. **Create a virtual environment (recommended)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Install Tesseract OCR** (Windows)
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location
   - Add to PATH or update code with installation path

5. **Download EasyOCR models** (automatic on first run)
   - Models will be downloaded to `~/.EasyOCR/model/`
   - Requires ~500MB of disk space

## Usage

### Running the Application

```powershell
python ic_authenticator.py
```

### Workflow

1. **Load Image**
   - Click "Load IC Image" button
   - Select an image of an IC component
   - Supported formats: PNG, JPG, JPEG, BMP, TIFF

2. **Configure Settings**
   - Select OCR method (recommend "Ensemble" for best accuracy)
   - Enable/disable debug visualization layers
   - Adjust processing parameters if needed

3. **Analyze IC**
   - Click "Analyze IC" button
   - Wait for processing to complete (typically 30-60 seconds)
   - View results in different tabs

4. **Review Results**
   - **Image Analysis Tab**: View the loaded image
   - **Debug Layers Tab**: Inspect preprocessing steps
   - **Results Tab**: View extracted markings and analysis
   - **Verification Tab**: See authenticity determination and confidence score

5. **Export Report**
   - Click "Export Report" after analysis
   - Choose format (JSON, PDF, or TXT)
   - Save for documentation

### Test Images

Sample images are provided in the `test_images` folder:
- `ADC0831_0-300x300.png`: ADC IC component
- `Screenshot 2025-10-06 222749.png`: Sample IC marking
- `Screenshot 2025-10-06 222803.png`: Sample IC marking

## Debug Visualization Layers

The system provides multiple debug layers for analysis:

1. **Original**: Raw input image
2. **Grayscale**: Converted grayscale image
3. **Denoised**: Noise-reduced image
4. **Enhanced**: CLAHE-enhanced contrast
5. **Edge Detection**: Canny edge detection result
6. **IC Detection**: Detected component regions
7. **ROI Extraction**: Extracted regions of interest
8. **Text Segmentation**: Detected text lines
9. **Feature Analysis**: Extracted features visualization

## System Architecture

```
ic_authenticator.py         # Main GUI application
├── image_processor.py       # Image preprocessing and enhancement
├── ocr_engine.py           # Multi-method OCR extraction
├── web_scraper.py          # Datasheet search and parsing
├── verification_engine.py  # Authenticity verification logic
└── database_manager.py     # Analysis history storage
```

## Verification Criteria

The system evaluates components based on:

### Critical Checks (High Weight)
- **Part Number Match** (30%): Exact or close match to official marking
- **Manufacturer Verification** (20%): Recognized manufacturer identification

### Important Checks (Medium Weight)
- **Date Code Validation** (15%): Valid format and reasonable age
- **Print Quality** (15%): Sharpness, contrast, and clarity

### Supporting Checks (Lower Weight)
- **Country of Origin** (10%): Matches expected manufacturing locations
- **Marking Format** (10%): Consistent with standard IC marking practices

### Confidence Scoring
- **85-100%**: High confidence - Component appears authentic
- **65-84%**: Medium confidence - Likely authentic with minor concerns
- **0-64%**: Low confidence - Authenticity suspect

## Advanced Features

### Batch Processing
Process multiple IC images in sequence:
1. Click "Batch Processing" button
2. Select multiple images
3. System processes each and generates summary report

### Analysis History
View past analyses:
1. Click "View History" button
2. Browse previous results
3. Search by part number
4. View statistics and trends

### Custom Configuration
Edit settings for advanced users:
- OCR confidence thresholds
- Image preprocessing parameters
- Verification rule weights
- Datasheet search sources

## Troubleshooting

### Common Issues

**1. OCR Not Working**
- Ensure all OCR engines are installed
- Check Tesseract installation and PATH
- Try different OCR methods

**2. Poor Detection Results**
- Ensure good image quality (sharp, well-lit)
- Try preprocessing images externally
- Adjust detection thresholds

**3. Slow Processing**
- Disable unused OCR methods
- Reduce image resolution
- Enable GPU acceleration if available

**4. Web Scraping Failures**
- Check internet connection
- Verify datasheet sources are accessible
- Use cached data when available

## Technical Details

### Image Processing Pipeline
1. Grayscale conversion
2. Noise reduction (Non-local means denoising)
3. Contrast enhancement (CLAHE)
4. Edge detection (Canny)
5. Morphological operations
6. Component detection (contour analysis)
7. ROI extraction
8. Text region segmentation

### OCR Methods
- **EasyOCR**: Deep learning-based, excellent for diverse fonts
- **PaddleOCR**: Fast and accurate, good for structured text
- **Tesseract**: Traditional OCR, good for standard fonts
- **Ensemble**: Combines all methods for maximum accuracy

### Verification Algorithm
1. Extract markings using OCR
2. Parse structured information (part number, date code, etc.)
3. Search online datasheets
4. Extract official marking specifications
5. Compare extracted vs. official markings
6. Analyze print quality
7. Calculate confidence score
8. Generate recommendation

## Research References

This system is based on research from:
- Harrison: "Exploration of Automated Laser Marking Analysis for Counterfeit IC Identification"
- Chang et al.: "Deep Learning-based AOI System for Detecting Component Marks"
- Springer: "Automated Optical Inspection for IC Component Verification"

## Future Enhancements

- [ ] Deep learning-based IC detection (YOLO)
- [ ] Advanced laser marking texture analysis
- [ ] Real-time camera integration
- [ ] Cloud-based datasheet database
- [ ] Mobile application
- [ ] Integration with manufacturing ERP systems
- [ ] X-ray analysis integration
- [ ] Blockchain-based authenticity tracking

## License

This system is developed for educational and research purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review debug visualization layers
3. Consult research papers
4. Contact development team

## Acknowledgments

- Research papers for theoretical foundation
- Open-source OCR engines (EasyOCR, PaddleOCR, Tesseract)
- OpenCV for image processing
- PyQt5 for GUI framework
