"""
Enhanced Web Scraper with PDF Search and Better Manufacturer Site Handling
Handles specific cases like CY8C29666-24PVXI from Infineon/Cypress
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, Optional, List
from urllib.parse import quote_plus, urljoin
import logging


class EnhancedDatasheetScraper:
    """Enhanced scraper with PDF search and better manufacturer handling"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 10
        
        # Manufacturer-specific search URLs
        self.manufacturer_sites = {
            'infineon': {
                'search_url': 'https://www.infineon.com/cms/en/search.html',
                'product_path': '/cms/en/product/'
            },
            'cypress': {
                'search_url': 'https://www.infineon.com/cms/en/search.html',  # Cypress now part of Infineon
                'product_path': '/cms/en/product/'
            },
            'ti': {
                'search_url': 'https://www.ti.com/sitesearch/en-us/docs/universalsearch.tsp',
                'product_path': '/product/'
            },
            'microchip': {
                'search_url': 'https://www.microchip.com/en-us/search',
                'product_path': '/en-us/product/'
            },
            'atmel': {  # Now Microchip
                'search_url': 'https://www.microchip.com/en-us/search',
                'product_path': '/en-us/product/'
            },
            'national': {  # Now TI
                'search_url': 'https://www.ti.com/sitesearch/en-us/docs/universalsearch.tsp',
                'product_path': '/product/'
            }
        }
    
    def search_google_for_pdfs(self, part_number: str) -> Optional[str]:
        """Search Google specifically for PDF datasheets"""
        try:
            # Google search for PDFs
            query = f"{part_number} datasheet filetype:pdf"
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for PDF links in results
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '.pdf' in href.lower() and ('datasheet' in href.lower() or part_number.lower() in href.lower()):
                        # Extract actual URL from Google redirect
                        if '/url?q=' in href:
                            actual_url = href.split('/url?q=')[1].split('&')[0]
                            return actual_url
                        elif href.startswith('http'):
                            return href
            
        except Exception as e:
            logging.debug(f"Google PDF search error: {e}")
        
        return None
    
    def search_mouser(self, part_number: str) -> Dict:
        """Search Mouser for part and datasheet"""
        try:
            # Mouser search API
            search_url = f"https://www.mouser.com/Search/Refine?Keyword={quote_plus(part_number)}"
            
            response = self.session.get(search_url, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for product page link
                product_links = soup.find_all('a', href=re.compile(r'/ProductDetail/'))
                if product_links:
                    product_url = urljoin('https://www.mouser.com', product_links[0]['href'])
                    
                    # Get product page
                    prod_response = self.session.get(product_url, timeout=self.timeout)
                    if prod_response.status_code == 200:
                        prod_soup = BeautifulSoup(prod_response.text, 'html.parser')
                        
                        # Find datasheet link
                        datasheet_links = prod_soup.find_all('a', href=re.compile(r'.*\.(pdf|PDF).*'))
                        datasheet_links += prod_soup.find_all('a', text=re.compile(r'[Dd]atasheet'))
                        
                        if datasheet_links:
                            datasheet_url = datasheet_links[0].get('href', '')
                            if datasheet_url:
                                if not datasheet_url.startswith('http'):
                                    datasheet_url = urljoin('https://www.mouser.com', datasheet_url)
                                
                                return {
                                    'found': True,
                                    'source': 'Mouser',
                                    'datasheet_url': datasheet_url,
                                    'part_marking': part_number
                                }
        
        except Exception as e:
            logging.debug(f"Mouser search error: {e}")
        
        return {'found': False}
    
    def search_digikey(self, part_number: str) -> Dict:
        """Search DigiKey for part and datasheet"""
        try:
            # DigiKey search
            search_url = f"https://www.digikey.com/en/products/filter?keywords={quote_plus(part_number)}"
            
            response = self.session.get(search_url, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for product links
                product_links = soup.find_all('a', href=re.compile(r'/en/products/detail/'))
                if product_links:
                    product_url = urljoin('https://www.digikey.com', product_links[0]['href'])
                    
                    # Get product page
                    prod_response = self.session.get(product_url, timeout=self.timeout)
                    if prod_response.status_code == 200:
                        prod_soup = BeautifulSoup(prod_response.text, 'html.parser')
                        
                        # Find datasheet link (DigiKey has specific class/structure)
                        datasheet_section = prod_soup.find('a', href=re.compile(r'.*\.(pdf|PDF).*'), 
                                                          text=re.compile(r'[Dd]atasheet'))
                        
                        if datasheet_section:
                            datasheet_url = datasheet_section.get('href', '')
                            if datasheet_url and not datasheet_url.startswith('http'):
                                datasheet_url = urljoin('https://www.digikey.com', datasheet_url)
                            
                            return {
                                'found': True,
                                'source': 'DigiKey',
                                'datasheet_url': datasheet_url,
                                'part_marking': part_number
                            }
        
        except Exception as e:
            logging.debug(f"DigiKey search error: {e}")
        
        return {'found': False}
    
    def search_infineon(self, part_number: str) -> Dict:
        """Search Infineon (includes Cypress products like CY8C)"""
        try:
            # Infineon/Cypress product search
            search_url = f"https://www.infineon.com/cms/en/search.html#!term={quote_plus(part_number)}&view=keyword"
            
            response = self.session.get(search_url, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for product links
                product_links = soup.find_all('a', href=re.compile(r'/cms/en/product/'))
                if product_links:
                    product_url = urljoin('https://www.infineon.com', product_links[0]['href'])
                    
                    # Get product page
                    prod_response = self.session.get(product_url, timeout=self.timeout)
                    if prod_response.status_code == 200:
                        prod_soup = BeautifulSoup(prod_response.text, 'html.parser')
                        
                        # Find datasheet in "Documents" section
                        doc_links = prod_soup.find_all('a', href=re.compile(r'.*\.(pdf|PDF).*'))
                        datasheet_links = [link for link in doc_links 
                                         if 'datasheet' in link.get('href', '').lower() or 
                                            'datasheet' in link.text.lower()]
                        
                        if datasheet_links:
                            datasheet_url = datasheet_links[0].get('href', '')
                            if not datasheet_url.startswith('http'):
                                datasheet_url = urljoin('https://www.infineon.com', datasheet_url)
                            
                            return {
                                'found': True,
                                'source': 'Infineon/Cypress',
                                'datasheet_url': datasheet_url,
                                'part_marking': part_number
                            }
        
        except Exception as e:
            logging.debug(f"Infineon search error: {e}")
        
        return {'found': False}
    
    def search_comprehensive(self, part_number: str) -> Dict:
        """
        Comprehensive search across multiple sources
        Priority: PDF search, Mouser, DigiKey, Manufacturer sites
        """
        print(f"\n🔍 Comprehensive search for: {part_number}")
        
        # 1. Try Google PDF search first (fastest for direct datasheets)
        print("  [1/5] Searching Google for PDFs...")
        pdf_url = self.search_google_for_pdfs(part_number)
        if pdf_url:
            print(f"  ✅ Found PDF: {pdf_url[:80]}...")
            return {
                'found': True,
                'source': 'Google PDF Search',
                'datasheet_url': pdf_url,
                'part_marking': part_number
            }
        
        # 2. Try Mouser
        print("  [2/5] Searching Mouser...")
        mouser_result = self.search_mouser(part_number)
        if mouser_result.get('found'):
            print(f"  ✅ Found on Mouser")
            return mouser_result
        
        # 3. Try DigiKey
        print("  [3/5] Searching DigiKey...")
        digikey_result = self.search_digikey(part_number)
        if digikey_result.get('found'):
            print(f"  ✅ Found on DigiKey")
            return digikey_result
        
        # 4. Try manufacturer-specific search based on part prefix
        print("  [4/5] Checking manufacturer sites...")
        if part_number.upper().startswith('CY8C'):
            # Cypress/Infineon
            infineon_result = self.search_infineon(part_number)
            if infineon_result.get('found'):
                print(f"  ✅ Found on Infineon/Cypress site")
                return infineon_result
        
        # 5. Fallback to existing scraper
        print("  [5/5] Trying fallback sources...")
        from web_scraper import DatasheetScraper
        fallback_scraper = DatasheetScraper()
        fallback_result = fallback_scraper.get_ic_official_data(part_number, '')
        
        if fallback_result and fallback_result.get('found'):
            print(f"  ✅ Found via fallback scraper")
            return fallback_result
        
        print(f"  ❌ No datasheet found across all sources")
        return {'found': False}


def test_enhanced_scraper():
    """Test the enhanced scraper with problematic parts"""
    test_parts = [
        "CY8C29666-24PVXI",  # Cypress PSoC - should find on Infineon
        "ATMEGA328P",  # Microchip - should find easily
        "SN74HC595N",  # TI - should find easily
        "ADC0831CCN",  # National/TI - should find
    ]
    
    scraper = EnhancedDatasheetScraper()
    
    print("="*100)
    print("TESTING ENHANCED DATASHEET SCRAPER")
    print("="*100)
    
    for part in test_parts:
        print(f"\n{'='*100}")
        print(f"Testing: {part}")
        print('='*100)
        
        result = scraper.search_comprehensive(part)
        
        if result.get('found'):
            print(f"\n✅ SUCCESS!")
            print(f"   Source: {result.get('source')}")
            print(f"   Datasheet: {result.get('datasheet_url', 'N/A')[:100]}")
        else:
            print(f"\n❌ NOT FOUND")
        
        time.sleep(2)  # Be polite to servers


if __name__ == "__main__":
    test_enhanced_scraper()
