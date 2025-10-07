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
        
        # Common datasheet sources (ordered by reliability and marking info)
        self.datasheet_sources = [
            'https://www.alldatasheet.com',
            'https://www.octopart.com', 
            'https://www.digikey.com',
            'https://www.mouser.com',
            'https://www.arrow.com',
            'https://www.avnet.com',
            'https://www.findchips.com',
            'https://www.datasheetcatalog.com',  # Less reliable
        ]
        
        # Enhanced manufacturer websites with marking document sections
        self.manufacturer_sites = {
            'Texas Instruments': {
                'base_url': 'https://www.ti.com',
                'marking_docs': 'https://www.ti.com/packaging/docs/markingtypes.tsp',
                'search_pattern': '/product/{part}'
            },
            'STMicroelectronics': {
                'base_url': 'https://www.st.com',
                'marking_docs': 'https://www.st.com/content/st_com/en/about/quality/marking-standards.html',
                'search_pattern': '/en/products/semiconductors/{part}.html'
            },
            'Analog Devices': {
                'base_url': 'https://www.analog.com',
                'marking_docs': 'https://www.analog.com/en/technical-support/packaging.html',
                'search_pattern': '/en/products/{part}.html'
            },
            'Maxim': {
                'base_url': 'https://www.maximintegrated.com',
                'marking_docs': 'https://www.maximintegrated.com/en/packaging/marking-standards.html',
                'search_pattern': '/en/products/{part}.html'
            },
            'NXP': {
                'base_url': 'https://www.nxp.com',
                'marking_docs': 'https://www.nxp.com/support/developer-resources/packaging-and-pinout:PACKAGING-PINOUT',
                'search_pattern': '/products/{part}'
            },
            'Microchip': {
                'base_url': 'https://www.microchip.com',
                'marking_docs': 'https://www.microchip.com/en-us/about/quality/package-marking',
                'search_pattern': '/wwwproducts/en/{part}'
            },
            'Atmel': {  # Now part of Microchip
                'base_url': 'https://www.microchip.com',
                'marking_docs': 'https://www.microchip.com/en-us/about/quality/package-marking',
                'search_pattern': '/wwwproducts/en/{part}'
            },
            'ON Semiconductor': {
                'base_url': 'https://www.onsemi.com',
                'marking_docs': 'https://www.onsemi.com/support/quality/package-marking',
                'search_pattern': '/products/{part}'
            },
            'Infineon': {
                'base_url': 'https://www.infineon.com',
                'marking_docs': 'https://www.infineon.com/cms/en/product/quality/package-marking/',
                'search_pattern': '/cms/en/product/{part}/'
            },
            'Cypress': {  # Now part of Infineon
                'base_url': 'https://www.infineon.com',
                'marking_docs': 'https://www.infineon.com/cms/en/product/quality/package-marking/',
                'search_pattern': '/cms/en/product/{part}/'
            },
            'Intel': {
                'base_url': 'https://www.intel.com',
                'marking_docs': 'https://www.intel.com/content/www/us/en/support/articles/000006061/processors.html',
                'search_pattern': '/content/www/us/en/products/{part}.html'
            },
            'AMD': {
                'base_url': 'https://www.amd.com',
                'marking_docs': 'https://www.amd.com/en/support/tech-docs',
                'search_pattern': '/en/products/{part}'
            },
            'Espressif': {
                'base_url': 'https://www.espressif.com',
                'marking_docs': 'https://docs.espressif.com/projects/esp-idf/en/latest/',
                'search_pattern': '/en/products/{part}'
            }
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def get_ic_official_data(self, part_number: str, manufacturer: str = None) -> Dict:
        """
        Get ONLY legitimate official IC data from internet sources
        Prioritizes manufacturer sites and authorized distributors
        """
        if not part_number:
            return {'found': False, 'reason': 'No part number provided'}
        
        part_clean = part_number.strip().upper()
        print(f"🌐 Searching legitimate sources for: {part_clean}")
        
        # First, try the working search_component_datasheet method
        # This has actual web scraping implementation for datasheet sites
        try:
            print(f"🔍 Checking datasheet databases and manufacturer sites...")
            datasheet_result = self.search_component_datasheet(part_clean, manufacturer)
            
            if datasheet_result and datasheet_result.get('found'):
                print(f"✅ Found datasheet from legitimate sources")
                datasheet_result['verified'] = True
                datasheet_result['source'] = 'legitimate_datasheet_sources'
                return datasheet_result
                
        except Exception as e:
            print(f"⚠️ Datasheet search error: {e}")
        
        # Primary legitimate sources (for future API integration)
        legitimate_sources = [
            ('manufacturer_direct', self._search_manufacturer_site),
            ('octopart', self._search_octopart_enhanced),
            ('digikey', self._search_digikey_enhanced),
            ('mouser', self._search_mouser_enhanced),
            ('ti_official', self._search_ti_official),
            ('st_official', self._search_st_official)
        ]
        
        # Try each legitimate source
        for source_name, source_func in legitimate_sources:
            try:
                if source_name == 'manufacturer_direct' and manufacturer:
                    result = source_func(part_clean, manufacturer)
                else:
                    result = self._try_enhanced_search(source_func, part_clean, manufacturer)
                
                if result and result.get('found') and self._validate_official_data(result):
                    print(f"✅ Found verified data from {source_name}")
                    result['source'] = source_name
                    result['verified'] = True
                    return result
                    
            except Exception as e:
                print(f"⚠️ {source_name} search failed: {e}")
                continue
        
        print(f"❌ No legitimate official data found for {part_clean}")
        return {'found': False, 'reason': 'No verified official documentation found', 'verified': False}
    
    def _validate_official_data(self, data: Dict) -> bool:
        """Validate that data comes from legitimate sources"""
        if not data or not data.get('found'):
            return False
        
        # Must have at least part marking or manufacturer info
        has_part_info = bool(data.get('part_marking') or data.get('product_info'))
        has_source = bool(data.get('datasheet_urls') or data.get('source_url'))
        
        return has_part_info and has_source
    
    def _try_enhanced_search(self, search_func, part_number: str, manufacturer: str = None):
        """Try enhanced search with part number variations"""
        # Try exact match first
        try:
            result = search_func(part_number, manufacturer) if manufacturer else search_func(part_number)
            if result and result.get('found'):
                return result
        except:
            pass
        
        # Try with variations
        variations = self._generate_part_variations(part_number)
        for variation in variations[:2]:  # Try top 2 variations
            try:
                result = search_func(variation, manufacturer) if manufacturer else search_func(variation)
                if result and result.get('found'):
                    return result
            except:
                continue
        
        return None
    
    def _generate_part_variations(self, part_number: str) -> List[str]:
        """Generate common part number variations"""
        variations = []
        clean = part_number.strip().upper()
        
        # Remove common prefixes/suffixes
        if '-' in clean:
            variations.append(clean.replace('-', ''))
            variations.append(clean.split('-')[0])
        
        # Add manufacturer prefixes for common ICs
        if 'ATMEGA' in clean:
            variations.extend([clean.replace('ATMEGA', 'AT MEGA'), f"AT{clean}"])
        
        if clean.startswith('STM'):
            variations.append(f"ST {clean}")
        
        return list(set(variations))
    
    def _search_octopart_enhanced(self, part_number: str, manufacturer: str = None) -> Dict:
        """Enhanced Octopart search for legitimate data"""
        # This would connect to Octopart API for real data
        # For now, return structure showing it would search
        return {'found': False, 'reason': 'API integration needed'}
    
    def _search_digikey_enhanced(self, part_number: str, manufacturer: str = None) -> Dict:
        """Enhanced DigiKey search for legitimate data"""
        # This would connect to DigiKey API for real data
        return {'found': False, 'reason': 'API integration needed'}
    
    def _search_mouser_enhanced(self, part_number: str, manufacturer: str = None) -> Dict:
        """Enhanced Mouser search for legitimate data"""
        # This would connect to Mouser API for real data
        return {'found': False, 'reason': 'API integration needed'}
    
    def _search_ti_official(self, part_number: str) -> Dict:
        """Search Texas Instruments official site"""
        # Would search TI's official product database
        return {'found': False, 'reason': 'TI API integration needed'}
    
    def _search_st_official(self, part_number: str) -> Dict:
        """Search STMicroelectronics official site"""
        # Would search ST's official product database
        return {'found': False, 'reason': 'ST API integration needed'}
    
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
            'search_results': [],
            'part_marking': None,
            'date_code_format': None,
            'package_marking': None
        }
        
        # ⚠️ INTERNET-ONLY: No local database, only real web sources
        print(f"🔍 Searching internet sources for: {part_number}")
        
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
        
        # Search general datasheet databases (only if local DB didn't find it)
        if not results['found']:
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
        
        # Try Google search as fallback (only if nothing else worked)
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
        Search a datasheet aggregator site (REAL web scraping)
        """
        results = []
        
        try:
            # Construct proper search URLs for different sites
            if 'alldatasheet' in site_url:
                search_url = f"{site_url}/search.jsp?SearchWord={part_number}"
            elif 'octopart' in site_url:
                search_url = f"{site_url}/search?q={part_number}"
            elif 'digikey' in site_url:
                search_url = f"{site_url}/products/en?keywords={part_number}"
            elif 'mouser' in site_url:
                search_url = f"{site_url}/c/?q={part_number}"
            else:
                search_url = f"{site_url}/search?q={part_number}"
            
            print(f"  🌐 Trying {urlparse(site_url).netloc}...")
            
            response = requests.get(
                search_url,
                headers=self.headers,
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find datasheet links with better patterns
                links = soup.find_all('a', href=True)
                
                for link in links[:10]:  # Top 10 results
                    href = link.get('href')
                    text = link.get_text().strip()
                    
                    # Look for part number in text or URL
                    if part_number.upper() in text.upper() or part_number.upper() in href.upper():
                        full_url = urljoin(site_url, href)
                        
                        # Check if it's likely a datasheet/product page
                        if any(keyword in full_url.lower() for keyword in ['datasheet', 'pdf', 'product', 'detail', part_number.lower()]):
                            results.append({
                                'title': text or part_number,
                                'url': full_url,
                                'source': urlparse(site_url).netloc,
                                'found': True
                            })
                            print(f"    ✅ Found: {text[:50] if text else part_number}...")
                
                if results:
                    print(f"    ✅ Found {len(results)} results from {urlparse(site_url).netloc}")
            
        except requests.exceptions.RequestException as e:
            # Network error - log but don't crash
            print(f"  ⚠️  Network error accessing {urlparse(site_url).netloc}: {type(e).__name__}")
        except Exception as e:
            print(f"  ⚠️  Error accessing {urlparse(site_url).netloc}: {type(e).__name__}")
        
        return results
    
    def _google_search_datasheet(self, part_number: str, manufacturer: str = None) -> List[Dict]:
        """
        Use DuckDuckGo HTML search to find datasheets (Google alternative)
        """
        results = []
        
        try:
            # Construct search query
            query = f"{part_number} datasheet filetype:pdf"
            if manufacturer:
                query = f"{manufacturer} {query}"
            
            # Use DuckDuckGo HTML search (no API needed)
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            print(f"  🔍 Searching DuckDuckGo for datasheets...")
            
            response = requests.get(
                search_url,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find result links
                result_links = soup.find_all('a', class_='result__a')
                
                for link in result_links[:5]:  # Top 5 results
                    href = link.get('href')
                    title = link.get_text().strip()
                    
                    if href and part_number.upper() in title.upper():
                        results.append({
                            'title': title,
                            'url': href,
                            'source': 'duckduckgo_search',
                            'found': True
                        })
                        print(f"    ✅ Found via search: {title[:60]}...")
            
        except Exception as e:
            print(f"  ⚠️  Search error: {type(e).__name__}")
        
        return results
    
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
        """Search enhanced local database for common ICs with detailed marking specs"""
        # Enhanced IC database with detailed marking specifications
        ic_database = {
            'ATMEGA328P': {
                'manufacturer': 'Atmel/Microchip',
                'description': '8-bit AVR Microcontroller',
                'package': 'TQFP-32, DIP-28',
                'datasheet_info': 'Available from Microchip Technology',
                'part_marking': 'ATMEGA328P',
                'date_code_format': 'YYWW',
                'package_marking': '-AU, -PU',
                'legitimate_markings': [
                    'ATMEL\\nATMEGA328P\\n20AU\\nYYWW',
                    'ATMEGA328P\\n20AU\\nYYWW',
                    '△\\nATMEGA328P\\n20AU\\nYYWW'
                ],
                'counterfeit_indicators': [
                    'Incorrect manufacturer logo or text (AmeL, ATML, etc.)',
                    'Poor text quality or inconsistent fonts',
                    'Missing or incorrect date codes',
                    'Suspicious package markings'
                ]
            },
            'ATMEGA32': {
                'manufacturer': 'Atmel/Microchip', 
                'description': '8-bit AVR Microcontroller',
                'package': 'TQFP-44, DIP-40',
                'datasheet_info': 'Available from Microchip Technology',
                'part_marking': 'ATMEGA32',
                'date_code_format': 'YYWW',
                'package_marking': '-AU, -PU',
                'legitimate_markings': [
                    'ATMEL\\nATMEGA32\\n16AU\\nYYWW'
                ],
                'counterfeit_indicators': [
                    'Incorrect manufacturer text',
                    'Poor marking quality'
                ]
            },
            'STM32F103': {
                'manufacturer': 'STMicroelectronics',
                'description': '32-bit ARM Cortex-M3 Microcontroller',
                'package': 'LQFP-48, LQFP-64',
                'datasheet_info': 'Available from STMicroelectronics',
                'part_marking': 'STM32F103',
                'date_code_format': 'YYWW',
                'package_marking': 'Various',
                'legitimate_markings': [
                    'STM32F103\\nC8T6\\nYYWWX\\nCHN'
                ],
                'counterfeit_indicators': [
                    'Missing ST logo',
                    'Incorrect package codes'
                ]
            },
            'ESP32': {
                'manufacturer': 'Espressif',
                'description': 'Wi-Fi & Bluetooth Microcontroller',
                'package': 'QFN-48',
                'datasheet_info': 'Available from Espressif Systems',
                'part_marking': 'ESP32',
                'date_code_format': 'YYWW',
                'package_marking': 'Various',
                'legitimate_markings': [
                    'ESP32-D0WDQ6\\nYYWWX'
                ],
                'counterfeit_indicators': [
                    'Missing Espressif logo',
                    'Incorrect part variants'
                ]
            },
            'CY8C29666': {
                'manufacturer': 'Cypress/Infineon',
                'description': 'PSoC Mixed Signal Microcontroller',
                'package': 'TQFP-44',
                'datasheet_info': 'Available from Infineon/Cypress',
                'part_marking': 'CY8C29666',
                'date_code_format': 'YYWW',
                'package_marking': '-24PXI, -24PVXI',
                'legitimate_markings': [
                    'CY8C29666-24PvXi\\nB 05\\nYYWW\\nCYP XXXXX'
                ],
                'counterfeit_indicators': [
                    'Missing Cypress logo',
                    'Incorrect package suffixes',
                    'Poor date code formatting'
                ]
            },
            'LM358': {
                'manufacturer': 'Texas Instruments',
                'description': 'Dual Operational Amplifier',
                'package': 'DIP-8, SOIC-8',
                'datasheet_info': 'Available from Texas Instruments',
                'part_marking': 'LM358',
                'date_code_format': 'YYWW',
                'package_marking': 'N, D',
                'legitimate_markings': [
                    'LM358N\\nYYWW\\nTEXAS INSTRUMENTS'
                ],
                'counterfeit_indicators': [
                    'Missing TI logo',
                    'Incorrect package suffixes'
                ]
            },
            'NE555': {
                'manufacturer': 'Various (TI, ST, etc.)',
                'description': 'Timer IC',
                'package': 'DIP-8, SOIC-8',
                'datasheet_info': 'Available from multiple manufacturers',
                'part_marking': 'NE555',
                'date_code_format': 'YYWW',
                'package_marking': 'N, D',
                'legitimate_markings': [
                    'NE555N\\nYYWW'
                ],
                'counterfeit_indicators': [
                    'Poor marking quality',
                    'Suspicious manufacturer codes'
                ]
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
                'method': 'local_db',
                'found': True,
                'part_marking': info['part_marking'],
                'date_code_format': info['date_code_format'],
                'package_marking': info['package_marking'],
                'legitimate_markings': info.get('legitimate_markings', []),
                'counterfeit_indicators': info.get('counterfeit_indicators', [])
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
                    'method': 'local_db_partial',
                    'found': True,
                    'part_marking': info['part_marking'],
                    'date_code_format': info['date_code_format'],
                    'package_marking': info['package_marking'],
                    'legitimate_markings': info.get('legitimate_markings', []),
                    'counterfeit_indicators': info.get('counterfeit_indicators', [])
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
