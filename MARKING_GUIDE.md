# IC Marking Interpretation Guide

## Overview
This guide helps understand how IC markings are structured and how the system extracts information from them.

---

## Common IC Marking Structure

### Typical Layout (3 Lines)
```
LINE 1: MANUFACTURER_CODE + PART_NUMBER + PACKAGE_TYPE
LINE 2: DATE_CODE + COUNTRY_CODE + ADDITIONAL_INFO  
LINE 3: LOT_CODE or TRACE_CODE
```

### Example: Cypress IC
```
CY8C29666-24PVXI    ← Part Number with Package
B05 PHI 2007        ← Date Code, Country, Year
CYP 606541          ← Lot/Trace Code
```

**Breakdown:**
- `CY8C29666-24PVXI`:
  - `CY` = Cypress manufacturer code
  - `8C29666` = Base part number
  - `24PVXI` = Package type (24-pin PVXI package)
  
- `B05 PHI 2007`:
  - `B05` = Date code (Assembly week/batch 05)
  - `PHI` = Philippines (country of origin)
  - `2007` = Year of manufacture
  
- `CYP 606541`:
  - `CYP` = Cypress manufacturer prefix
  - `606541` = Lot/trace code for quality tracking

---

## Manufacturer Codes

### Common Prefixes
| Code | Manufacturer |
|------|-------------|
| CY, CYPRESS | Cypress Semiconductor |
| TI | Texas Instruments |
| ST, STM | STMicroelectronics |
| AD, ADI | Analog Devices |
| MAX | Maxim Integrated |
| NXP | NXP Semiconductors |
| IFX | Infineon Technologies |
| MCHP, ATMEL | Microchip Technology |
| ON | ON Semiconductor |

### Examples:
- `CY8C29666` - Cypress PSoC microcontroller
- `TL072CP` - Texas Instruments op-amp
- `STM32F103` - STMicroelectronics ARM microcontroller
- `AD8232` - Analog Devices heart rate monitor IC

---

## Part Number Formats

### Format 1: Prefix + Numbers + Package
**Pattern:** `[LETTERS][DIGITS][LETTERS]`
- Example: `LM358N`
  - `LM` = Linear Monolithic (TI series)
  - `358` = Part number
  - `N` = DIP package

### Format 2: Letter + Number + Letter + Number + Suffix
**Pattern:** `[L][N][L][N]-[SUFFIX]`
- Example: `CY8C29666-24PVXI`
  - `CY` = Cypress
  - `8C` = Product family (PSoC)
  - `29666` = Specific model
  - `24PVXI` = 24-pin package, XI temperature grade

### Format 3: Number + Letter + Number
**Pattern:** `[DIGITS][LETTERS][DIGITS]`
- Example: `74HC595`
  - `74` = 7400 series logic
  - `HC` = High-speed CMOS
  - `595` = Shift register type

### Format 4: Manufacturer + Dash + Number
**Pattern:** `[LETTERS]-[DIGITS]`
- Example: `MAX-3232`
  - `MAX` = Maxim
  - `3232` = RS-232 transceiver

---

## Date Codes

### Common Formats

#### Year + Week (YYWW)
- Format: `2007` or `0705`
- Example: `0705` = Week 5 of 2007

#### Letter + Week (LWW)
- Format: `B05`
- Example: `B05` = Batch B, Week 05

#### Year + Month + Day (YYMMDD)
- Format: `070523`
- Example: `070523` = May 23, 2007

#### Full Year
- Format: `2007`
- Example: `2007` = Manufactured in 2007

### Dating System Notes:
- **Week Numbers:** 01-52 (week of the year)
- **Batch Letters:** A-Z (production batch identifier)
- **Old ICs:** May only show 2-digit year (07 = 2007)
- **Very Old ICs:** May use Julian date (day of year)

---

## Country of Origin Codes

### Common Codes
| Code | Country |
|------|---------|
| PHI, PHL | Philippines |
| CHN, PRC | China |
| TWN, ROC | Taiwan |
| MYS | Malaysia |
| THA | Thailand |
| KOR | Korea |
| JPN | Japan |
| USA, US | United States |
| DEU | Germany |
| MEX | Mexico |

### Examples in Context:
- `B05 PHI 2007` - Philippines, 2007
- `07W52 CHN` - China, Week 52 of 2007
- `MYS 0830` - Malaysia, Week 30 of 2008

---

## Lot/Trace Codes

### Purpose
Track manufacturing batches for quality control and recall purposes.

### Common Formats

#### Manufacturer Prefix + Number
- Format: `CYP 606541`
- `CYP` = Cypress prefix
- `606541` = Unique lot number

#### LOT + Alphanumeric
- Format: `LOT: A12345`
- `A12345` = Lot identifier

#### Letter + Numbers
- Format: `L123456`
- Single letter followed by 5-6 digits

### Notes:
- Lot codes are often on separate line
- May include spaces (e.g., `CYP 606541`)
- Used for traceability in case of defects
- Usually unique per production batch

---

## Package Type Codes (Suffix)

### Common Package Codes
| Code | Package Type | Description |
|------|-------------|-------------|
| N | DIP | Dual In-line Package |
| D, SO | SOIC | Small Outline IC |
| P, TSSOP | TSSOP | Thin Shrink Small Outline |
| PV, PVXI | SSOP | Shrink Small Outline (Xi = extended temp) |
| QFP | QFP | Quad Flat Package |
| BGA | BGA | Ball Grid Array |
| CSP | CSP | Chip Scale Package |

### Temperature Grades
| Code | Range | Description |
|------|-------|-------------|
| C | 0°C to +70°C | Commercial |
| I | -40°C to +85°C | Industrial |
| XI, E | -40°C to +125°C | Extended Industrial |
| M | -55°C to +125°C | Military |

### Example: `CY8C29666-24PVXI`
- `24` = 24 pins
- `PV` = SSOP package
- `XI` = Extended industrial temperature range

---

## How the System Extracts Markings

### Step 1: Image Processing
1. Convert to grayscale
2. Denoise and enhance contrast (CLAHE)
3. Detect IC region boundaries
4. Extract text regions

### Step 2: OCR Extraction
1. Apply multiple OCR engines (EasyOCR, PaddleOCR, Tesseract)
2. Sort text by Y-coordinate to preserve line structure
3. Group text on same horizontal line
4. Combine results from all engines

### Step 3: Pattern Matching
1. **Part Number:** Look for alphanumeric with hyphens (e.g., `CY8C29666-24PVXI`)
2. **Manufacturer:** Match against known prefixes (e.g., `CY` → Cypress)
3. **Date Code:** Extract year or week numbers (e.g., `2007`, `B05`)
4. **Country:** Match against known codes (e.g., `PHI` → Philippines)
5. **Lot Code:** Find manufacturer prefix + numbers (e.g., `CYP 606541`)

### Step 4: Verification
1. Search online datasheets for official marking format
2. Compare extracted markings with official specifications
3. Calculate confidence scores based on:
   - Part number match (30%)
   - Manufacturer ID (20%)
   - Date code validity (15%)
   - Country code (10%)
   - Print quality (15%)
   - Marking format (10%)

---

## OCR Common Errors and Corrections

### Character Confusion
| OCR Reads | Actually Is | Context |
|-----------|-------------|---------|
| O (letter) | 0 (zero) | In numbers: `CY8C29666` not `CY8C29O66` |
| l (L) | 1 (one) | In numbers: `606541` not `6065l1` |
| I (i) | 1 (one) | In numbers: `24PVXI` has letter I at end |
| S | 5 | In numbers: `0S` → `05` |
| Z | 2 | In numbers: `Z007` → `2007` |
| B | 8 | In part numbers: Depends on context |

### System Auto-Corrections
The system automatically applies these corrections when extracting part numbers:
- Replaces `O` with `0` in numeric contexts
- Replaces `l` with `1` in numeric contexts
- Preserves `I` in package codes (e.g., `PVXI`)

### Example Correction:
**OCR Output:** `CY8C29666-Z4PVII`  
**System Corrects To:** `CY8C29666-24PVXI`
- `Z4` → `24` (Z confused with 2)
- `II` → `XI` (I confused with 1, but XI is valid package code)

---

## Interpreting System Results

### Extracted Markings Display
```
EXTRACTED MARKINGS
--------------------------------------------------------------------------------
Raw Text: CY8C29666-24PVXI B05 PHI 2007 CYP 606541
Lines: ['CY8C29666-24PVXI', 'B05 PHI 2007', 'CYP 606541']
Manufacturer: Cypress
Part Number: CY8C29666-24PVXI
Date Code: 2007
Lot Code: CYP 606541
Country Of Origin: PHILIPPINES
Additional Codes: ['B05']
```

### Understanding Confidence Scores

#### High Confidence (80-100%)
- All major fields extracted correctly
- Part number matches official datasheet
- Manufacturer identified
- Date code valid
- Good print quality

#### Medium Confidence (50-79%)
- Part number extracted but some uncertainty
- Manufacturer identified
- Some fields missing (lot code, country)
- Moderate print quality

#### Low Confidence (0-49%)
- Part number uncertain or not found
- Manufacturer not identified
- Multiple fields missing
- Poor print quality or OCR errors

### Red Flags for Counterfeits
1. **Part number doesn't match any datasheet**
2. **Manufacturer code inconsistent**
3. **Invalid date format**
4. **Country code doesn't match known manufacturing locations**
5. **Print quality significantly worse than genuine**
6. **Marking format doesn't match OEM specifications**

---

## Tips for Better Accuracy

### Image Quality
1. **Resolution:** Minimum 1280x960, higher is better
2. **Focus:** Sharp focus on IC markings
3. **Lighting:** Even, diffuse lighting (avoid glare)
4. **Angle:** Perpendicular to IC surface
5. **Cleanliness:** Clean IC surface before imaging

### OCR Method Selection
- **Ensemble:** Most accurate, combines all methods (slowest)
- **EasyOCR:** Best for difficult/faded text
- **PaddleOCR:** Fast and accurate for good quality images
- **Tesseract:** Good for standard fonts and high contrast

### Dealing with Poor Results
1. **Try different OCR method** - Each engine has strengths
2. **Improve lighting** - Add diffused light source
3. **Increase resolution** - Use higher camera resolution
4. **Clean the IC** - Remove dust/oxidation
5. **Check debug layers** - Review "Enhanced" and "Text Segmentation" tabs

---

## Examples from Common Manufacturers

### Cypress PSoC
```
CY8C29666-24PVXI
B05 PHI 2007
CYP 606541
```
- Part: PSoC programmable system-on-chip
- Package: 24-pin SSOP, extended temp
- Made: Week 05, 2007, Philippines

### Texas Instruments Op-Amp
```
TL072CP
0730 MYS
```
- Part: Dual JFET op-amp
- Package: DIP
- Made: Week 30, 2007, Malaysia

### STM32 Microcontroller
```
STM32F103C8T6
CHN 1845
ARM
```
- Part: ARM Cortex-M3 MCU
- Package: LQFP48
- Made: Week 45, 2018, China

---

## Verification Process

### What the System Checks

#### 1. Part Number Verification (30% weight)
- Searches online datasheets
- Compares extracted number with official specs
- Checks for known part number formats

#### 2. Manufacturer Identification (20% weight)
- Matches manufacturer code
- Verifies code is consistent with part number
- Checks manufacturer still produces this part

#### 3. Date Code Validation (15% weight)
- Checks date format is valid
- Verifies year is reasonable (not future)
- Checks if part was produced in that timeframe

#### 4. Country Verification (10% weight)
- Checks if manufacturer produces in that country
- Verifies country code is valid
- Cross-references with known production locations

#### 5. Print Quality (15% weight)
- Measures sharpness and contrast
- Detects laser vs. ink marking
- Checks for consistent font

#### 6. Marking Format (10% weight)
- Compares layout with official specifications
- Checks line structure
- Verifies all expected fields present

### Final Authentication
**Authentic:** Confidence ≥ 70%, no critical anomalies  
**Suspect:** Confidence 40-69%, some anomalies  
**Counterfeit:** Confidence < 40%, multiple critical issues

---

## Troubleshooting Extraction Issues

### Issue: Part Number Not Detected
**Solution:**
- Check "Debug Layers" tab → "Text Segmentation"
- Improve image contrast
- Try different OCR method
- Manually verify text is visible in "Enhanced" layer

### Issue: Wrong Manufacturer Detected
**Solution:**
- Verify manufacturer code in first line
- Check if multiple manufacturers use similar codes
- Review original image for clarity

### Issue: Date Code Missing
**Solution:**
- Date might be on separate line
- Check raw OCR text for numbers
- Some old ICs don't have date codes

### Issue: Low Confidence Score
**Solution:**
- Improve image quality (lighting, focus)
- Clean IC surface
- Try Ensemble OCR method
- Verify internet connection (for datasheet lookup)

---

**Last Updated:** October 7, 2025  
**System Version:** 1.0.0
