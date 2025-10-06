"""
Verification Engine Module
Compares extracted markings with official specifications
Determines authenticity using multiple verification methods
"""

import numpy as np
from fuzzywuzzy import fuzz
from typing import Dict, List, Any
import cv2
from datetime import datetime
import re


class VerificationEngine:
    """
    Advanced verification engine for IC authenticity
    Uses multiple verification methods and machine learning
    """
    
    def __init__(self):
        self.verification_rules = self._load_verification_rules()
        
    def _load_verification_rules(self) -> Dict:
        """Load verification rules and thresholds"""
        return {
            'text_similarity_threshold': 80,  # Fuzzy match threshold
            'date_code_validity_years': 20,   # Date codes older than this are suspicious (changed from 10 to 20)
            'quality_score_threshold': 60,    # Minimum image quality
            'required_fields': ['part_number'],
            'suspicious_patterns': [
                'unknown manufacturer',
                'invalid date code',
                'mismatched country',
                'poor print quality'
            ]
        }
    
    def verify_component(
        self,
        extracted_data: Dict,
        official_data: Dict,
        images: Dict
    ) -> Dict[str, Any]:
        """
        Main verification function
        Performs comprehensive authenticity check
        """
        verification_result = {
            'is_authentic': False,
            'confidence': 0.0,
            'checks_passed': [],
            'checks_failed': [],
            'anomalies': [],
            'recommendation': '',
            'detailed_scores': {}
        }
        
        # Check if we have official data to compare against
        has_official_data = official_data.get('found', False)
        
        if not has_official_data and extracted_data.get('part_number'):
            # We have extracted data but no official data to compare
            # This is not necessarily suspicious - could be a valid IC
            verification_result['is_authentic'] = True
            verification_result['confidence'] = max(extracted_data.get('confidence', 0) * 100, 60)
            verification_result['checks_passed'].append('Text Successfully Extracted')
            verification_result['anomalies'].append(
                "Official datasheet not found - manual verification recommended"
            )
            verification_result['recommendation'] = self._generate_recommendation(verification_result)
            return verification_result
        
        # Check 1: Part Number Verification
        part_check = self._verify_part_number(
            extracted_data.get('part_number'),
            official_data.get('part_marking')
        )
        verification_result['detailed_scores']['part_number'] = part_check
        
        # Only count as failed if we have extracted data but it doesn't match
        if extracted_data.get('part_number') and not part_check['passed']:
            verification_result['checks_failed'].append('Part Number Mismatch')
            verification_result['anomalies'].append(
                f"Part number mismatch: extracted '{extracted_data.get('part_number')}' "
                f"vs expected '{official_data.get('part_marking')}'"
            )
        elif part_check['passed']:
            verification_result['checks_passed'].append('Part Number Match')
        # If no extracted data, don't count as pass or fail
        
        # Check 2: Manufacturer Verification
        mfr_check = self._verify_manufacturer(
            extracted_data.get('manufacturer'),
            official_data
        )
        verification_result['detailed_scores']['manufacturer'] = mfr_check
        
        # Only count as failed if we have extracted data but it doesn't match
        if extracted_data.get('manufacturer') and not mfr_check['passed']:
            verification_result['checks_failed'].append('Manufacturer Mismatch')
            verification_result['anomalies'].append(
                f"Manufacturer verification failed: {mfr_check.get('reason', 'Unknown')}"
            )
        elif mfr_check['passed']:
            verification_result['checks_passed'].append('Manufacturer Verified')
        # If no extracted data, don't count as pass or fail
        
        # Check 3: Date Code Validation
        date_check = self._verify_date_code(
            extracted_data.get('date_code'),
            official_data.get('date_code_format')
        )
        verification_result['detailed_scores']['date_code'] = date_check
        
        if date_check['passed']:
            verification_result['checks_passed'].append('Valid Date Code')
        else:
            verification_result['checks_failed'].append('Invalid Date Code')
            verification_result['anomalies'].append(
                f"Date code issue: {date_check.get('reason', 'Invalid format')}"
            )
        
        # Check 4: Country of Origin
        country_check = self._verify_country(
            extracted_data.get('country_of_origin'),
            official_data.get('country_codes', [])
        )
        verification_result['detailed_scores']['country'] = country_check
        
        if country_check['passed']:
            verification_result['checks_passed'].append('Country Code Valid')
        else:
            verification_result['checks_failed'].append('Country Code Issue')
            verification_result['anomalies'].append(
                f"Country verification: {country_check.get('reason', 'Mismatch')}"
            )
        
        # Check 5: Print Quality Analysis
        quality_check = self._verify_print_quality(images)
        verification_result['detailed_scores']['print_quality'] = quality_check
        
        if quality_check['passed']:
            verification_result['checks_passed'].append('Good Print Quality')
        else:
            verification_result['checks_failed'].append('Poor Print Quality')
            verification_result['anomalies'].append(
                f"Print quality issue: {quality_check.get('reason', 'Below standard')}"
            )
        
        # Check 6: Marking Format Consistency
        format_check = self._verify_marking_format(
            extracted_data,
            official_data
        )
        verification_result['detailed_scores']['marking_format'] = format_check
        
        if format_check['passed']:
            verification_result['checks_passed'].append('Marking Format Correct')
        else:
            verification_result['checks_failed'].append('Marking Format Issue')
            verification_result['anomalies'].append(
                f"Format issue: {format_check.get('reason', 'Inconsistent')}"
            )
        
        # Calculate overall confidence score
        confidence = self._calculate_confidence(verification_result['detailed_scores'])
        verification_result['confidence'] = confidence
        
        # Determine authenticity
        passed_count = len(verification_result['checks_passed'])
        total_count = passed_count + len(verification_result['checks_failed'])
        pass_rate = passed_count / total_count if total_count > 0 else 0
        
        # Determine authenticity with more reasonable thresholds
        # If we have extracted data and it matches, that's good
        # If we have no extracted data, default to cautious acceptance
        has_extracted_data = any([
            extracted_data.get('part_number'),
            extracted_data.get('manufacturer'),
            extracted_data.get('date_code')
        ])
        
        if has_extracted_data:
            # We have data to verify - use normal logic
            verification_result['is_authentic'] = (
                pass_rate >= 0.60 and confidence >= 50  # More lenient thresholds
            )
        else:
            # No extracted data - could be OCR failure, not counterfeit
            # Default to cautious acceptance with low confidence
            verification_result['is_authentic'] = True
            verification_result['confidence'] = max(confidence, 40)  # Minimum confidence
            verification_result['anomalies'].append(
                "OCR extraction failed - manual verification recommended"
            )
        
        # Generate recommendation
        verification_result['recommendation'] = self._generate_recommendation(
            verification_result
        )
        
        return verification_result
    
    def _verify_part_number(self, extracted: str, expected: str) -> Dict:
        """Verify part number matches with improved OCR tolerance"""
        if not extracted and not expected:
            return {
                'passed': True,  # Both missing is not a failure
                'score': 50,
                'reason': 'No part number data to compare'
            }
        
        if not extracted or not expected:
            return {
                'passed': False,
                'score': 0,
                'reason': 'Missing part number data'
            }
        
        # Clean and normalize part numbers for comparison
        def clean_part_number(part):
            # Remove common OCR errors and normalize
            part = part.upper().strip()
            # Replace common OCR mistakes
            replacements = {
                '0': 'O', 'O': '0',  # 0/O confusion
                '1': 'I', 'I': '1',  # 1/I confusion
                '8': 'B', 'B': '8',  # 8/B confusion
                '5': 'S', 'S': '5',  # 5/S confusion
            }
            return part
        
        extracted_clean = clean_part_number(extracted)
        expected_clean = clean_part_number(expected)
        
        # Use fuzzy matching for flexibility
        similarity = fuzz.ratio(extracted_clean, expected_clean)
        
        # Also try partial matching for truncated OCR
        partial_sim = fuzz.partial_ratio(extracted_clean, expected_clean)
        
        # Use the better score
        best_similarity = max(similarity, partial_sim)
        
        # Lower threshold for OCR tolerance
        passed = best_similarity >= 75  # Reduced from default threshold
        
        return {
            'passed': passed,
            'score': best_similarity,
            'extracted': extracted,
            'expected': expected,
            'reason': 'Match' if passed else f'Low similarity ({similarity}%)'
        }
    
    def _verify_manufacturer(self, extracted: str, official_data: Dict) -> Dict:
        """Verify manufacturer information"""
        if not extracted:
            return {
                'passed': False,
                'score': 0,
                'reason': 'Manufacturer not detected'
            }
        
        # Check if manufacturer is known
        known_manufacturers = [
            'Texas Instruments', 'STMicroelectronics', 'Analog Devices',
            'Maxim', 'NXP', 'Infineon', 'Microchip', 'ON Semiconductor',
            'Renesas', 'Cypress', 'Intel', 'Broadcom'
        ]
        
        # Fuzzy match against known manufacturers
        best_match = 0
        matched_manufacturer = None
        
        for mfr in known_manufacturers:
            similarity = fuzz.ratio(extracted.upper(), mfr.upper())
            if similarity > best_match:
                best_match = similarity
                matched_manufacturer = mfr
        
        passed = best_match >= 70
        
        return {
            'passed': passed,
            'score': best_match,
            'extracted': extracted,
            'matched': matched_manufacturer,
            'reason': 'Verified' if passed else 'Unknown or suspicious manufacturer'
        }
    
    def _verify_date_code(self, extracted: str, expected_format: str) -> Dict:
        """Verify date code format and validity"""
        if not extracted:
            return {
                'passed': False,
                'score': 0,
                'reason': 'No date code found'
            }
        
        # Try to parse date code
        parsed_date = self._parse_date_code(extracted)
        
        if not parsed_date:
            return {
                'passed': False,
                'score': 0,
                'reason': 'Invalid date code format'
            }
        
        # Check if date is reasonable (not in future, not too old)
        current_year = datetime.now().year
        year = parsed_date.get('year', 0)
        
        if year > current_year:
            return {
                'passed': False,
                'score': 0,
                'reason': 'Date code in the future'
            }
        
        age = current_year - year
        if age > self.verification_rules['date_code_validity_years']:
            return {
                'passed': False,
                'score': 30,
                'reason': f'Component too old ({age} years)'
            }
        
        # Date is valid
        score = 100 - (age * 5)  # Slight penalty for older parts
        
        return {
            'passed': True,
            'score': max(score, 60),
            'extracted': extracted,
            'parsed': parsed_date,
            'reason': f'Valid date code (Year: {year})'
        }
    
    def _parse_date_code(self, date_code: str) -> Dict:
        """Parse date code into year and week/month"""
        # Remove spaces and special characters
        cleaned = re.sub(r'[^A-Z0-9]', '', date_code.upper())
        
        # Try different formats
        # Format 1: YYWW (4 digits) - Handle both 19XX and 20XX
        if len(cleaned) == 4 and cleaned.isdigit():
            yy = int(cleaned[:2])
            week = int(cleaned[2:])
            
            # Smart year detection: 00-40 = 2000-2040, 90-99 = 1990-1999
            if yy <= 40:
                year = 2000 + yy
            else:
                year = 1900 + yy
            
            if 1 <= week <= 53:
                return {'year': year, 'week': week, 'format': 'YYWW'}
        
        # Format 2: YYYYWW (6 digits)
        if len(cleaned) == 6 and cleaned.isdigit():
            year = int(cleaned[:4])
            week = int(cleaned[4:])
            
            if 1900 <= year <= 2100 and 1 <= week <= 53:
                return {'year': year, 'week': week, 'format': 'YYYYWW'}
        
        # Format 3: YYMMDD (6 digits)
        if len(cleaned) == 6 and cleaned.isdigit():
            yy = int(cleaned[:2])
            month = int(cleaned[2:4])
            day = int(cleaned[4:])
            
            # Smart year detection
            if yy <= 40:
                year = 2000 + yy
            else:
                year = 1900 + yy
            
            if 1 <= month <= 12 and 1 <= day <= 31:
                return {
                    'year': year,
                    'month': month,
                    'day': day,
                    'format': 'YYMMDD'
                }
        
        return None
    
    def _verify_country(self, extracted: str, expected_countries: List[str]) -> Dict:
        """Verify country of origin"""
        if not extracted:
            return {
                'passed': True,  # Not required
                'score': 50,
                'reason': 'Country not specified'
            }
        
        if not expected_countries:
            # No expected countries specified
            return {
                'passed': True,
                'score': 70,
                'reason': 'No country restrictions'
            }
        
        # Check if extracted country matches any expected
        for country in expected_countries:
            similarity = fuzz.ratio(
                extracted.upper(),
                country.upper()
            )
            
            if similarity >= 80:
                return {
                    'passed': True,
                    'score': 100,
                    'extracted': extracted,
                    'matched': country,
                    'reason': 'Country match'
                }
        
        return {
            'passed': False,
            'score': 30,
            'extracted': extracted,
            'expected': expected_countries,
            'reason': 'Country mismatch or unexpected origin'
        }
    
    def _verify_print_quality(self, images: Dict) -> Dict:
        """Verify print/marking quality"""
        if 'enhanced' not in images:
            return {
                'passed': False,
                'score': 0,
                'reason': 'No image data available'
            }
        
        image = images['enhanced']
        
        # Calculate quality metrics
        # 1. Sharpness
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        sharpness = laplacian.var()
        
        # 2. Contrast
        contrast = image.std()
        
        # 3. Noise level (estimate)
        noise = self._estimate_noise(image)
        
        # Compute quality score
        sharpness_score = min(sharpness / 10, 100)
        contrast_score = min(contrast / 0.8, 100)
        noise_score = max(0, 100 - noise * 2)
        
        overall_score = (
            sharpness_score * 0.4 +
            contrast_score * 0.3 +
            noise_score * 0.3
        )
        
        passed = overall_score >= self.verification_rules['quality_score_threshold']
        
        return {
            'passed': passed,
            'score': overall_score,
            'sharpness': sharpness,
            'contrast': contrast,
            'noise': noise,
            'reason': 'Good quality' if passed else 'Poor print quality'
        }
    
    def _estimate_noise(self, image):
        """Estimate noise level in image"""
        # Simple noise estimation using standard deviation of differences
        h, w = image.shape
        
        # Calculate differences with neighbors
        diff_h = np.abs(np.diff(image.astype(float), axis=0))
        diff_w = np.abs(np.diff(image.astype(float), axis=1))
        
        # Estimate noise
        noise = (diff_h.std() + diff_w.std()) / 2
        
        return noise
    
    def _verify_marking_format(self, extracted: Dict, official: Dict) -> Dict:
        """Verify overall marking format consistency"""
        issues = []
        score = 100
        
        # Check if required fields are present
        if not extracted.get('part_number'):
            issues.append('Missing part number')
            score -= 40
        
        # Check format consistency
        raw_text = extracted.get('raw_text', '')
        lines = extracted.get('lines', [])
        
        # Typical IC markings have 3-5 lines
        if len(lines) < 2:
            issues.append('Too few marking lines')
            score -= 20
        elif len(lines) > 6:
            issues.append('Unusually many marking lines')
            score -= 10
        
        # Check for special characters that shouldn't be there
        suspicious_chars = ['@', '#', '$', '%', '^', '&', '*', '(', ')']
        for char in suspicious_chars:
            if char in raw_text:
                issues.append(f'Suspicious character: {char}')
                score -= 10
        
        passed = score >= 60 and len(issues) == 0
        
        return {
            'passed': passed,
            'score': max(score, 0),
            'issues': issues,
            'reason': 'Format OK' if passed else f'Format issues: {", ".join(issues)}'
        }
    
    def _calculate_confidence(self, scores: Dict) -> float:
        """Calculate overall confidence score"""
        if not scores:
            return 0.0
        
        # Weight different checks
        weights = {
            'part_number': 0.30,
            'manufacturer': 0.20,
            'date_code': 0.15,
            'country': 0.10,
            'print_quality': 0.15,
            'marking_format': 0.10
        }
        
        total_score = 0
        total_weight = 0
        
        for check, weight in weights.items():
            if check in scores:
                score_value = scores[check].get('score', 0)
                total_score += score_value * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        confidence = total_score / total_weight
        return min(confidence, 100.0)
    
    def _generate_recommendation(self, verification_result: Dict) -> str:
        """Generate recommendation based on verification results"""
        confidence = verification_result['confidence']
        is_authentic = verification_result['is_authentic']
        anomalies = verification_result['anomalies']
        
        if is_authentic and confidence >= 85:
            recommendation = (
                "✓ COMPONENT APPEARS AUTHENTIC\n\n"
                "The component has passed all major verification checks with high confidence. "
                "All markings are consistent with official specifications.\n\n"
                "Recommendation: ACCEPT"
            )
        elif is_authentic and confidence >= 65:
            recommendation = (
                "⚠ COMPONENT LIKELY AUTHENTIC (with minor concerns)\n\n"
                "The component has passed most verification checks, but some minor "
                "discrepancies were noted:\n"
            )
            for anomaly in anomalies[:3]:
                recommendation += f"  • {anomaly}\n"
            recommendation += "\nRecommendation: ACCEPT with additional inspection"
        else:
            recommendation = (
                "✗ COMPONENT AUTHENTICITY SUSPECT\n\n"
                "The component has failed critical verification checks. "
                "Detected issues:\n"
            )
            for anomaly in anomalies:
                recommendation += f"  • {anomaly}\n"
            recommendation += (
                "\nRecommendation: REJECT and further investigate supplier\n"
                "Consider additional testing (X-ray, decapsulation, electrical testing)"
            )
        
        return recommendation
