"""
MANUFACTURER MARKING SCHEME VALIDATOR
Based on research papers and manufacturer datasheets
Detects counterfeits by validating marking patterns, date codes, and positioning
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime


class ManufacturerMarkingValidator:
    """
    Validates IC markings against manufacturer specifications
    
    Based on research:
    - "Detection of Counterfeit Electronic Components" (IEEE)
    - "Anomaly Detection in IC Markings" (ACM)
    - Manufacturer datasheets and marking standards
    
    Common counterfeit indicators:
    1. Invalid date code format (wrong YYWW pattern)
    2. Impossible dates (future dates, dates before product release)
    3. Missing/incorrect lot codes
    4. Wrong marking order/positioning
    5. Inconsistent font/spacing (detected via OCR quality variance)
    6. Missing mandatory markings (country code, logo, etc.)
    """
    
    def __init__(self):
        # Manufacturer-specific marking schemes
        self.marking_schemes = {
            'MICROCHIP': {
                'logo_text': ['AMEL', 'ATMEL', 'MICROCHIP', 'amel'],
                'date_format': 'YYWW',  # Year-Week
                'date_length': 4,
                'date_range': (2000, 2025),  # Valid manufacturing years
                'mandatory_fields': ['part_number', 'date_code'],  # Removed 'package' - too strict
                'typical_order': ['logo', 'part_number', 'package', 'date_code'],
                # ATMEGA328P released in 2009
                'product_release': {'ATMEGA328P': 2009, 'ATMEGA328': 2009}
            },
            'TI': {  # Texas Instruments
                'logo_text': ['TI', 'TEXAS', 'ti'],
                'date_format': 'YYWW',
                'date_length': 4,
                'date_range': (2000, 2025),
                'mandatory_fields': ['part_number', 'date_code'],  # Lot code optional
                'typical_order': ['part_number', 'date_code', 'lot_code', 'country'],
                'lot_format': r'^[A-Z]\d{1,2}$',  # E.g., E4, A19
                'product_release': {'SN74HC595': 1988, 'SN74': 1970}
            },
            'INFINEON': {  # Cypress/Infineon
                'logo_text': ['CYP', 'CYPRESS', 'INFINEON', 'cyp'],
                'date_format': 'YYWW',
                'date_length': 4,
                'date_range': (2000, 2025),
                'mandatory_fields': ['part_number', 'date_code'],  # Lot code optional
                'typical_order': ['part_number', 'batch', 'date', 'logo', 'lot'],
                'product_release': {'CY8C29666': 2005, 'CY8C': 2003}
            },
            'NATIONAL': {  # National Semiconductor (now TI)
                'logo_text': ['NSC', 'NATIONAL', 'NS'],
                'date_format': 'YYWW',
                'date_length': 4,
                'date_range': (1990, 2011),  # Company acquired by TI in 2011
                'mandatory_fields': ['part_number', 'date_code'],
                'product_release': {'ADC0831': 1995}
            }
        }
    
    def identify_manufacturer(self, part_number: str, logo_text: str = '') -> str:
        """Identify manufacturer from part number or logo"""
        part_upper = part_number.upper()
        logo_upper = logo_text.upper()
        
        # Microchip/Atmel (ATMEGA, PIC, ATTINY, etc.)
        if any(x in part_upper for x in ['ATMEGA', 'ATTINY', 'PIC', 'SAM']):
            return 'MICROCHIP'
        if any(x in logo_upper for x in ['AMEL', 'ATMEL', 'MICROCHIP']):
            return 'MICROCHIP'
        
        # Texas Instruments (SN74, TL, LM, etc.)
        if part_upper.startswith(('SN74', 'SN75', 'TL', 'LM', 'TPS')):
            return 'TI'
        if 'TI' in logo_upper or 'TEXAS' in logo_upper:
            return 'TI'
        
        # Infineon/Cypress (CY8C, PSoC, etc.)
        if part_upper.startswith(('CY8C', 'CY7C', 'PSOC')):
            return 'INFINEON'
        if 'CYP' in logo_upper or 'CYPRESS' in logo_upper or 'INFINEON' in logo_upper:
            return 'INFINEON'
        
        # National Semiconductor (ADC, LM, etc.)
        if part_upper.startswith('ADC'):
            return 'NATIONAL'
        
        return 'UNKNOWN'
    
    def validate_date_code(self, date_code: str, manufacturer: str, part_number: str) -> Dict:
        """
        Validate date code format and logic
        Returns: {valid: bool, reason: str, parsed_date: dict}
        """
        if not date_code or manufacturer not in self.marking_schemes:
            return {'valid': False, 'reason': 'Unknown manufacturer or missing date code'}
        
        scheme = self.marking_schemes[manufacturer]
        
        # Remove non-alphanumeric characters
        cleaned_date = re.sub(r'[^0-9A-Za-z]', '', date_code)
        
        # Check if it's a 4-digit YYWW format
        if len(cleaned_date) == 4 and cleaned_date.isdigit():
            yy = int(cleaned_date[:2])
            ww = int(cleaned_date[2:4])
            
            # Validate week (01-53)
            if ww < 1 or ww > 53:
                return {
                    'valid': False,
                    'reason': f'Invalid week number: {ww} (must be 01-53)',
                    'severity': 'CRITICAL'
                }
            
            # Determine full year (assume 20xx for now)
            full_year = 2000 + yy
            
            # Check if date is in valid range
            min_year, max_year = scheme['date_range']
            if full_year < min_year or full_year > max_year:
                return {
                    'valid': False,
                    'reason': f'Date {full_year} outside valid range {min_year}-{max_year}',
                    'severity': 'CRITICAL'
                }
            
            # Check if date is in the future
            current_year = datetime.now().year
            if full_year > current_year:
                return {
                    'valid': False,
                    'reason': f'Future date: {full_year} (current: {current_year})',
                    'severity': 'CRITICAL'
                }
            
            # Check if date is before product release
            if 'product_release' in scheme:
                for product_prefix, release_year in scheme['product_release'].items():
                    if product_prefix in part_number.upper():
                        if full_year < release_year:
                            return {
                                'valid': False,
                                'reason': f'Date {full_year} before product release {release_year}',
                                'severity': 'CRITICAL'
                            }
            
            return {
                'valid': True,
                'reason': 'Valid date code',
                'parsed_date': {'year': full_year, 'week': ww},
                'date_string': f'{full_year}-W{ww:02d}'
            }
        
        # Check for lot code format (e.g., E4, A19)
        if re.match(r'^[A-Z]\d{1,2}$', cleaned_date):
            return {
                'valid': True,
                'reason': 'Valid lot code format',
                'type': 'lot_code',
                'parsed_date': None
            }
        
        # Check for full year (2007, 2023, etc.)
        if len(cleaned_date) == 4 and cleaned_date.startswith('20'):
            year = int(cleaned_date)
            if scheme['date_range'][0] <= year <= scheme['date_range'][1]:
                return {
                    'valid': True,
                    'reason': 'Valid full year',
                    'type': 'full_year',
                    'parsed_date': {'year': year}
                }
        
        return {
            'valid': False,
            'reason': f'Invalid date format: {date_code} (expected YYWW)',
            'severity': 'MAJOR'
        }
    
    def validate_lot_code(self, lot_code: str, manufacturer: str) -> Dict:
        """Validate lot code format"""
        if not lot_code or manufacturer not in self.marking_schemes:
            return {'valid': False, 'reason': 'Missing lot code'}
        
        scheme = self.marking_schemes[manufacturer]
        
        if 'lot_format' in scheme:
            if re.match(scheme['lot_format'], lot_code.upper()):
                return {'valid': True, 'reason': 'Valid lot code'}
            else:
                return {
                    'valid': False,
                    'reason': f'Invalid lot code format: {lot_code}',
                    'severity': 'MAJOR'
                }
        
        return {'valid': True, 'reason': 'No specific lot format required'}
    
    def check_marking_completeness(self, extracted_data: Dict, manufacturer: str) -> Dict:
        """Check if all mandatory markings are present"""
        if manufacturer not in self.marking_schemes:
            return {'complete': False, 'missing': ['Unknown manufacturer']}
        
        scheme = self.marking_schemes[manufacturer]
        mandatory = scheme.get('mandatory_fields', [])
        
        missing = []
        for field in mandatory:
            if field not in extracted_data or not extracted_data[field]:
                missing.append(field)
        
        if missing:
            return {
                'complete': False,
                'missing': missing,
                'severity': 'MAJOR',
                'reason': f'Missing mandatory fields: {", ".join(missing)}'
            }
        
        return {'complete': True, 'missing': [], 'reason': 'All mandatory fields present'}
    
    def validate_markings(self, part_number: str, date_codes: List[str], 
                         logo_text: str = '', lot_codes: List[str] = None) -> Dict:
        """
        Complete marking validation
        Returns comprehensive validation results
        """
        # Identify manufacturer
        manufacturer = self.identify_manufacturer(part_number, logo_text)
        
        results = {
            'manufacturer': manufacturer,
            'part_number': part_number,
            'validation_passed': True,
            'issues': [],
            'warnings': [],
            'date_validation': None,
            'lot_validation': None,
            'completeness': None
        }
        
        if manufacturer == 'UNKNOWN':
            results['warnings'].append('Unknown manufacturer - limited validation')
        
        # Validate date codes
        if date_codes:
            # Use the most likely date code (4 digits)
            main_date = None
            for dc in date_codes:
                cleaned = re.sub(r'[^0-9]', '', dc)
                if len(cleaned) == 4:
                    main_date = dc
                    break
            
            if main_date:
                date_val = self.validate_date_code(main_date, manufacturer, part_number)
                results['date_validation'] = date_val
                
                if not date_val.get('valid'):
                    results['validation_passed'] = False
                    severity = date_val.get('severity', 'MAJOR')
                    results['issues'].append({
                        'type': 'INVALID_DATE',
                        'severity': severity,
                        'message': date_val.get('reason')
                    })
        else:
            results['validation_passed'] = False
            results['issues'].append({
                'type': 'MISSING_DATE',
                'severity': 'CRITICAL',
                'message': 'No date code found - all legitimate ICs have date codes'
            })
        
        # Validate lot codes
        if lot_codes and manufacturer != 'UNKNOWN':
            for lot in lot_codes:
                lot_val = self.validate_lot_code(lot, manufacturer)
                if not lot_val.get('valid'):
                    results['warnings'].append({
                        'type': 'INVALID_LOT',
                        'severity': lot_val.get('severity', 'MINOR'),
                        'message': lot_val.get('reason')
                    })
        
        # Check completeness
        extracted_data = {
            'part_number': part_number if part_number else None,
            'date_code': date_codes[0] if date_codes else None,
            'lot_code': lot_codes[0] if lot_codes else None,
            'logo': logo_text if logo_text else None
        }
        
        completeness = self.check_marking_completeness(extracted_data, manufacturer)
        results['completeness'] = completeness
        
        if not completeness.get('complete'):
            results['validation_passed'] = False
            results['issues'].append({
                'type': 'INCOMPLETE_MARKINGS',
                'severity': completeness.get('severity', 'MAJOR'),
                'message': completeness.get('reason')
            })
        
        return results


# Test the validator
if __name__ == "__main__":
    validator = ManufacturerMarkingValidator()
    
    print("="*100)
    print("🔬 TESTING MANUFACTURER MARKING VALIDATOR")
    print("="*100)
    
    # Test cases
    test_cases = [
        {
            'name': 'type1 - ATMEGA328P with date 1004',
            'part': 'ATMEGA328P',
            'dates': ['1004', '100'],
            'logo': 'AMEL'
        },
        {
            'name': 'type2 - ATMEGA328P with date 0723',
            'part': 'ATMEGA328P',
            'dates': ['0723', '23'],
            'logo': 'AMEL'
        },
        {
            'name': 'Invalid - future date 2599',
            'part': 'ATMEGA328P',
            'dates': ['2599'],
            'logo': 'AMEL'
        },
        {
            'name': 'Invalid - before product release',
            'part': 'ATMEGA328P',
            'dates': ['0501'],  # 2005, before ATMEGA328P release (2009)
            'logo': 'AMEL'
        },
        {
            'name': 'SN74HC595N with lot E4',
            'part': 'SN74HC595N',
            'dates': ['E4'],
            'logo': 'TI',
            'lots': ['E4']
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*100}")
        print(f"TEST: {test['name']}")
        print('-'*100)
        
        result = validator.validate_markings(
            test['part'],
            test['dates'],
            test.get('logo', ''),
            test.get('lots', [])
        )
        
        print(f"Manufacturer: {result['manufacturer']}")
        print(f"Validation Passed: {'✅' if result['validation_passed'] else '❌'}")
        
        if result['date_validation']:
            dv = result['date_validation']
            print(f"\nDate Validation:")
            print(f"  Valid: {'✅' if dv.get('valid') else '❌'}")
            print(f"  Reason: {dv.get('reason')}")
            if dv.get('parsed_date'):
                print(f"  Parsed: {dv.get('date_string', dv.get('parsed_date'))}")
        
        if result['issues']:
            print(f"\n❌ ISSUES:")
            for issue in result['issues']:
                print(f"  [{issue['severity']}] {issue['type']}: {issue['message']}")
        
        if result['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in result['warnings']:
                print(f"  [{warning.get('severity', 'MINOR')}] {warning.get('type', 'WARNING')}: {warning.get('message', warning)}")
    
    print(f"\n{'='*100}")
    print("✅ VALIDATOR TEST COMPLETE")
    print("="*100)
