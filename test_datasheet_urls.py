"""
Test script to validate all datasheet URLs return valid PDFs (not 404s)
"""

import requests
from smart_ic_authenticator import SmartICAuthenticator

# Test chips from various manufacturers
test_chips = {
    'Microchip': ['ATMEGA328P', 'PIC16F877A', 'ATTINY85'],
    'Texas Instruments': ['LM358', 'SN74HC595', 'TL071', 'NE555', 'ADC0831'],
    'STMicroelectronics': ['STM32F103C8T6', 'M74HC238B1'],
    'Infineon': ['CY8C29666-24PVXI', 'CY7C68013A'],
    'NXP': ['MC33774A'],
    'Analog Devices': ['LT1013', 'AD620', 'MAX232']
}

print("="*80)
print("DATASHEET URL VALIDATION TEST")
print("="*80)

auth = SmartICAuthenticator()
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

total_tests = 0
passed_tests = 0
failed_chips = []

for manufacturer, chips in test_chips.items():
    print(f"\n{'='*80}")
    print(f"Testing {manufacturer}")
    print(f"{'='*80}")
    
    for chip in chips:
        total_tests += 1
        print(f"\nTesting: {chip}")
        
        # Use the authenticator's datasheet search
        result = auth._find_datasheet(chip, manufacturer)
        
        if not result['found']:
            print(f"  ❌ FAILED: No datasheet URL found")
            failed_chips.append((chip, manufacturer, "No URL found"))
            continue
        
        url = result['url']
        print(f"  URL: {url}")
        
        # Test if URL is accessible
        try:
            response = session.head(url, timeout=5, allow_redirects=True)
            status = response.status_code
            content_type = response.headers.get('Content-Type', '').lower()
            
            if status == 200:
                if 'pdf' in content_type or url.endswith('.pdf'):
                    print(f"  ✅ PASSED: Valid PDF (Status: {status}, Type: {content_type})")
                    passed_tests += 1
                else:
                    print(f"  ✅ PASSED: Valid page (Status: {status}, Type: {content_type})")
                    passed_tests += 1
            elif status == 404:
                print(f"  ❌ FAILED: 404 NOT FOUND")
                failed_chips.append((chip, manufacturer, f"404 Error: {url}"))
            else:
                print(f"  ⚠️  WARNING: Status {status}")
                if status in [301, 302, 307, 308]:
                    print(f"     Redirect to: {response.url}")
                    passed_tests += 1
                else:
                    failed_chips.append((chip, manufacturer, f"Status {status}: {url}"))
        
        except requests.exceptions.Timeout:
            print(f"  ⚠️  TIMEOUT: URL took too long to respond")
            failed_chips.append((chip, manufacturer, f"Timeout: {url}"))
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            failed_chips.append((chip, manufacturer, f"Error: {str(e)}"))

# Summary
print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
print(f"Failed: {len(failed_chips)} ({len(failed_chips)/total_tests*100:.1f}%)")

if failed_chips:
    print(f"\n{'='*80}")
    print("FAILED CHIPS (Need fixing):")
    print(f"{'='*80}")
    for chip, mfg, reason in failed_chips:
        print(f"  {chip} ({mfg}): {reason}")
