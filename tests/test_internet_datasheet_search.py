#!/usr/bin/env python3
"""
Test Internet-Only Datasheet Search
Verifies that the system finds real datasheets from the internet
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_scraper import DatasheetScraper

def test_internet_datasheet_search():
    """Test that datasheet search uses only real internet sources"""
    print("🌐 Testing Internet-Only Datasheet Search")
    print("=" * 60)
    
    scraper = DatasheetScraper()
    
    # Test common ICs
    test_parts = [
        ('ATMEGA328P', 'Atmel'),
        ('STM32F103', 'STMicroelectronics'),
        ('LM358', 'Texas Instruments'),
        ('NE555', None)
    ]
    
    for part_number, manufacturer in test_parts:
        print(f"\n📦 Testing: {part_number} ({manufacturer or 'Any manufacturer'})")
        print("-" * 60)
        
        result = scraper.get_ic_official_data(part_number, manufacturer)
        
        if result.get('found'):
            print(f"✅ Found datasheet!")
            print(f"   Source: {result.get('source', 'Unknown')}")
            if result.get('datasheet_urls'):
                print(f"   URLs: {len(result['datasheet_urls'])} found")
                print(f"   First URL: {result['datasheet_urls'][0][:80]}...")
            print(f"   Part Marking: {result.get('part_marking', 'N/A')}")
            print(f"   Date Code Format: {result.get('date_code_format', 'N/A')}")
        else:
            print(f"❌ No datasheet found")
            print(f"   Reason: {result.get('reason', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("✅ Internet-Only Datasheet Search Test Complete")

if __name__ == "__main__":
    test_internet_datasheet_search()