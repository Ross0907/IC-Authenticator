"""
Dynamic Web Scraper for Datasheets and Manufacturer Information
No hardcoded part numbers - works with any IC
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, Optional
import json
from urllib.parse import quote


class WorkingDatasheetScraper:
    """Universal datasheet scraper - works for any IC part number"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        self.timeout = 10
        
        # Dynamic manufacturer detection patterns
        self.manufacturer_patterns = {
            r'^SN7\d': 'Texas Instruments',
            r'^TI\d': 'Texas Instruments',
            r'^TPS\d': 'Texas Instruments',
            r'^LM\d': 'Texas Instruments',
            r'^ATMEGA': 'Microchip',
            r'^ATTINY': 'Microchip',
            r'^PIC\d': 'Microchip',
            r'^CY8C': 'Infineon/Cypress',
            r'^STM32': 'STMicroelectronics',
            r'^STM\d': 'STMicroelectronics',
            r'^NRF\d': 'Nordic Semiconductor',
            r'^MAX\d': 'Maxim/Analog Devices',
            r'^ADC\d': 'Various Manufacturers',
            r'^LTC\d': 'Analog Devices',
            r'^AD\d{3,}': 'Analog Devices',
            r'^74\w+': 'Various Manufacturers',
        }
    
    def detect_manufacturer(self, part_number: str) -> Optional[str]:
        """Dynamically detect manufacturer from part number pattern"""
        part_upper = part_number.upper().strip()
        
        for pattern, manufacturer in self.manufacturer_patterns.items():
            if re.match(pattern, part_upper):
                return manufacturer
        
        return "Unknown Manufacturer"
    
    def clean_part_number(self, part_number: str) -> str:
        """Clean part number for searching"""
        return part_number.strip().replace(' ', '').replace('_', '-')
    
    def search_octopart(self, part_number: str) -> dict:
        """Search Octopart - most reliable aggregator"""
        try:
            url = f"https://octopart.com/search?q={quote(part_number)}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Check for actual results
                if soup.find_all('div', class_='card') or 'part-result' in response.text.lower():
                    manufacturer = self.detect_manufacturer(part_number)
                    return {
                        'found': True, 
                        'source': 'Octopart', 
                        'url': url,
                        'manufacturer': manufacturer,
                        'confidence': 'high'
                    }
        except Exception as e:
            print(f"  [Octopart Error]: {str(e)}")
        
        return {'found': False}
    
    def search_alldatasheet(self, part_number: str) -> dict:
        """Search AllDataSheet.com"""
        try:
            # Use search instead of direct URL
            search_url = f"https://www.alldatasheet.com/datasheet-pdf/search/search.html?search={quote(part_number)}"
            response = self.session.get(search_url, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code == 200:
                if "datasheet" in response.text.lower() and "404" not in response.text:
                    manufacturer = self.detect_manufacturer(part_number)
                    return {
                        'found': True, 
                        'source': 'AllDatasheet', 
                        'url': search_url,
                        'manufacturer': manufacturer,
                        'confidence': 'medium'
                    }
        except Exception as e:
            print(f"  [AllDatasheet Error]: {str(e)}")
        
        return {'found': False}
    
    def search_ti_direct(self, part_number: str) -> dict:
        """Search TI directly for SN74/TI parts"""
        part_upper = part_number.upper()
        if not (part_upper.startswith('SN74') or part_upper.startswith('TI') or part_upper.startswith('TPS') or part_upper.startswith('LM')):
            return {'found': False}
        
        try:
            # TI uses lowercase part numbers in URLs
            url = f"https://www.ti.com/product/{part_number.lower()}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                if "datasheet" in response.text.lower():
                    return {
                        'found': True, 
                        'source': 'Texas Instruments', 
                        'url': url,
                        'manufacturer': 'Texas Instruments',
                        'confidence': 'high'
                    }
        except Exception as e:
            print(f"  [TI Error]: {str(e)}")
        
        return {'found': False}
    
    def search_microchip_direct(self, part_number: str) -> dict:
        """Search Microchip directly for ATMEGA/PIC/ATTINY parts"""
        part_upper = part_number.upper()
        if not (part_upper.startswith('ATMEGA') or part_upper.startswith('ATTINY') or part_upper.startswith('PIC')):
            return {'found': False}
        
        try:
            # Microchip uses specific format
            url = f"https://www.microchip.com/en-us/product/{part_number.upper()}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                if "datasheet" in response.text.lower() or "documentation" in response.text.lower():
                    return {
                        'found': True, 
                        'source': 'Microchip', 
                        'url': url,
                        'manufacturer': 'Microchip',
                        'confidence': 'high'
                    }
        except Exception as e:
            print(f"  [Microchip Error]: {str(e)}")
        
        return {'found': False}
    
    def search_infineon_direct(self, part_number: str) -> dict:
        """Search Infineon directly for CY8C parts"""
        if not part_number.upper().startswith('CY8C'):
            return {'found': False}
        
        try:
            # Infineon search
            search_url = f"https://www.infineon.com/cms/en/search.html?intc=searchkeyword#!term={quote(part_number)}&view=keyword"
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                # If we get a result page (not 404)
                if part_number.upper() in response.text.upper():
                    return {
                        'found': True, 
                        'source': 'Infineon', 
                        'url': search_url,
                        'manufacturer': 'Infineon/Cypress',
                        'confidence': 'high'
                    }
        except Exception as e:
            print(f"  [Infineon Error]: {str(e)}")
        
        return {'found': False}
    
    def search_datasheetarchive(self, part_number: str) -> dict:
        """Search DatasheetArchive"""
        try:
            search_url = f"https://www.datasheetarchive.com/search?q={quote(part_number)}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                if "datasheet" in response.text.lower() and "results" in response.text.lower():
                    manufacturer = self.detect_manufacturer(part_number)
                    return {
                        'found': True, 
                        'source': 'DatasheetArchive', 
                        'url': search_url,
                        'manufacturer': manufacturer,
                        'confidence': 'medium'
                    }
        except Exception as e:
            print(f"  [Archive Error]: {str(e)}")
        
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
