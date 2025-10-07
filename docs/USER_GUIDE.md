# User Guide - IC Authentication System

## Table of Contents
1. [Getting Started](#getting-started)
2. [Main Interface](#main-interface)
3. [Loading Images](#loading-images)
4. [Configuring Analysis](#configuring-analysis)
5. [Running Analysis](#running-analysis)
6. [Understanding Results](#understanding-results)
7. [Debug Visualization](#debug-visualization)
8. [Batch Processing](#batch-processing)
9. [Exporting Reports](#exporting-reports)
10. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### First Launch

1. Open PowerShell in the project folder
2. Run: `.\run.ps1` (automated) OR `python ic_authenticator.py` (manual)
3. The main window will appear

### Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                    IC Authentication System                      │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                   │
│   Control    │              Display Area                        │
│    Panel     │         (Tabs: Image/Debug/Results/Verify)      │
│              │                                                   │
│  - Load      │                                                   │
│  - Settings  │                                                   │
│  - Analyze   │                                                   │
│  - Options   │                                                   │
│              │                                                   │
└──────────────┴──────────────────────────────────────────────────┘
```

---

## Main Interface

### Control Panel (Left Side)

**Image Input Section:**
- 📁 **Load IC Image**: Select image file from disk
- 📷 **Capture from Camera**: Take photo (future feature)

**OCR Settings:**
- Dropdown menu to select OCR method:
  - `Ensemble (All)` - Combines all methods (RECOMMENDED)
  - `EasyOCR` - Deep learning OCR
  - `PaddleOCR` - Fast Chinese/English OCR
  - `Tesseract` - Traditional OCR

**Debug Visualization:**
- ☑ Show Preprocessing Steps
- ☑ Show IC Detection
- ☑ Show Text Segmentation
- ☑ Show Feature Analysis

**Analysis Button:**
- 🔍 **Analyze IC** - Start the analysis (enabled after loading image)

**Progress Indicator:**
- Progress bar showing analysis progress (0-100%)
- Status text showing current step

**Additional Options:**
- 📦 **Batch Processing** - Process multiple images
- 📊 **View History** - See past analyses
- 💾 **Export Report** - Save results

### Display Area (Right Side)

**Tab 1: 📷 Image Analysis**
- Shows the loaded IC image
- Image information (dimensions, filename)
- Can zoom and pan

**Tab 2: 🔧 Debug Layers**
- Dropdown to select debug layer
- Shows various processing stages
- Helps understand the analysis process

**Tab 3: 📋 Results**
- Extracted markings
- Official specifications
- Comparison results
- Detailed analysis text

**Tab 4: ✓ Verification**
- Authenticity determination (Authentic/Suspect)
- Confidence score (0-100%)
- Detailed verification info
- Recommendation

---

## Loading Images

### Supported Formats
- PNG (recommended)
- JPEG/JPG
- BMP
- TIFF

### Image Requirements

**Resolution:**
- Minimum: 640x480 pixels
- Recommended: 1280x960 or higher
- Maximum: Limited by RAM

**Quality:**
- Sharp focus on IC markings
- Good lighting (avoid shadows)
- Minimal background noise
- IC should occupy significant portion of image

**Best Practices:**
- Use macro lens or close-up mode
- Even, diffuse lighting
- Perpendicular angle to IC surface
- Avoid reflections on shiny surfaces

### Loading Steps

1. Click **"Load IC Image"** button
2. Navigate to image file
3. Select image
4. Click **"Open"**
5. Image appears in "Image Analysis" tab
6. **"Analyze IC"** button becomes enabled

---

## Configuring Analysis

### OCR Method Selection

**Ensemble (All)** - RECOMMENDED
- Uses all available OCR engines
- Combines results for best accuracy
- Slower but most reliable
- Use for critical verification

**EasyOCR**
- Deep learning-based
- Good for varied fonts and angles
- Moderate speed
- Use for difficult markings

**PaddleOCR**
- Fast and accurate
- Good for standard text
- Fastest option
- Use for clear markings

**Tesseract**
- Traditional OCR
- Good for printed text
- Moderate accuracy
- Use for standard fonts

### Debug Options

Enable/disable visualization layers:
- **Preprocessing**: See noise reduction, enhancement
- **IC Detection**: See detected component regions
- **Text Segmentation**: See identified text areas
- **Feature Analysis**: See extracted features

Recommendation: Enable all for first analysis, then disable for faster processing.

---

## Running Analysis

### Analysis Process

1. Ensure image is loaded
2. Select OCR method
3. Enable desired debug options
4. Click **"Analyze IC"** button
5. Watch progress bar and status updates
6. Wait for completion (30-60 seconds typically)

### Progress Steps

You'll see these status messages:

1. "Loading image..." (10%)
2. "Preprocessing image..." (20%)
3. "Detecting IC component..." (30%)
4. "Extracting markings..." (40%)
5. "Performing OCR..." (50%)
6. "Parsing marking information..." (60%)
7. "Searching for datasheet..." (70%)
8. "Analyzing datasheet..." (80%)
9. "Verifying authenticity..." (90%)
10. "Compilation results..." (95%)
11. "Analysis complete!" (100%)

### What Happens Behind the Scenes

```
Your Image
    ↓
Image Processing (noise reduction, enhancement)
    ↓
IC Detection (find the component)
    ↓
Marking Extraction (locate text regions)
    ↓
OCR Processing (read the text)
    ↓
Structure Parsing (identify part number, date, etc.)
    ↓
Datasheet Search (find official specs online)
    ↓
Specification Extraction (get official markings)
    ↓
Multi-Factor Verification (compare and analyze)
    ↓
Confidence Calculation
    ↓
Results Display
```

---

## Understanding Results

### Results Tab

**Section 1: Extracted Markings**
```
Part Number: LM358N
Manufacturer: Texas Instruments
Date Code: 2143
Country: MALAYSIA
```

**Section 2: Official Markings** (from datasheet)
```
Part Marking: LM358N
Date Code Format: YYWW (Year-Week)
Country Codes: MALAYSIA, CHINA, PHILIPPINES
```

**Section 3: Verification Results**
```
Authentic: True/False
Confidence: 85.5%
Recommendation: [Detailed recommendation]
```

**Section 4: Detected Anomalies** (if any)
```
- Part number mismatch
- Invalid date code
- Poor print quality
- etc.
```

### Verification Tab

**Authenticity Indicator**
- Green background: ✓ AUTHENTIC
- Red background: ✗ COUNTERFEIT SUSPECTED

**Confidence Bar**
- Visual representation of confidence (0-100%)
- Green: High (85-100%)
- Yellow: Medium (65-84%)
- Red: Low (0-64%)

**Detailed Info**
- JSON-formatted verification details
- Scores for each verification check
- Reasoning for each decision

### Interpreting Confidence Scores

**85-100% (High Confidence)**
```
✓ All major checks passed
✓ Markings match official specs
✓ Good print quality
✓ Valid date code
→ Component appears AUTHENTIC
→ Recommended: ACCEPT
```

**65-84% (Medium Confidence)**
```
⚠ Most checks passed
⚠ Minor discrepancies noted
⚠ Some concerns but not critical
→ Component likely authentic
→ Recommended: ACCEPT with additional inspection
```

**0-64% (Low Confidence)**
```
✗ Critical checks failed
✗ Significant discrepancies
✗ Multiple anomalies detected
→ Component authenticity SUSPECT
→ Recommended: REJECT and investigate
```

---

## Debug Visualization

### Available Layers

1. **Original**
   - The raw input image
   - No processing applied

2. **Grayscale**
   - Converted to grayscale
   - Simplifies analysis

3. **Denoised**
   - Noise reduction applied
   - Cleaner image for processing

4. **Enhanced**
   - Contrast enhanced using CLAHE
   - Better visibility of markings

5. **Edge Detection**
   - Edges detected using Canny algorithm
   - Shows boundaries and text edges

6. **IC Detection**
   - Green boxes around detected ICs
   - Shows what the system identified as components

7. **ROI Extraction**
   - Regions of Interest highlighted
   - Shows areas selected for OCR

8. **Text Segmentation**
   - Individual text lines identified
   - Shows how text is separated

9. **Feature Analysis**
   - Extracted features visualization
   - Advanced analysis data

### How to Use Debug Layers

1. Go to **"Debug Layers"** tab
2. Select layer from dropdown
3. View the processed image
4. Switch between layers to understand processing
5. Helpful for troubleshooting poor results

### Troubleshooting with Debug Layers

**Problem: No IC detected**
- Check "IC Detection" layer
- If empty, adjust image quality or framing

**Problem: Poor OCR results**
- Check "Enhanced" layer - should have good contrast
- Check "Text Segmentation" - should show text boxes
- If text not segmented, IC might be out of focus

**Problem: Low confidence**
- Review all layers to identify weak points
- Check if preprocessing is adequate
- Verify IC is clearly visible in "Enhanced" layer

---

## Batch Processing

### Use Case
Process multiple IC images at once, useful for:
- Quality control sampling
- Large inventory verification
- Supplier batch validation

### Steps

1. Click **"Batch Processing"** button
2. Dialog appears for multiple file selection
3. Select all IC images to process
4. System processes each image sequentially
5. Summary report generated at end

### Batch Report Contents
- Total images processed
- Authentic count
- Suspect count
- Average confidence score
- Individual results for each image

---

## Exporting Reports

### Export Formats

**JSON (Machine-Readable)**
- Complete data structure
- All extracted information
- Verification details
- Use for: Integration with other systems

**TXT (Human-Readable)**
- Formatted text report
- Easy to read
- Contains all key information
- Use for: Documentation, printing

**PDF (Future)**
- Professional formatted report
- Includes images
- Use for: Presentations, formal documentation

### Export Steps

1. Complete an analysis
2. Click **"Export Report"** button
3. Choose format from dropdown
4. Select save location
5. Enter filename
6. Click **"Save"**

### Report Contents

All formats include:
- Timestamp
- Image information
- Extracted markings
- Official specifications
- Verification results
- Confidence score
- Anomalies (if any)
- Recommendation

---

## Tips & Best Practices

### Getting Best Results

**Image Capture:**
- Use tripod for stability
- Consistent lighting setup
- White or neutral background
- Fill frame with IC (but not too close)
- Focus on the markings

**Lighting:**
- Diffuse, even lighting
- Avoid harsh shadows
- Prevent reflections
- Use ring light or lightbox if possible

**Camera Settings:**
- Macro mode enabled
- Highest resolution
- Lowest ISO (for less noise)
- Fast shutter speed (prevent blur)

**Image Quality:**
- Sharp focus essential
- Good contrast
- No motion blur
- No glare on IC surface

### When to Use Each OCR Method

**Use Ensemble when:**
- Critical verification required
- Time is not a constraint
- Marking is challenging to read
- Maximum accuracy needed

**Use EasyOCR when:**
- Markings at odd angles
- Unusual or decorative fonts
- Poor lighting conditions
- Partially obscured text

**Use PaddleOCR when:**
- Standard IC markings
- Good image quality
- Speed is important
- Clear, printed text

**Use Tesseract when:**
- Traditional printed fonts
- High contrast markings
- Standard orientation
- Simple text layout

### Improving Accuracy

1. **Multiple Angles**: Capture same IC from different angles
2. **Different Lighting**: Try various lighting conditions
3. **Image Enhancement**: Pre-process images externally if needed
4. **OCR Comparison**: Run same image with different OCR methods
5. **Manual Verification**: Always verify critical components manually

### Common Issues & Solutions

**Issue: OCR extracts incorrect text**
- Solution: Try different OCR method
- Solution: Improve image quality
- Solution: Clean IC surface before imaging

**Issue: IC not detected**
- Solution: Ensure IC occupies significant portion of image
- Solution: Improve contrast between IC and background
- Solution: Check image is in focus

**Issue: Low confidence despite good markings**
- Solution: Datasheet might not be found online
- Solution: Verify part number format is correct
- Solution: Check if manufacturer is in database

**Issue: Slow processing**
- Solution: Disable unnecessary debug options
- Solution: Reduce image resolution
- Solution: Use single OCR method instead of ensemble

### Quality Control Workflow

**Recommended Process:**

1. **Sample Selection**
   - Select representative samples per lot
   - Include edge cases

2. **Image Capture**
   - Standardized setup
   - Consistent conditions
   - Multiple angles if needed

3. **Analysis**
   - Use ensemble OCR for critical components
   - Enable debug for first samples
   - Batch process similar components

4. **Review**
   - Check high confidence authentics quickly
   - Thoroughly review medium confidence
   - Reject low confidence

5. **Documentation**
   - Export reports for all rejects
   - Keep database for trending
   - Review statistics periodically

6. **Escalation**
   - Physical inspection for suspects
   - Additional testing (X-ray, electrical)
   - Supplier notification if patterns emerge

---

## Keyboard Shortcuts

(Future feature - to be implemented)

- `Ctrl+O`: Open image
- `Ctrl+A`: Analyze
- `Ctrl+E`: Export report
- `Ctrl+H`: View history
- `F5`: Refresh
- `Esc`: Cancel analysis

---

## Support

If you need help:
1. Check this User Guide
2. Review README.md for technical details
3. Run test_system.py to verify installation
4. Check debug layers to understand processing
5. Review example_usage.py for code examples

---

**Happy IC Authentication! 🔍🔬✓**
