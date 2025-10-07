"""Test ATMEGA328P manufacturer identification"""

from marking_validator import ManufacturerMarkingValidator

v = ManufacturerMarkingValidator()

print('Testing ATMEGA328P manufacturer identification:')
print('='*60)

r1 = v.validate_markings('ATMEGA328P', ['1004'], 'AMEL')
print(f'With AMEL logo: Manufacturer = {r1["manufacturer"]}')

r2 = v.validate_markings('ATMEGA328P', ['1004'], 'ATMEL')
print(f'With ATMEL logo: Manufacturer = {r2["manufacturer"]}')

r3 = v.validate_markings('ATMEGA328P', ['1004'], '')
print(f'No logo: Manufacturer = {r3["manufacturer"]}')
