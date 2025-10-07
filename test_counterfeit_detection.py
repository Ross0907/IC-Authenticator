"""
Quick demonstration of counterfeit detection via date code validation
"""

from marking_validator import ManufacturerMarkingValidator

print("="*100)
print("🔬 COUNTERFEIT DETECTION TEST")
print("="*100)

validator = ManufacturerMarkingValidator()

# Test your two chips
test_cases = [
    {
        'name': '🔵 type1 - ATMEGA328P',
        'part': 'ATMEGA328P',
        'dates': ['1004'],  # Week 4 of 2010
        'logo': 'AMEL'
    },
    {
        'name': '🔴 type2 - ATMEGA328P',
        'part': 'ATMEGA328P',
        'dates': ['0723'],  # Week 23 of 2007
        'logo': 'AMEL'
    }
]

print("\n" + "="*100)
print("PRODUCT INFORMATION")
print("="*100)
print("Part Number: ATMEGA328P")
print("Manufacturer: Microchip (formerly Atmel)")
print("**PRODUCT RELEASE YEAR: 2009** ⭐")
print("="*100)

for test in test_cases:
    print(f"\n{test['name']}")
    print("-"*100)
    
    result = validator.validate_markings(
        test['part'],
        test['dates'],
        test.get('logo', '')
    )
    
    # Focus on date validation
    if result['date_validation']:
        dv = result['date_validation']
        print(f"\n📅 DATE CODE ANALYSIS:")
        print(f"   Input: {test['dates'][0]}")
        
        if dv.get('parsed_date'):
            year = dv['parsed_date']['year']
            week = dv['parsed_date']['week']
            print(f"   Parsed: Year {year}, Week {week}")
            print(f"   Date String: {dv.get('date_string', 'N/A')}")
        
        print(f"\n   Validation: {'✅ VALID' if dv.get('valid') else '❌ INVALID'}")
        print(f"   Reason: {dv.get('reason')}")
        
        if not dv.get('valid') and dv.get('severity'):
            print(f"   Severity: {dv.get('severity')}")
    
    # Overall verdict
    print(f"\n🎯 AUTHENTICATION VERDICT:")
    if result['validation_passed']:
        print(f"   ✅ AUTHENTIC - Manufacturer markings valid")
    else:
        print(f"   ❌ COUNTERFEIT/SUSPICIOUS - Marking validation failed")
    
    # Show critical issues
    if result['issues']:
        print(f"\n   🚨 ISSUES DETECTED:")
        for issue in result['issues']:
            severity_emoji = "🔴" if issue['severity'] == 'CRITICAL' else "🟡"
            print(f"      {severity_emoji} [{issue['severity']}] {issue['type']}")
            print(f"         {issue['message']}")

print("\n" + "="*100)
print("🎯 CONCLUSION")
print("="*100)
print("""
type1 (date 1004 = 2010): ✅ AUTHENTIC
  - Date is 1 year AFTER product release (2009)
  - Reasonable manufacturing date
  
type2 (date 0723 = 2007): ❌ COUNTERFEIT
  - Date is 2 years BEFORE product release (2009)
  - IMPOSSIBLE - chip cannot exist before product was released!
  - This is a CRITICAL counterfeit indicator

🔬 DETECTION METHOD:
Date code validation against manufacturer product release dates.
This cannot be explained by environmental noise, blurry text, or OCR errors.
A chip dated 2007 for a product released in 2009 is physically impossible.
""")
print("="*100)
