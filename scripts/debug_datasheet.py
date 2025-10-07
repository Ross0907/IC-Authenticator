#!/usr/bin/env python3
"""
Debug the datasheet lookup to see what's happening
"""

from web_scraper import DatasheetScraper

def debug_datasheet_lookup():
    """Debug the datasheet lookup process"""
    print("Debugging Datasheet Lookup")
    print("=" * 40)
    
    scraper = DatasheetScraper()
    
    # Test ATMEGA328P lookup
    print("\\n🔍 Testing ATMEGA328P lookup...")
    result = scraper.search_component_datasheet('ATMEGA328P', 'Atmel')
    
    print(f"Found: {result.get('found', False)}")
    print(f"Part marking: {result.get('part_marking', 'None')}")
    print(f"Date code format: {result.get('date_code_format', 'None')}")
    print(f"Package marking: {result.get('package_marking', 'None')}")
    print(f"Search results: {len(result.get('search_results', []))}")
    
    if result.get('search_results'):
        for i, sr in enumerate(result['search_results'][:2]):
            print(f"  Result {i+1}: {sr.get('source', 'Unknown')} - {sr.get('method', 'Unknown')}")
    
    print("\\n🔍 Testing local database directly...")
    local_result = scraper._search_local_datasheet_db('ATMEGA328P')
    print(f"Local result: {local_result}")

if __name__ == "__main__":
    debug_datasheet_lookup()