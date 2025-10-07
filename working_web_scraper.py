"""
WORKING Web Scraper - Actually finds datasheets
Tests real web searches to verify part existence
"""

import requests
from bs4 import BeautifulSoup
import re
import time


class WorkingDatasheetScraper:
    """Scraper that actually works by checking real sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 5
    
    def search_octopart(self, part_number: str) -> dict:
        """Search Octopart - most reliable aggregator"""
        try:
            url = f"https://octopart.com/search?q={part_number}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Check if "No results" appears
                if "No results found" not in response.text and "results" in response.text.lower():
                    return {'found': True, 'source': 'octopart', 'url': url}
        except:
            pass
        
        return {'found': False}
    
    def search_alldatasheet(self, part_number: str) -> dict:
        """Search AllDataSheet.com"""
        try:
            # Clean part number for URL
            clean_part = part_number.upper().replace('-', '').replace('_', '')
            url = f"https://www.alldatasheet.com/datasheet-pdf/pdf/1/{clean_part}.html"
            
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code == 200:
                if "404" not in response.text and "not found" not in response.text.lower():
                    return {'found': True, 'source': 'alldatasheet', 'url': url}
        except:
            pass
        
        return {'found': False}
    
    def search_ti_direct(self, part_number: str) -> dict:
        """Search TI directly for SN74 parts"""
        if not part_number.upper().startswith('SN74'):
            return {'found': False}
        
        try:
            # TI uses lowercase part numbers in URLs
            url = f"https://www.ti.com/product/{part_number.lower()}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                if "datasheet" in response.text.lower():
                    return {'found': True, 'source': 'texas_instruments', 'url': url}
        except:
            pass
        
        return {'found': False}
    
    def search_microchip_direct(self, part_number: str) -> dict:
        """Search Microchip directly for ATMEGA parts"""
        if not part_number.upper().startswith('ATMEGA'):
            return {'found': False}
        
        try:
            # Microchip uses specific format
            url = f"https://www.microchip.com/en-us/product/{part_number.upper()}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                if "datasheet" in response.text.lower() or "documentation" in response.text.lower():
                    return {'found': True, 'source': 'microchip', 'url': url}
        except:
            pass
        
        return {'found': False}
    
    def search_infineon_direct(self, part_number: str) -> dict:
        """Search Infineon directly for CY8C parts"""
        if not part_number.upper().startswith('CY8C'):
            return {'found': False}
        
        try:
            # Infineon search
            search_url = f"https://www.infineon.com/cms/en/search.html?intc=searchkeyword#!term={part_number}&view=keyword"
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                # If we get a result page (not 404)
                if part_number.upper() in response.text.upper():
                    return {'found': True, 'source': 'infineon', 'url': search_url}
        except:
            pass
        
        return {'found': False}
    
    def search_datasheetarchive(self, part_number: str) -> dict:
        """Search DatasheetArchive"""
        try:
            search_url = f"https://www.datasheetarchive.com/search?q={part_number}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                if "datasheet" in response.text.lower() and "results" in response.text.lower():
                    return {'found': True, 'source': 'datasheetarchive', 'url': search_url}
        except:
            pass
        
        return {'found': False}
    
    def search_comprehensive(self, part_number: str) -> dict:
        """
        Comprehensive search across all sources
        Returns first successful match
        """
        print(f"\n🔍 Searching for: {part_number}")
        
        # Try manufacturer-specific first (fastest)
        if part_number.upper().startswith('SN74'):
            print("  [TI] Checking Texas Instruments...")
            result = self.search_ti_direct(part_number)
            if result['found']:
                print(f"  ✅ FOUND on TI!")
                return result
        
        if part_number.upper().startswith('ATMEGA'):
            print("  [Microchip] Checking Microchip...")
            result = self.search_microchip_direct(part_number)
            if result['found']:
                print(f"  ✅ FOUND on Microchip!")
                return result
        
        if part_number.upper().startswith('CY8C'):
            print("  [Infineon] Checking Infineon/Cypress...")
            result = self.search_infineon_direct(part_number)
            if result['found']:
                print(f"  ✅ FOUND on Infineon!")
                return result
        
        # Try aggregators
        print("  [Octopart] Checking Octopart...")
        result = self.search_octopart(part_number)
        if result['found']:
            print(f"  ✅ FOUND on Octopart!")
            return result
        
        print("  [AllDatasheet] Checking AllDatasheet...")
        result = self.search_alldatasheet(part_number)
        if result['found']:
            print(f"  ✅ FOUND on AllDatasheet!")
            return result
        
        print("  [Archive] Checking DatasheetArchive...")
        result = self.search_datasheetarchive(part_number)
        if result['found']:
            print(f"  ✅ FOUND on DatasheetArchive!")
            return result
        
        print(f"  ❌ NOT FOUND across all sources")
        return {'found': False}


if __name__ == "__main__":
    # Test on all our parts
    scraper = WorkingDatasheetScraper()
    
    test_parts = [
        "ATMEGA328P",
        "ATMEGAS2BP",  # Should NOT be found (typo)
        "CY8C29666-24PVXI",
        "SN74HC595N",
        "ADC0831CCN",
        "0831CCN"  # Should NOT be found (missing ADC prefix)
    ]
    
    print("="*80)
    print("🧪 TESTING WORKING WEB SCRAPER")
    print("="*80)
    
    for part in test_parts:
        result = scraper.search_comprehensive(part)
        print(f"  Result: {result}\n")
        time.sleep(0.5)  # Be polite to servers
