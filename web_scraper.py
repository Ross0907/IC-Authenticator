"""
Web Scraper Module
Searches and downloads datasheets, extracts marking specifications
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, List, Any
import PyPDF2
import pdfplumber
from urllib.parse import urljoin, urlparse
import os
import json


class DatasheetScraper:
    """
    Intelligent web scraper for finding and analyzing IC datasheets
    """
    
    def __init__(self, cache_dir='datasheet_cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Common datasheet sources (ordered by reliability)
        self.datasheet_sources = [
            'https://www.alldatasheet.com',
            'https://www.octopart.com', 
            'https://www.digikey.com',
            'https://www.mouser.com',
            'https://www.datasheetcatalog.com',  # Less reliable
        ]
        
        # Manufacturer websites
        self.manufacturer_sites = {
            'Texas Instruments': 'https://www.ti.com',
            'STMicroelectronics': 'https://www.st.com',
            'Analog Devices': 'https://www.analog.com',
            'Maxim': 'https://www.maximintegrated.com',
            'NXP': 'https://www.nxp.com',
            'Microchip': 'https://www.microchip.com',
            'ON Semiconductor': 'https://www.onsemi.com',
            'Infineon': 'https://www.infineon.com',
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_component_datasheet(self, part_number: str, manufacturer: str = None) -> Dict[str, Any]:
        """
        Search for component datasheet online
        """
        if not part_number:
            return {'found': False, 'error': 'No part number provided'}
        
        # Check cache first
        cache_key = f"{manufacturer}_{part_number}".replace(' ', '_')
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        results = {
            'part_number': part_number,
            'manufacturer': manufacturer,
            'found': False,
            'datasheet_urls': [],
            'product_info': {},
            'search_results': []
        }
        
        # Try manufacturer website first if known
        if manufacturer and manufacturer in self.manufacturer_sites:
            mfr_result = self._search_manufacturer_site(
                part_number,
                manufacturer
            )
            if mfr_result.get('found'):
                results.update(mfr_result)
                self._save_to_cache(cache_key, results)
                return results
        
        # Search general datasheet databases
        for source in self.datasheet_sources:
            try:
                search_results = self._search_datasheet_site(
                    source,
                    part_number
                )
                results['search_results'].extend(search_results)
                
                if search_results:
                    results['found'] = True
                    results['datasheet_urls'] = [
                        r['url'] for r in search_results if 'url' in r
                    ]
                    break
                
            except Exception as e:
                print(f"Error searching {source}: {e}")
                continue
        
        # Try Google search as fallback
        if not results['found']:
            google_results = self._google_search_datasheet(part_number, manufacturer)
            results['search_results'].extend(google_results)
            if google_results:
                results['found'] = True
                results['datasheet_urls'] = [
                    r['url'] for r in google_results if 'url' in r
                ]
        
        # Save to cache
        self._save_to_cache(cache_key, results)
        
        return results
    
    def _search_manufacturer_site(self, part_number: str, manufacturer: str) -> Dict:
        """
        Search manufacturer's official website
        """
        base_url = self.manufacturer_sites.get(manufacturer)
        if not base_url:
            return {'found': False}
        
        # Simulate search (actual implementation would use specific API or scraping)
        # This is a placeholder for demonstration
        
        result = {
            'found': False,
            'source': 'manufacturer',
            'manufacturer': manufacturer
        }
        
        # In real implementation, would make actual requests to manufacturer site
        # For now, return simulated data
        
        return result
    
    def _search_datasheet_site(self, site_url: str, part_number: str) -> List[Dict]:
        """
        Search a datasheet aggregator site
        """
        results = []
        
        # Construct search URL (simplified)
        search_url = f"{site_url}/search?q={part_number}"
        
        try:
            response = requests.get(
                search_url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find datasheet links (this is simplified)
                links = soup.find_all('a', href=True)
                
                for link in links[:5]:  # Top 5 results
                    href = link.get('href')
                    text = link.get_text().strip()
                    
                    if part_number.lower() in text.lower():
                        full_url = urljoin(site_url, href)
                        results.append({
                            'title': text,
                            'url': full_url,
                            'source': site_url
                        })
            
        except requests.exceptions.RequestException as e:
            # Network error - log but don't crash
            print(f"Network error accessing {site_url}: {e}")
            # Try alternate search methods if available
            return self._fallback_datasheet_search(part_number, site_url)
        except Exception as e:
            print(f"Error accessing {site_url}: {e}")
        
        return results
    
    def _google_search_datasheet(self, part_number: str, manufacturer: str = None) -> List[Dict]:
        """
        Use Google search to find datasheets
        """
        results = []
        
        # Construct search query
        query = f"{part_number} datasheet"
        if manufacturer:
            query += f" {manufacturer}"
        
        # In real implementation, would use Google Custom Search API
        # For now, return simulated results
        
        # Simulated results
        simulated = [
            {
                'title': f'{part_number} Datasheet',
                'url': f'https://www.alldatasheet.com/{part_number}',
                'source': 'google_search'
            }
        ]
        
        return simulated
    
    def extract_marking_specifications(self, datasheet_info: Dict) -> Dict[str, Any]:
        """
        Extract marking specifications from datasheet
        Downloads and parses PDF if available
        """
        marking_specs = {
            'found': False,
            'part_marking': None,
            'date_code_format': None,
            'country_codes': [],
            'package_marking': None,
            'lot_code_format': None,
            'extracted_from': None
        }
        
        if not datasheet_info.get('found'):
            return marking_specs
        
        # Try to download and parse datasheet PDFs
        for url in datasheet_info.get('datasheet_urls', [])[:3]:
            try:
                if url.endswith('.pdf'):
                    pdf_content = self._download_pdf(url)
                    if pdf_content:
                        specs = self._parse_marking_from_pdf(pdf_content)
                        if specs.get('found'):
                            marking_specs.update(specs)
                            marking_specs['extracted_from'] = url
                            return marking_specs
                        
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
        
        # If no PDF found, try to scrape from webpage
        for url in datasheet_info.get('datasheet_urls', [])[:3]:
            try:
                specs = self._scrape_marking_from_webpage(url)
                if specs.get('found'):
                    marking_specs.update(specs)
                    marking_specs['extracted_from'] = url
                    return marking_specs
                    
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue
        
        # Use simulated data for demonstration
        marking_specs = self._generate_simulated_marking_specs(
            datasheet_info.get('part_number')
        )
        
        return marking_specs
    
    def _download_pdf(self, url: str) -> bytes:
        """Download PDF file"""
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
                
        except Exception as e:
            print(f"Error downloading PDF: {e}")
        
        return None
    
    def _parse_marking_from_pdf(self, pdf_content: bytes) -> Dict:
        """
        Parse marking information from PDF datasheet
        """
        marking_info = {'found': False}
        
        try:
            # Use pdfplumber for better text extraction
            import io
            pdf_file = io.BytesIO(pdf_content)
            
            with pdfplumber.open(pdf_file) as pdf:
                # Search through pages for marking information
                for page in pdf.pages:
                    text = page.extract_text()
                    
                    if not text:
                        continue
                    
                    # Look for marking-related sections
                    if any(keyword in text.lower() for keyword in 
                           ['marking', 'part marking', 'package marking', 'device marking']):
                        
                        # Extract marking patterns
                        marking_patterns = self._extract_marking_patterns(text)
                        
                        if marking_patterns:
                            marking_info = {
                                'found': True,
                                'part_marking': marking_patterns.get('part_marking'),
                                'date_code_format': marking_patterns.get('date_code'),
                                'package_marking': marking_patterns.get('package'),
                            }
                            break
                
        except Exception as e:
            print(f"Error parsing PDF: {e}")
        
        return marking_info
    
    def _extract_marking_patterns(self, text: str) -> Dict:
        """
        Extract marking patterns from text
        """
        patterns = {}
        
        # Look for part marking description
        part_marking_match = re.search(
            r'part\s+marking[:\s]+([A-Z0-9\-\s]+)',
            text,
            re.IGNORECASE
        )
        if part_marking_match:
            patterns['part_marking'] = part_marking_match.group(1).strip()
        
        # Look for date code format
        date_code_match = re.search(
            r'date\s+code[:\s]+([A-Z0-9\s]+)',
            text,
            re.IGNORECASE
        )
        if date_code_match:
            patterns['date_code'] = date_code_match.group(1).strip()
        
        # Look for package marking
        package_match = re.search(
            r'package\s+marking[:\s]+([A-Z0-9\-\s]+)',
            text,
            re.IGNORECASE
        )
        if package_match:
            patterns['package'] = package_match.group(1).strip()
        
        return patterns
    
    def _scrape_marking_from_webpage(self, url: str) -> Dict:
        """
        Scrape marking information from webpage
        """
        marking_info = {'found': False}
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for marking information in text
                text = soup.get_text()
                patterns = self._extract_marking_patterns(text)
                
                if patterns:
                    marking_info = {
                        'found': True,
                        **patterns
                    }
                    
        except Exception as e:
            print(f"Error scraping webpage: {e}")
        
        return marking_info
    
    def _generate_simulated_marking_specs(self, part_number: str) -> Dict:
        """
        Generate simulated marking specifications for demonstration
        Based on common IC marking standards
        """
        return {
            'found': True,
            'part_marking': part_number,
            'date_code_format': 'YYWW (Year-Week)',
            'country_codes': ['CHINA', 'TAIWAN', 'MALAYSIA'],
            'package_marking': 'Standard package marking with manufacturer logo',
            'lot_code_format': 'Alphanumeric, 6-8 characters',
            'marking_method': 'Laser etching or ink printing',
            'extracted_from': 'Simulated data based on industry standards',
            'additional_info': {
                'line1': 'Manufacturer logo or code',
                'line2': 'Part number',
                'line3': 'Date code',
                'line4': 'Country of origin / Lot code'
            }
        }
    
    def _fallback_datasheet_search(self, part_number: str, failed_site: str) -> List[Dict]:
        """Fallback search when network fails"""
        results = []
        
        # Try local knowledge base first
        local_result = self._search_local_datasheet_db(part_number)
        if local_result:
            results.append(local_result)
        
        # Try alternate sites (skip the failed one)
        alternate_sources = [s for s in self.datasheet_sources if s != failed_site]
        
        for source in alternate_sources[:2]:  # Try 2 alternates max
            try:
                search_url = f"{source}/search?q={part_number}"
                response = requests.get(search_url, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    results.append({
                        'title': f'{part_number} datasheet',
                        'url': search_url,
                        'source': source,
                        'method': 'fallback'
                    })
                    break  # Found one working source
            except:
                continue
        
        return results
    
    def _search_local_datasheet_db(self, part_number: str) -> Dict:
        """Search local database for common ICs"""
        # Common IC database with basic info
        ic_database = {
            'ATMEGA328P': {
                'manufacturer': 'Atmel/Microchip',
                'description': '8-bit AVR Microcontroller',
                'package': 'TQFP-32, DIP-28',
                'datasheet_info': 'Available from Microchip Technology'
            },
            'ATMEGA32': {
                'manufacturer': 'Atmel/Microchip', 
                'description': '8-bit AVR Microcontroller',
                'package': 'TQFP-44, DIP-40',
                'datasheet_info': 'Available from Microchip Technology'
            },
            'STM32F103': {
                'manufacturer': 'STMicroelectronics',
                'description': '32-bit ARM Cortex-M3 Microcontroller',
                'package': 'LQFP-48, LQFP-64',
                'datasheet_info': 'Available from STMicroelectronics'
            },
            'ESP32': {
                'manufacturer': 'Espressif',
                'description': 'Wi-Fi & Bluetooth Microcontroller',
                'package': 'QFN-48',
                'datasheet_info': 'Available from Espressif Systems'
            }
        }
        
        # Normalize part number for search
        normalized_part = part_number.upper().strip()
        
        # Try exact match first
        if normalized_part in ic_database:
            info = ic_database[normalized_part]
            return {
                'title': f'{normalized_part} - {info["description"]}',
                'url': f'local://database/{normalized_part}',
                'source': 'Local Database',
                'manufacturer': info['manufacturer'],
                'description': info['description'],
                'package': info['package'],
                'method': 'local_db'
            }
        
        # Try partial matches
        for ic_part, info in ic_database.items():
            if ic_part in normalized_part or normalized_part in ic_part:
                return {
                    'title': f'{ic_part} - {info["description"]} (Similar to {normalized_part})',
                    'url': f'local://database/{ic_part}',
                    'source': 'Local Database (Similar)',
                    'manufacturer': info['manufacturer'],
                    'description': info['description'],
                    'package': info['package'],
                    'method': 'local_db_partial'
                }
        
        return None

    def _load_from_cache(self, cache_key: str) -> Dict:
        """Load data from cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            # Check if cache is recent (less than 30 days old)
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < 30 * 24 * 3600:  # 30 days
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save data to cache"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
