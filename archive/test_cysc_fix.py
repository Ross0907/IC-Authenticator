"""Quick test for CY8C validation"""

from marking_validator import ManufacturerMarkingValidator

v = ManufacturerMarkingValidator()

print('='*80)
print('=== CY8C29666 with date 2007 (full year - Image 1) ===')
r1 = v.validate_markings('CY8C29666', ['2007'], 'CYP')
print(f'Valid: {r1["validation_passed"]}')
print(f'Manufacturer: {r1["manufacturer"]}')
if r1['date_validation']:
    print(f'Date validation: {r1["date_validation"]}')
if r1['issues']:
    print('Issues:')
    for i in r1['issues']:
        print(f'  {i["severity"]} - {i["message"]}')

print('\n' + '='*80)
print('=== CY8C29666 with date 1025 (YYWW - Image 2) ===')
r2 = v.validate_markings('CY8C29666', ['1025'], 'CYP')
print(f'Valid: {r2["validation_passed"]}')
print(f'Manufacturer: {r2["manufacturer"]}')
if r2['date_validation']:
    print(f'Date validation: {r2["date_validation"]}')
if r2['issues']:
    print('Issues:')
    for i in r2['issues']:
        print(f'  {i["severity"]} - {i["message"]}')
