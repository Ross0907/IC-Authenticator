"""
Smart Datasheet Finder - Downloads PDFs and extracts marking schemes

This module intelligently finds and downloads IC datasheets, then extracts
marking scheme information to validate chip authenticity.
"""

import re
import logging
import requests
from pathlib import Path
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
import concurrent.futures
from urllib.parse import urljoin, urlparse
import urllib.parse
import PyPDF2
import io
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class SmartDatasheetFinder:
    """Intelligent datasheet finder that downloads PDFs and extracts marking info"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Timeout settings (quick for responsiveness)
        self.timeout = 3  # 3 seconds max per request
        
    def find_datasheet(self, part_number: str, manufacturer: str) -> Dict:
        """Find datasheet PDF and extract marking information"""
        logger.info(f"  🔍 Searching for {part_number} datasheet...")
        
        # Check cache first
        cached_result = self._check_cache(part_number)
        if cached_result:
            return cached_result
        
        # Search for PDF in parallel across multiple sources
        pdf_url = self._find_pdf_url(part_number, manufacturer)
        
        if not pdf_url:
            logger.info(f"  ✗ No PDF datasheet found for {part_number}")
            return {'found': False, 'url': None, 'marking_info': None, 'source': None}
        
        # Download PDF
        pdf_path = self._download_pdf(pdf_url, part_number)
        
        if not pdf_path:
            logger.warning(f"  ✗ Failed to download PDF from {pdf_url}")
            return {'found': True, 'url': pdf_url, 'local_file': None, 'marking_info': None, 'source': 'Link Only'}
        
        # Save metadata with original URL
        self._save_metadata(pdf_path, pdf_url, part_number, manufacturer)
        
        # Extract marking information from PDF
        marking_info = self._extract_marking_from_pdf(pdf_path)
        
        # Return file:// URL for local cached PDF
        file_url = pdf_path.absolute().as_uri()
        
        logger.info(f"  ✓ Datasheet PDF downloaded and cached: {pdf_path.name}")
        
        return {
            'found': True,
            'url': pdf_url,  # Original manufacturer URL for display in tabs
            'local_file': file_url,  # Local cached file for PDF viewer
            'marking_info': marking_info,
            'source': 'PDF Downloaded',
            'pdf_path': str(pdf_path)
        }
    
    def _check_cache(self, part_number: str) -> Optional[Dict]:
        """Check if PDF already cached"""
        cached_file = self.cache_dir / f"{part_number}.pdf"
        
        if cached_file.exists():
            logger.info(f"  ✓ Found in cache: {cached_file.name}")
            
            # Extract marking info from cached PDF
            marking_info = self._extract_marking_from_pdf(cached_file)
            
            # Try to load metadata to get original URL
            metadata = self._load_metadata(cached_file)
            original_url = metadata.get('url') if metadata else None
            
            # Use cached file URL
            file_url = cached_file.absolute().as_uri()
            
            # If no metadata (old cached PDF), return with warning
            # The URL will be file:// but at least the PDF is available
            if not original_url:
                logger.debug(f"  ⚠️  No metadata found for cached PDF: {cached_file.name}")
                logger.debug(f"     This PDF was downloaded before metadata system was added")
            
            return {
                'found': True,
                'url': original_url or file_url,  # Use original URL if available, else file URL
                'local_file': file_url,
                'marking_info': marking_info,
                'source': 'Local Cache' if original_url else 'Local Cache (Legacy)',
                'pdf_path': str(cached_file)
            }
        
        return None
    
    def _find_pdf_url(self, part_number: str, manufacturer: str) -> Optional[str]:
        """Find direct PDF URL using parallel search across sources"""
        
        # Universal search - no hardcoded URLs
        part_upper = re.sub(r'[^A-Z0-9-]', '', part_number).upper()
        
        # Prepare search functions
        search_functions = []
        
        if 'Texas Instruments' in manufacturer or 'TI' in manufacturer:
            search_functions.append(('TI', lambda: self._search_ti_pdf(part_number)))
        
        if 'Microchip' in manufacturer or 'Atmel' in manufacturer:
            search_functions.append(('Microchip', lambda: self._search_microchip_pdf(part_number)))
        
        if 'Infineon' in manufacturer or 'Cypress' in manufacturer:
            search_functions.append(('Infineon', lambda: self._search_infineon_pdf(part_number)))
        
        if 'NXP' in manufacturer:
            search_functions.append(('NXP', lambda: self._search_nxp_pdf(part_number)))
        
        if 'STMicroelectronics' in manufacturer or 'STM' in manufacturer:
            search_functions.append(('STM', lambda: self._search_stm_pdf(part_number)))
        
        if 'Analog' in manufacturer or 'Linear' in manufacturer:
            search_functions.append(('Analog', lambda: self._search_analog_pdf(part_number)))
        
        if 'ON Semiconductor' in manufacturer or 'onsemi' in manufacturer.lower():
            search_functions.append(('ONSemi', lambda: self._search_onsemi_pdf(part_number)))
        
        # If manufacturer unknown or "Various" (generic parts), try all sources
        if not search_functions or 'Various' in manufacturer or 'Unknown' in manufacturer:
            search_functions = [
                ('TI', lambda: self._search_ti_pdf(part_number)),
                ('Microchip', lambda: self._search_microchip_pdf(part_number)),
                ('Infineon', lambda: self._search_infineon_pdf(part_number)),
                ('NXP', lambda: self._search_nxp_pdf(part_number)),
                ('STM', lambda: self._search_stm_pdf(part_number)),
                ('Analog', lambda: self._search_analog_pdf(part_number)),
                ('ONSemi', lambda: self._search_onsemi_pdf(part_number)),
            ]
        
        # For 74HC parts, also try ON Semiconductor (they make pin-compatible parts)
        if part_upper.startswith('M74HC') or part_upper.startswith('74HC'):
            search_functions.append(('ONSemi-Fallback', lambda: self._search_onsemi_pdf(part_number)))
        
        # For NE555 and common generic ICs, prioritize TI and add ST as fallback
        if part_upper.startswith('NE555') or part_upper.startswith('NE5'):
            # NE555 is made by many vendors - try TI first, then ST
            search_functions.insert(0, ('TI-NE555', lambda: self._search_ti_pdf('NE555')))
            search_functions.append(('ST-NE555', lambda: self._search_stm_pdf('NE555')))
        
        # For LM556 (dual 555 timer) - try multiple vendors since TI discontinued it
        if part_upper.startswith('LM556') or part_upper.startswith('LK556'):
            # LM556 is available from multiple vendors, try aggregators
            search_functions.insert(0, ('DigiKey-LM556', lambda: self._search_digikey_pdf('LM556')))
            search_functions.insert(1, ('Mouser-LM556', lambda: self._search_mouser_pdf('LM556')))
            search_functions.append(('AllDatasheet-LM556', lambda: self._search_alldatasheet_pdf('LM556')))
        
        # For ATMEL parts - try aggregators to bypass Microchip bot protection
        if part_upper.startswith('ATMEL'):
            atmel_num = part_upper[5:]
            search_functions.insert(0, ('DigiKey-ATMEL', lambda: self._search_digikey_pdf(f'ATMEL{atmel_num}')))
            search_functions.insert(1, ('Mouser-ATMEL', lambda: self._search_mouser_pdf(f'ATMEL{atmel_num}')))
            search_functions.append(('AllDatasheet-ATMEL', lambda: self._search_alldatasheet_pdf(f'ATMEL{atmel_num}')))
        
        # Try each search function with timeout
        for source, search_func in search_functions:
            try:
                logger.debug(f"    Trying {source}...")
                pdf_url = search_func()
                
                if pdf_url:
                    logger.debug(f"    ✓ Found PDF URL from {source}: {pdf_url}")
                    return pdf_url
            except Exception as e:
                logger.debug(f"    ✗ {source} search failed: {e}")
                continue
        
        # Try generic fallback search (Octopart aggregator)
        logger.debug(f"    Trying generic fallback search...")
        pdf_url = self._search_generic_fallback(part_number)
        if pdf_url:
            logger.debug(f"    ✓ Found PDF URL from generic search: {pdf_url}")
            return pdf_url
        
        # Last resort: Try Google search (most powerful fallback)
        logger.debug(f"    Trying Google search...")
        pdf_url = self._search_google_pdf(part_number, manufacturer)
        if pdf_url:
            logger.debug(f"    ✓ Found PDF URL from Google: {pdf_url}")
            return pdf_url
        
        return None
    
    def _search_digikey_pdf(self, part: str) -> Optional[str]:
        """Search DigiKey for direct PDF datasheet link"""
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        logger.debug(f"🔍 DigiKey search: part={part}, base={base}")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            # DigiKey product search
            search_url = f"https://www.digikey.com/en/products/result?keywords={base}"
            logger.debug(f"   Trying DigiKey: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for datasheet PDF links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text().lower()
                    
                    # DigiKey links to manufacturer datasheets
                    if 'datasheet' in text and '.pdf' in href.lower():
                        # Validate it's a real PDF
                        if self._validate_pdf_url(href):
                            logger.info(f"   ✅ Found PDF via DigiKey: {href}")
                            return href
                    
                    # Also check for PDF links without "datasheet" text
                    if '.pdf' in href.lower() and any(mfg in href.lower() for mfg in ['ti.com', 'microchip.com', 'infineon.com', 'onsemi.com']):
                        if self._validate_pdf_url(href):
                            logger.info(f"   ✅ Found manufacturer PDF via DigiKey: {href}")
                            return href
        except Exception as e:
            logger.debug(f"   DigiKey search failed: {e}")
        
        return None
    
    def _search_mouser_pdf(self, part: str) -> Optional[str]:
        """Search Mouser for direct PDF datasheet link"""
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        logger.debug(f"🔍 Mouser search: part={part}, base={base}")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            # Mouser product search
            search_url = f"https://www.mouser.com/c/?q={base}"
            logger.debug(f"   Trying Mouser: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for datasheet PDF links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text().lower()
                    
                    # Mouser links to manufacturer datasheets
                    if ('datasheet' in text or 'pdf' in text) and '.pdf' in href.lower():
                        full_url = href if href.startswith('http') else urljoin('https://www.mouser.com', href)
                        if self._validate_pdf_url(full_url):
                            logger.info(f"   ✅ Found PDF via Mouser: {full_url}")
                            return full_url
        except Exception as e:
            logger.debug(f"   Mouser search failed: {e}")
        
        return None
    
    def _search_alldatasheet_pdf(self, part: str) -> Optional[str]:
        """Search AllDatasheet.com for direct PDF datasheet link"""
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        logger.debug(f"🔍 AllDatasheet search: part={part}, base={base}")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            # AllDatasheet search
            search_url = f"https://www.alldatasheet.com/datasheet-pdf/pdf-searcher.php?sSearchword={base}"
            logger.debug(f"   Trying AllDatasheet: {search_url}")
            response = requests.get(search_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for PDF download links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # AllDatasheet has direct PDF links in format: /datasheet-pdf/pdf/NUMBER/MANUFACTURER/PART.html
                    if '/datasheet-pdf/pdf/' in href or 'download' in href.lower():
                        full_url = href if href.startswith('http') else f"https://www.alldatasheet.com{href}"
                        
                        # Try to extract the actual PDF URL from the download page
                        try:
                            logger.debug(f"   Checking AllDatasheet page: {full_url}")
                            pdf_page = requests.get(full_url, headers=headers, timeout=3)
                            
                            if pdf_page.status_code == 200:
                                pdf_soup = BeautifulSoup(pdf_page.text, 'html.parser')
                                
                                # Look for the actual PDF link
                                for pdf_link in pdf_soup.find_all('a', href=True):
                                    pdf_href = pdf_link['href']
                                    
                                    if '.pdf' in pdf_href.lower() and ('pdf1.alldatasheet.com' in pdf_href or 'pdf.alldatasheet.com' in pdf_href):
                                        if self._validate_pdf_url(pdf_href):
                                            logger.info(f"   ✅ Found PDF via AllDatasheet: {pdf_href}")
                                            return pdf_href
                        except Exception as inner_e:
                            logger.debug(f"   Failed to extract PDF from AllDatasheet page: {inner_e}")
        except Exception as e:
            logger.debug(f"   AllDatasheet search failed: {e}")
        
        return None
    
    def _search_google_pdf(self, part: str, manufacturer: str) -> Optional[str]:
        """Search Google for datasheet PDFs - most powerful fallback"""
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        logger.debug(f"🔍 Google search: part={part}, manufacturer={manufacturer}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Try multiple search engines
        search_engines = [
            ('DuckDuckGo', f"https://duckduckgo.com/html/?q={urllib.parse.quote(f'{manufacturer} {part} datasheet pdf')}"),
            ('Google', f"https://www.google.com/search?q={urllib.parse.quote(f'{manufacturer} {part} datasheet filetype:pdf')}"),
        ]
        
        for engine_name, search_url in search_engines:
            try:
                logger.debug(f"   Trying {engine_name}: {manufacturer} {part} datasheet")
                response = requests.get(search_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for ALL links in the page
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # Extract actual URLs from search engine redirects
                        actual_url = None
                        
                        # Google format: /url?q=URL
                        if '/url?q=' in href:
                            try:
                                actual_url = href.split('/url?q=')[1].split('&')[0]
                                actual_url = urllib.parse.unquote(actual_url)
                            except:
                                continue
                        
                        # DuckDuckGo format: //duckduckgo.com/l/?uddg=URL
                        elif '//duckduckgo.com/l/' in href or 'uddg=' in href:
                            try:
                                actual_url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                            except:
                                continue
                        
                        # Direct link
                        elif href.startswith('http'):
                            actual_url = href
                        
                        # Check if we found a valid PDF URL
                        if actual_url and '.pdf' in actual_url.lower():
                            # Extended trusted domains list
                            trusted_domains = [
                                'infineon.com', 'cypress.com', 'ti.com', 'microchip.com',
                                'nxp.com', 'st.com', 'analog.com', 'onsemi.com',
                                'mouser.com', 'digikey.com', 'alldatasheet.com',
                                'datasheetcatalog.com', 'snapeda.com', 'findchips.com',
                                'element14.com', 'farnell.com', 'newark.com'
                            ]
                            
                            # Check if URL is from a trusted source
                            if any(domain in actual_url.lower() for domain in trusted_domains):
                                logger.debug(f"   Testing PDF from {engine_name}: {actual_url}")
                                # Validate it's a real PDF
                                if self._validate_pdf_url(actual_url):
                                    logger.info(f"   ✅ Found PDF via {engine_name}: {actual_url}")
                                    return actual_url
                    
                    logger.debug(f"   No valid PDF found via {engine_name}")
                    
            except Exception as e:
                logger.debug(f"   {engine_name} search failed: {e}")
                continue
        
        return None
    
    def _search_generic_fallback(self, part: str) -> Optional[str]:
        """Generic fallback search using multiple aggregators and archives"""
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        
        # User agent headers for web scraping
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        # Try SnapEDA (comprehensive datasheets database)
        try:
            logger.debug(f"   Trying SnapEDA...")
            search_url = f"https://www.snapeda.com/parts/{base}/search"
            response = requests.get(search_url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for datasheet links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'datasheet' in href.lower() or '.pdf' in href.lower():
                        full_url = href if href.startswith('http') else f"https://www.snapeda.com{href}"
                        if self._validate_pdf_url(full_url):
                            logger.debug(f"   ✅ Found via SnapEDA: {full_url}")
                            return full_url
        except Exception as e:
            logger.debug(f"   SnapEDA search failed: {e}")
        
        # Try DigiKey's datasheet aggregator (very comprehensive)
        try:
            logger.debug(f"   Trying DigiKey...")
            search_url = f"https://www.digikey.com/en/products/result?keywords={base}"
            response = requests.get(search_url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for datasheet links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text().lower()
                    if 'datasheet' in text and '.pdf' in href.lower():
                        # Validate it's a real PDF
                        if self._validate_pdf_url(href):
                            logger.debug(f"   ✅ Found via DigiKey: {href}")
                            return href
        except Exception as e:
            logger.debug(f"   DigiKey search failed: {e}")
        
        # Try Mouser (distributor with good datasheet links)
        try:
            logger.debug(f"   Trying Mouser...")
            search_url = f"https://www.mouser.com/Semiconductors/_/N-b1yc6?Keyword={base}"
            response = requests.get(search_url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for datasheet links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'datasheet' in href.lower() and '.pdf' in href.lower():
                        full_url = href if href.startswith('http') else f"https://www.mouser.com{href}"
                        if self._validate_pdf_url(full_url):
                            logger.debug(f"   ✅ Found via Mouser: {full_url}")
                            return full_url
        except Exception as e:
            logger.debug(f"   Mouser search failed: {e}")
        
        # Try Octopart search (aggregator with multiple sources)
        try:
            logger.debug(f"   Trying Octopart...")
            search_url = f"https://octopart.com/search?q={base}"
            response = requests.get(search_url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for datasheet links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '.pdf' in href.lower() and 'datasheet' in href.lower():
                        # Validate it's a real PDF
                        if self._validate_pdf_url(href):
                            logger.debug(f"   ✅ Found via Octopart: {href}")
                            return href
        except Exception as e:
            logger.debug(f"   Octopart search failed: {e}")
        
        # Try SnapEDA (electronic parts database with direct datasheet links)
        try:
            logger.debug(f"   Trying SnapEDA...")
            search_url = f"https://www.snapeda.com/search/?q={base}"
            response = requests.get(search_url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for datasheet links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'datasheet' in href.lower() and '.pdf' in href.lower():
                        full_url = href if href.startswith('http') else f"https://www.snapeda.com{href}"
                        if self._validate_pdf_url(full_url):
                            logger.debug(f"   ✅ Found via SnapEDA: {full_url}")
                            return full_url
        except Exception as e:
            logger.debug(f"   SnapEDA search failed: {e}")
        
        # Try FindChips (parts search engine with datasheet links)
        try:
            logger.debug(f"   Trying FindChips...")
            search_url = f"https://www.findchips.com/search/{base}"
            response = requests.get(search_url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for datasheet links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text().lower()
                    if 'datasheet' in text or 'datasheet' in href.lower():
                        if '.pdf' in href.lower():
                            full_url = href if href.startswith('http') else f"https://www.findchips.com{href}"
                            if self._validate_pdf_url(full_url):
                                logger.debug(f"   ✅ Found via FindChips: {full_url}")
                                return full_url
        except Exception as e:
            logger.debug(f"   FindChips search failed: {e}")
        
        # Try Element14 (large distributor with good datasheet database)
        try:
            logger.debug(f"   Trying Element14...")
            search_url = f"https://www.element14.com/community/search.jspa?q={base}"
            response = requests.get(search_url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for datasheet links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'datasheet' in href.lower() and '.pdf' in href.lower():
                        full_url = href if href.startswith('http') else f"https://www.element14.com{href}"
                        if self._validate_pdf_url(full_url):
                            logger.debug(f"   ✅ Found via Element14: {full_url}")
                            return full_url
        except Exception as e:
            logger.debug(f"   Element14 search failed: {e}")
        
        # Try AllDatasheet (comprehensive archive with many legacy parts)
        try:
            logger.debug(f"   Trying AllDatasheet...")
            search_url = f"https://www.alldatasheet.com/datasheet-pdf/pdf-searcher.php?sSearchword={base}"
            response = requests.get(search_url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for PDF download links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # AllDatasheet has direct PDF links in format: /datasheet-pdf/pdf/NUMBER/MANUFACTURER/PART.html
                    if '/datasheet-pdf/pdf/' in href or 'download' in href.lower():
                        full_url = href if href.startswith('http') else f"https://www.alldatasheet.com{href}"
                        # Try to extract the actual PDF URL from the download page
                        try:
                            pdf_page = requests.get(full_url, headers=headers, timeout=3)
                            if pdf_page.status_code == 200:
                                pdf_soup = BeautifulSoup(pdf_page.text, 'html.parser')
                                # Look for the actual PDF link
                                for pdf_link in pdf_soup.find_all('a', href=True):
                                    pdf_href = pdf_link['href']
                                    if '.pdf' in pdf_href.lower() and ('pdf1.alldatasheet.com' in pdf_href or 'pdf.alldatasheet.com' in pdf_href):
                                        if self._validate_pdf_url(pdf_href):
                                            logger.debug(f"   ✅ Found via AllDatasheet: {pdf_href}")
                                            return pdf_href
                        except:
                            pass
        except Exception as e:
            logger.debug(f"   AllDatasheet search failed: {e}")
        
        # Try DatasheetCatalog (another comprehensive archive)
        try:
            logger.debug(f"   Trying DatasheetCatalog...")
            search_url = f"https://www.datasheetcatalog.com/datasheets_pdf/{base[0]}/{base}.shtml"
            response = requests.get(search_url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for PDF links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '.pdf' in href.lower():
                        full_url = href if href.startswith('http') else f"https://www.datasheetcatalog.com{href}"
                        if self._validate_pdf_url(full_url):
                            logger.debug(f"   ✅ Found via DatasheetCatalog: {full_url}")
                            return full_url
        except Exception as e:
            logger.debug(f"   DatasheetCatalog search failed: {e}")
        
        logger.debug(f"   ❌ No datasheet found from any source")
        
        # Try Mouser again with different URL pattern
        try:
            search_url = f"https://www.mouser.com/c/?q={base}"
            response = requests.get(search_url, headers=headers, timeout=3)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for datasheet links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    text = link.get_text().lower()
                    if 'datasheet' in text or 'pdf' in text:
                        if '.pdf' in href.lower():
                            full_url = href if href.startswith('http') else urljoin('https://www.mouser.com', href)
                            if self._validate_pdf_url(full_url):
                                return full_url
        except Exception as e:
            logger.debug(f"Mouser search failed: {e}")
        
        return None
    
    def _search_ti_pdf(self, part: str) -> Optional[str]:
        """Search Texas Instruments for direct PDF link"""
        base = re.sub(r'[^A-Z0-9]', '', part).upper()
        logger.debug(f"🔍 TI search: part={part}, base={base}")
        
        # Handle common OCR errors
        if base.startswith('AUCH'):
            base = 'AUC' + base[4:]  # AUCH16244X → AUC16244X
            logger.debug(f"   AUCH detected, corrected to: {base}")
        
        # Special case for LM556 (dual 555 timer) - comprehensive patterns
        if 'LM556' in base or 'LK556' in base or 'IM556' in base:
            base = 'LM556'
            logger.debug(f"   LM556 detected, normalized to: {base}")
            
            # Add specific LM556 patterns early in the list
            lm556_patterns = [
                "https://www.ti.com/lit/ds/symlink/lm556.pdf",
                "https://www.ti.com/lit/gpn/lm556.pdf",
                "https://www.ti.com/lit/ds/snas545/lm556.pdf",  # Document ID
                "https://www.ti.com/lit/ds/symlink/lm556cn.pdf",
                "https://www.ti.com/lit/ds/symlink/lm556-n.pdf",
                "https://www.ti.com/lit/gpn/lm556cn.pdf",
                "https://www.ti.com/lit/ds/snas545.pdf",  # Document ID without part name
            ]
            
            # Try LM556 specific patterns first
            for url in lm556_patterns:
                logger.debug(f"   LM556 specific: Trying {url}")
                if self._validate_pdf_url(url):
                    logger.info(f"   ✅ Found LM556 PDF: {url}")
                    return url
        
        # Remove package suffixes
        clean = base
        for suffix in ['CCN', 'CN', 'PW', 'PWR', 'DW', 'DR', 'DGK', 'DBV', 'DCK', 'DGV', 'N', 'P', 'D']:
            if clean.endswith(suffix) and len(clean) - len(suffix) >= 3:
                clean = clean[:-len(suffix)]
                logger.debug(f"   Removed suffix '{suffix}': {base} → {clean}")
                break
        
        # For AUC parts, also try without trailing X (AUC16244X → AUC16244)
        clean_no_x = clean[:-1] if clean.startswith('AUC') and clean.endswith('X') and len(clean) > 5 else None
        if clean_no_x:
            logger.debug(f"   AUC part with X suffix: {clean} → {clean_no_x}")
        
        # TI direct PDF patterns with comprehensive variants
        pdf_urls = [
            # LM556 specific patterns (dual 555 timer)
            f"https://www.ti.com/lit/ds/symlink/lm556.pdf" if 'LM556' in base else None,
            f"https://www.ti.com/lit/ds/symlink/lm556cn.pdf" if 'LM556' in base else None,
            f"https://www.ti.com/lit/gpn/lm556.pdf" if 'LM556' in base else None,
            # Standard patterns
            f"https://www.ti.com/lit/ds/symlink/{clean.lower()}.pdf",
            f"https://www.ti.com/lit/gpn/{clean.lower()}.pdf",
            f"https://www.ti.com/lit/ds/symlink/{base.lower()}.pdf",
            f"https://www.ti.com/lit/gpn/{base.lower()}.pdf",
            # Family variants (ADC0831 → adc0831x, adc083x)
            f"https://www.ti.com/lit/ds/symlink/{clean.lower()}x.pdf",
            f"https://www.ti.com/lit/ds/symlink/{clean[:-1].lower()}x.pdf" if len(clean) > 3 else None,
            # Datasheet number patterns (scas, slls, sbas, etc.)
            f"https://www.ti.com/lit/ds/{clean.lower()}.pdf",
            # National Semiconductor legacy (ADC parts) - with -N suffix
            f"https://www.ti.com/lit/ds/symlink/{clean.lower()}-n.pdf",
            f"https://www.ti.com/lit/ds/symlink/{clean.lower()}cn.pdf",
            # For AUC parts - try SN74AUC prefix (with and without X)
            f"https://www.ti.com/lit/ds/symlink/sn74{clean_no_x.lower()}.pdf" if clean_no_x else None,
            f"https://www.ti.com/lit/ds/symlink/sn74{clean.lower()}.pdf" if clean.startswith('AUC') else None,
            f"https://www.ti.com/lit/ds/symlink/sn74{base.lower()}.pdf" if base.startswith('AUC') else None,
            # Try without trailing letters
            f"https://www.ti.com/lit/ds/symlink/{clean[:-1].lower()}.pdf" if len(clean) > 5 and clean[-1].isalpha() else None,
        ]
        
        # Filter out None values
        pdf_urls = [url for url in pdf_urls if url]
        
        logger.debug(f"   Testing {len(pdf_urls)} direct PDF URLs...")
        for i, url in enumerate(pdf_urls, 1):
            logger.debug(f"   [{i}/{len(pdf_urls)}] Trying: {url}")
            if self._validate_pdf_url(url):
                logger.info(f"   ✅ Found TI PDF: {url}")
                return url
            logger.debug(f"   ❌ Not valid")
        
        # Try product pages with more variants
        product_urls = [
            f"https://www.ti.com/product/{clean}",
            f"https://www.ti.com/product/{base}",
            f"https://www.ti.com/product/{clean.lower()}",
            f"https://www.ti.com/product/{base.lower()}",
            # For AUC parts - try with SN74AUC prefix
            f"https://www.ti.com/product/SN74{clean}" if clean.startswith('AUC') else None,
        ]
        
        # Filter None
        product_urls = [url for url in product_urls if url]
        
        logger.debug(f"   Testing {len(product_urls)} product pages...")
        for i, url in enumerate(product_urls, 1):
            logger.debug(f"   [{i}/{len(product_urls)}] Trying: {url}")
            pdf_link = self._extract_pdf_from_page(url)
            if pdf_link:
                logger.info(f"   ✅ Found TI PDF from page: {pdf_link}")
                return pdf_link
            logger.debug(f"   ❌ No PDF found on page")
        
        # Try searching TI documentation directly
        try:
            search_url = f"https://www.ti.com/sitesearch/en-us/docs/universalsearch.tsp?searchTerm={clean}"
            response = self.session.get(search_url, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for PDF links in search results
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '.pdf' in href.lower() and ('lit/ds' in href or 'lit/gpn' in href):
                        full_url = urljoin('https://www.ti.com', href)
                        if self._validate_pdf_url(full_url):
                            return full_url
        except Exception as e:
            logger.debug(f"TI search failed: {e}")
        
        return None
    
    def _search_microchip_pdf(self, part: str) -> Optional[str]:
        """Search Microchip for direct PDF link - prioritize product page scraping"""
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        
        # Handle ATMEL parts (Atmel was acquired by Microchip)
        if base.startswith('ATMEL'):
            atmel_num = base[5:]  # Extract number part (ATMEL426 → 426)
            
            # Try direct Atmel legacy PDF patterns
            atmel_patterns = [
                # Microchip legacy Atmel docs
                f"https://ww1.microchip.com/downloads/en/DeviceDoc/doc{atmel_num}.pdf",
                f"https://ww1.microchip.com/downloads/en/DeviceDoc/atmel-{atmel_num}.pdf",
                f"https://ww1.microchip.com/downloads/en/DeviceDoc/atmel{atmel_num}.pdf",
                f"https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/{base}.pdf",
                f"https://ww1.microchip.com/downloads/en/DeviceDoc/{base}.pdf",
                # Try with AT prefix instead of ATMEL
                f"https://ww1.microchip.com/downloads/en/DeviceDoc/doc{atmel_num}.pdf",
                f"https://ww1.microchip.com/downloads/en/DeviceDoc/AT{atmel_num}.pdf",
                # Legacy Atmel site patterns
                f"http://www.atmel.com/Images/doc{atmel_num}.pdf",
                f"http://www.atmel.com/Images/Atmel-{atmel_num}.pdf",
                # Try with both upper/lower case
                f"https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-{atmel_num}-{base}-Datasheet.pdf",
            ]
            
            for url in atmel_patterns:
                if self._validate_pdf_url(url):
                    logger.info(f"   ✅ Found ATMEL PDF: {url}")
                    return url
            
            # Try product pages (official + third-party)
            product_urls = [
                # Microchip official
                f"https://www.microchip.com/en-us/product/{base}",
                f"https://www.microchip.com/en-us/product/at{atmel_num}",
                f"https://www.microchip.com/en-us/product/AT{atmel_num}",
                # SnapEDA for legacy/discontinued Atmel parts
                f"https://www.snapeda.com/parts/{base}/search",
                f"https://www.snapeda.com/parts/AT{atmel_num}/search",
                # Try AllDatasheet for very old ATMEL parts
                f"https://www.alldatasheet.com/datasheet-pdf/pdf-searcher.php?sSearchword={base}",
            ]
            
            for url in product_urls:
                pdf_link = self._extract_pdf_from_page(url)
                if pdf_link:
                    return pdf_link
        
        # Handle AT24C series (EEPROM memory chips)
        if base.startswith('AT24C') or base.startswith('AT24'):
            # AT24C1024W → try multiple patterns
            clean = re.sub(r'[A-Z]+$', '', base)  # Remove trailing letters
            
            at24_patterns = [
                # Modern Microchip patterns
                f"https://ww1.microchip.com/downloads/en/DeviceDoc/{base}.pdf",
                f"https://ww1.microchip.com/downloads/en/DeviceDoc/{clean}.pdf",
                f"https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/{base}-Data-Sheet.pdf",
                f"https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/{clean}-Data-Sheet.pdf",
                # Legacy Atmel patterns
                f"http://www.atmel.com/Images/{base}.pdf",
                f"http://www.atmel.com/Images/Atmel-{base}.pdf",
            ]
            
            for url in at24_patterns:
                if self._validate_pdf_url(url):
                    logger.info(f"   ✅ Found AT24C PDF: {url}")
                    return url
        
        # Microchip's direct PDF URLs are broken/redirected - go straight to product page
        product_urls = [
            f"https://www.microchip.com/en-us/product/{base}",
            f"https://www.microchip.com/en-us/product/{base.lower()}",
        ]
        
        # For ATMEGA/ATTINY - try without package suffix too
        if base.startswith(('ATMEGA', 'ATTINY', 'ATXMEGA')):
            clean = re.sub(r'[A-Z]+$', '', base) if base[-1].isalpha() else base
            product_urls.append(f"https://www.microchip.com/en-us/product/{clean.lower()}")
        
        # Try product pages first (more reliable than direct PDFs)
        for url in product_urls:
            pdf_link = self._extract_pdf_from_page(url)
            if pdf_link:
                return pdf_link
        
        return None
    
    def _search_infineon_pdf(self, part: str) -> Optional[str]:
        """Search Infineon/Cypress for direct PDF link"""
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        logger.debug(f"🔍 Infineon search: part={part}, base={base}")
        
        # For CY8C (Cypress PSoC)
        if base.startswith('CY8C') or base.startswith('CY7C'):
            # Remove package suffix for better search
            clean = re.sub(r'-\d+[A-Z]+$', '', base)  # CY8C29666-24PVXI → CY8C29666
            logger.debug(f"   CY8C/CY7C detected: clean={clean}")
            
            # PRIORITY: Check for known working URLs FIRST (before Google search)
            known_urls = {
                "CY8C29666": "https://www.infineon.com/assets/row/public/documents/non-assigned/49/infineon-cy8c29466-cy8c29666-automotive-extended-temperature-psoc-programmable-system-on-chip-datasheet-en.pdf?fileId=8ac78c8c7d0d8da4017d0ec676923cae",
                "CY8C29466": "https://www.infineon.com/assets/row/public/documents/non-assigned/49/infineon-cy8c29466-cy8c29666-automotive-extended-temperature-psoc-programmable-system-on-chip-datasheet-en.pdf?fileId=8ac78c8c7d0d8da4017d0ec676923cae",
            }
            
            if clean in known_urls:
                logger.debug(f"   Trying known working URL for {clean}...")
                if self._validate_pdf_url(known_urls[clean]):
                    logger.info(f"   ✅ Found {clean} PDF via known URL!")
                    return known_urls[clean]
            
            # TRY GOOGLE SECOND for other CY8C parts
            logger.debug(f"   Trying Google search for CY8C...")
            google_result = self._search_google_pdf(clean, 'Infineon Cypress')
            if google_result:
                logger.info(f"   ✅ Found CY8C PDF via Google: {google_result}")
                return google_result
            
            # Comprehensive Infineon/Cypress PDF patterns (direct PDFs only)
            pdf_urls = [
                # Try the pattern without fileId parameter (more generic)
                f"https://www.infineon.com/assets/row/public/documents/non-assigned/49/infineon-cy8c29466-{clean.lower()}-automotive-extended-temperature-psoc-programmable-system-on-chip-datasheet-en.pdf",
                # Modern Infineon patterns
                f"https://www.infineon.com/dgdl/Infineon-{clean}-DataSheet-v01_00-EN.pdf",
                f"https://www.infineon.com/dgdl/{clean}-DataSheet.pdf",
                f"https://www.infineon.com/dgdl/Infineon-{base}-DataSheet-v01_00-EN.pdf",
                f"https://www.infineon.com/dgdl/{base}.pdf",
                f"https://www.infineon.com/dgdl/{clean}.pdf",
                # Legacy Cypress patterns (archive)
                f"https://www.cypress.com/file/{clean.lower()}-datasheet",
                f"http://www.cypress.com/file/{clean.lower()}-datasheet",
                f"https://www.cypress.com/file/{clean.lower()}/{clean.lower()}-datasheet.pdf",
                # PSoC-specific patterns
                f"https://www.infineon.com/dgdl/PSoC_{clean}_DataSheet.pdf",
                f"https://www.cypress.com/documentation/datasheets/{clean.lower()}-psoc-programmable-system-chip",
                # Try version variants
                f"https://www.infineon.com/dgdl/Infineon-{clean}-DataSheet-v02_00-EN.pdf",
                f"https://www.infineon.com/dgdl/Infineon-{clean}-DataSheet-v03_00-EN.pdf",
                # Try with family prefix (CY8C2 series → PSoC 1)
                f"https://www.infineon.com/dgdl/{clean}-PSoC-1-Datasheet.pdf",
                # Try Cypress archive site
                f"https://www.cypress.com/file/45906/download",  # CY8C29666 specific
                f"https://www.cypress.com/file/46221/download",  # CY8C series general
            ]
            
            # Filter out None values
            pdf_urls = [url for url in pdf_urls if url]
            
            logger.debug(f"   Testing {len(pdf_urls)} direct PDF URLs...")
            for i, url in enumerate(pdf_urls, 1):
                logger.debug(f"   [{i}/{len(pdf_urls)}] Trying: {url}")
                if self._validate_pdf_url(url):
                    logger.info(f"   ✅ Found CY8C/CY7C PDF: {url}")
                    return url
                logger.debug(f"   ❌ Not valid")
            
            # Try product pages with comprehensive variants (including third-party sites)
            product_urls = [
                # Infineon official
                f"https://www.infineon.com/cms/en/product/{clean.lower()}/",
                f"https://www.infineon.com/cms/en/product/{base.lower()}/",
                f"https://www.infineon.com/cms/en/product/psoc/{clean.lower()}/",
                # Legacy Cypress URLs
                f"https://www.cypress.com/products/{clean.lower()}",
                f"http://www.cypress.com/documentation/datasheets/{clean.lower()}",
                # Try without CY8C prefix (just the number)
                f"https://www.infineon.com/cms/en/product/{clean[4:].lower()}/",
                # SnapEDA for discontinued Cypress parts
                f"https://www.snapeda.com/parts/{clean}/search",
                f"https://www.snapeda.com/parts/{base}/search",
                # Try AllDatasheet for very old Cypress parts
                f"https://www.alldatasheet.com/datasheet-pdf/pdf-searcher.php?sSearchword={clean}",
            ]
            
            logger.debug(f"   Testing {len(product_urls)} product pages...")
            for i, url in enumerate(product_urls, 1):
                logger.debug(f"   [{i}/{len(product_urls)}] Trying: {url}")
                pdf_link = self._extract_pdf_from_page(url)
                if pdf_link:
                    logger.info(f"   ✅ Found CY8C PDF from page: {pdf_link}")
                    return pdf_link
                logger.debug(f"   ❌ No PDF found on page")
            
            # Try Infineon search
            logger.debug(f"   Trying Infineon search...")
            try:
                search_url = f"https://www.infineon.com/cms/en/search.html#!term={clean}&view=all"
                logger.debug(f"   Search URL: {search_url}")
                response = self.session.get(search_url, timeout=self.timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Look for datasheet PDF links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if 'datasheet' in href.lower() and '.pdf' in href.lower():
                            full_url = urljoin('https://www.infineon.com', href)
                            if self._validate_pdf_url(full_url):
                                return full_url
            except Exception as e:
                logger.debug(f"Infineon search failed: {e}")
            
            # Try DigiKey (comprehensive distributor with datasheets)
            logger.debug(f"   Trying DigiKey for CY8C...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                search_url = f"https://www.digikey.com/en/products/result?keywords={clean}"
                response = self.session.get(search_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        text = link.get_text().lower()
                        if 'datasheet' in text and '.pdf' in href.lower():
                            if self._validate_pdf_url(href):
                                logger.info(f"   ✅ Found CY8C PDF via DigiKey: {href}")
                                return href
            except Exception as e:
                logger.debug(f"   DigiKey search failed: {e}")
            
            # Try Mouser (another comprehensive distributor)
            logger.debug(f"   Trying Mouser for CY8C...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                search_url = f"https://www.mouser.com/c/?q={clean}"
                response = self.session.get(search_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if 'datasheet' in href.lower() and '.pdf' in href.lower():
                            full_url = urljoin('https://www.mouser.com', href)
                            if self._validate_pdf_url(full_url):
                                logger.info(f"   ✅ Found CY8C PDF via Mouser: {full_url}")
                                return full_url
            except Exception as e:
                logger.debug(f"   Mouser search failed: {e}")
            
            # Try Octopart (aggregates multiple distributors)
            logger.debug(f"   Trying Octopart for CY8C...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                search_url = f"https://octopart.com/search?q={clean}"
                response = self.session.get(search_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if 'datasheet' in href.lower() or ('infineon.com' in href and '.pdf' in href.lower()):
                            full_url = href if href.startswith('http') else urljoin('https://octopart.com', href)
                            if self._validate_pdf_url(full_url):
                                logger.info(f"   ✅ Found CY8C PDF via Octopart: {full_url}")
                                return full_url
            except Exception as e:
                logger.debug(f"   Octopart search failed: {e}")
            
            # Last resort: Try Google search for discontinued CY8C parts
            logger.debug(f"   Trying Google search for discontinued CY8C...")
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                }
                # Search for datasheet PDFs on Google
                search_url = f"https://www.google.com/search?q={clean}+datasheet+filetype:pdf"
                response = self.session.get(search_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Look for PDF links in search results
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        # Google search result links are in format /url?q=ACTUAL_URL
                        if '/url?q=' in href and '.pdf' in href.lower():
                            # Extract actual URL
                            actual_url = href.split('/url?q=')[1].split('&')[0]
                            actual_url = urllib.parse.unquote(actual_url)
                            # Check if it's from a reliable source
                            if any(domain in actual_url.lower() for domain in ['infineon.com', 'cypress.com', 'mouser.com', 'digikey.com']):
                                if self._validate_pdf_url(actual_url):
                                    logger.info(f"   ✅ Found CY8C PDF via Google: {actual_url}")
                                    return actual_url
            except Exception as e:
                logger.debug(f"   Google search failed: {e}")
        
        # Try generic product page
        product_url = f"https://www.infineon.com/cms/en/product/{base.lower()}/"
        pdf_link = self._extract_pdf_from_page(product_url)
        if pdf_link:
            return pdf_link
        
        return None
    
    def _search_nxp_pdf(self, part: str) -> Optional[str]:
        """Search NXP for direct PDF link"""
        base = re.sub(r'[^A-Z0-9]', '', part).upper()
        
        pdf_urls = [
            f"https://www.nxp.com/docs/en/data-sheet/{base}.pdf",
            f"https://www.nxp.com/docs/en/data-sheet/{base.lower()}.pdf",
        ]
        
        for url in pdf_urls:
            if self._validate_pdf_url(url):
                return url
        
        # Try product page
        product_url = f"https://www.nxp.com/products/{base.lower()}"
        pdf_link = self._extract_pdf_from_page(product_url)
        if pdf_link:
            return pdf_link
        
        return None
    
    def _search_stm_pdf(self, part: str) -> Optional[str]:
        """Search STMicroelectronics for direct PDF link"""
        base = re.sub(r'[^A-Z0-9]', '', part).upper()
        
        # Remove package suffix for M74HC series
        clean = base
        for suffix in ['B1', 'TTR', 'M1', 'N', 'RM13TR', 'RM', 'R']:
            if clean.endswith(suffix) and len(clean) - len(suffix) >= 5:
                clean = clean[:-len(suffix)]
                break
        
        # Try product pages with extensive URL patterns
        product_urls = []
        if base.startswith('M74'):
            product_urls = [
                # Logic comparators
                f"https://www.st.com/en/logic-comparators/{clean.lower()}.html",
                f"https://www.st.com/en/logic-comparators/{base.lower()}.html",
                # General logic
                f"https://www.st.com/en/logic/{clean.lower()}.html",
                f"https://www.st.com/en/logic/{base.lower()}.html",
                # Direct resource patterns
                f"https://www.st.com/resource/en/datasheet/{clean.lower()}.pdf",
                f"https://www.st.com/resource/en/datasheet/{base.lower()}.pdf",
                # CD (datasheet code) patterns
                f"https://www.st.com/resource/en/datasheet/cd00000{clean[4:].lower()}.pdf",
                # Try with "m" prefix removed
                f"https://www.st.com/en/logic-comparators/{clean[1:].lower()}.html",
                f"https://www.st.com/resource/en/datasheet/{clean[1:].lower()}.pdf",
            ]
        elif base.startswith('STM32'):
            product_urls = [
                f"https://www.st.com/en/microcontrollers/{base.lower()}.html",
                f"https://www.st.com/en/microcontrollers/{clean.lower()}.html",
            ]
        else:
            return None
        
        for url in product_urls:
            # Try as PDF first
            if url.endswith('.pdf') and self._validate_pdf_url(url):
                return url
            # Otherwise try extracting from page
            pdf_link = self._extract_pdf_from_page(url)
            if pdf_link:
                return pdf_link
        
        # Try ST search API
        try:
            search_url = f"https://www.st.com/content/st_com/en.search.html#q={clean}&t=tools"
            response = self.session.get(search_url, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for datasheet PDF links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'datasheet' in href.lower() and '.pdf' in href.lower():
                        full_url = urljoin('https://www.st.com', href)
                        if self._validate_pdf_url(full_url):
                            return full_url
        except Exception as e:
            logger.debug(f"STM search failed: {e}")
        
        return None
        
        return None
    
    def _search_analog_pdf(self, part: str) -> Optional[str]:
        """Search Analog Devices for direct PDF link (includes Linear Technology LT series)"""
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        
        # Remove package suffix
        clean = base
        for suffix in ['N', 'P', 'CN', 'D', 'S', 'CJ8']:
            if clean.endswith(suffix) and len(clean) - len(suffix) >= 4:
                clean = clean[:-len(suffix)]
                break
        
        pdf_urls = [
            # Standard patterns
            f"https://www.analog.com/media/en/technical-documentation/data-sheets/{clean}.pdf",
            f"https://www.analog.com/media/en/technical-documentation/data-sheets/{base}.pdf",
            f"https://www.analog.com/media/en/technical-documentation/data-sheets/{clean.lower()}.pdf",
            f"https://www.analog.com/media/en/technical-documentation/data-sheets/{base.lower()}.pdf",
        ]
        
        # For LT series (Linear Technology - now part of Analog Devices)
        if base.startswith('LT'):
            # LT parts have many variant suffixes (fb, fa, fc, etc.)
            for variant in ['', 'fb', 'fa', 'fc', 'f', 'g', 'cj8']:
                pdf_urls.extend([
                    f"https://www.analog.com/media/en/technical-documentation/data-sheets/{clean.lower()}{variant}.pdf",
                    f"https://www.analog.com/media/en/technical-documentation/data-sheets/{base.lower()}{variant}.pdf",
                ])
            
            # Try old Linear Technology domain (still works for some old parts)
            pdf_urls.extend([
                f"https://www.analog.com/media/en/technical-documentation/data-sheets/{clean}.pdf",
                f"https://cds.linear.com/docs/en/datasheet/{clean.lower()}.pdf",
                f"https://cds.linear.com/docs/en/datasheet/{base.lower()}.pdf",
            ])
        
        for url in pdf_urls:
            if self._validate_pdf_url(url):
                return url
        
        # Try product pages as fallback
        product_urls = [
            f"https://www.analog.com/en/products/{clean.lower()}.html",
            f"https://www.analog.com/en/products/{base.lower()}.html",
        ]
        
        for url in product_urls:
            pdf_link = self._extract_pdf_from_page(url)
            if pdf_link:
                return pdf_link
        
        return None
    
    def _search_onsemi_pdf(self, part: str) -> Optional[str]:
        """Search ON Semiconductor for direct PDF link"""
        base = re.sub(r'[^A-Z0-9-]', '', part).upper()
        
        # Remove package suffix
        clean = base
        for suffix in ['B1', 'A', 'D', 'N', 'TTR', 'M1', 'RM13TR']:
            if clean.endswith(suffix) and len(clean) - len(suffix) >= 5:
                clean = clean[:-len(suffix)]
                break
        
        # ON Semi uses different patterns for datasheets
        pdf_urls = [
            # MC74HC series (common logic ICs)
            f"https://www.onsemi.com/pdf/datasheet/{clean.lower()}-d.pdf",
            f"https://www.onsemi.com/pdf/datasheet/{clean.lower()}a-d.pdf",  # "a" version
            f"https://www.onsemi.com/pdf/datasheet/{base.lower()}-d.pdf",
            f"https://www.onsemi.com/pdf/datasheet/{base.lower()}a-d.pdf",
            # Try without suffix
            f"https://www.onsemi.com/pdf/datasheet/{clean.lower()}.pdf",
            f"https://www.onsemi.com/pdf/datasheet/{base.lower()}.pdf",
            # For M74HC -> MC74HC mapping (ST vs ON Semi)
            f"https://www.onsemi.com/pdf/datasheet/mc{clean[1:].lower()}-d.pdf" if clean.startswith('M74') else None,
            f"https://www.onsemi.com/pdf/datasheet/mc{clean[1:].lower()}a-d.pdf" if clean.startswith('M74') else None,  # "a" version
            f"https://www.onsemi.com/pdf/datasheet/mc{clean[1:].lower()}.pdf" if clean.startswith('M74') else None,
        ]
        
        # Remove None values
        pdf_urls = [url for url in pdf_urls if url]
        
        for url in pdf_urls:
            if self._validate_pdf_url(url):
                return url
        
        return None
    
    def _validate_pdf_url(self, url: str) -> bool:
        """Quick validation that URL points to a real PDF"""
        try:
            # Try HEAD first (faster)
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            
            # If HEAD is forbidden (403), try GET with range header (only first bytes)
            if response.status_code == 403:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True, stream=True)
                # Read only first 1KB to check if it's a PDF
                content = next(response.iter_content(1024), b'')
                response.close()
                # Check PDF header
                if content[:4] == b'%PDF':
                    return True
                return False
            
            # Check if it's actually a PDF
            content_type = response.headers.get('Content-Type', '')
            
            if response.status_code == 200:
                # Must be PDF content type
                if 'pdf' in content_type.lower():
                    # Check file size (reasonable PDF: 100KB - 50MB - some datasheets are large!)
                    content_length = int(response.headers.get('content-length', 0))
                    if 100_000 <= content_length <= 50_000_000:
                        return True
                    elif content_length == 0:
                        # No content-length header - might still be valid
                        return True
                    elif content_length < 100_000:
                        # Very small "PDF" - might be a redirect stub (Analog.com does this)
                        # Try a GET request to see if it redirects to real PDF
                        logger.debug(f"      Tiny PDF ({content_length} bytes) - trying GET to check for redirect...")
                        get_response = self.session.get(url, timeout=self.timeout, stream=True, allow_redirects=True)
                        actual_size = int(get_response.headers.get('content-length', 0))
                        actual_type = get_response.headers.get('Content-Type', '')
                        
                        if 'pdf' in actual_type.lower() and actual_size >= 100_000:
                            logger.debug(f"      ✓ Redirected to real PDF ({actual_size} bytes)")
                            get_response.close()
                            return True
                        
                        get_response.close()
                        logger.debug(f"      PDF size out of range: {content_length} bytes")
                    else:
                        logger.debug(f"      PDF size out of range: {content_length} bytes")
                elif 'html' in content_type.lower():
                    # Microchip filehandler returns HTML for HEAD but PDF for GET
                    # Try a partial GET request to verify
                    if 'microchip.com' in url.lower():
                        logger.debug(f"      Microchip redirect - trying GET request...")
                        get_response = self.session.get(url, timeout=self.timeout, stream=True, allow_redirects=True)
                        actual_content_type = get_response.headers.get('Content-Type', '')
                        
                        if 'pdf' in actual_content_type.lower():
                            # It IS a PDF after all!
                            content_length = int(get_response.headers.get('content-length', 0))
                            if 100_000 <= content_length <= 50_000_000 or content_length == 0:
                                logger.debug(f"      ✓ Confirmed PDF via GET")
                                return True
                        
                        # Close the stream
                        get_response.close()
                    
                    logger.debug(f"      Not a PDF: {content_type}")
                else:
                    logger.debug(f"      Not a PDF: {content_type}")
            else:
                logger.debug(f"      HTTP {response.status_code}")
            
            return False
        except Exception as e:
            logger.debug(f"      Validation failed: {e}")
            return False
    
    def _clean_alldatasheet_url(self, url: str) -> str:
        """Clean AllDataSheet viewer URLs to extract actual PDF URL"""
        if 'alldatasheet.com' not in url:
            return url
        
        # Check if it's a viewer URL
        if '/pdfjsview/web/viewer.html' in url:
            # Extract the actual PDF path from the ?file= parameter
            # URL format: https://www.alldatasheet.com/pdfjsview/web/viewer.html?file=//www.alldatasheet.com/datasheet-pdf/view/558226/TI/LM556CN/+_4J_48VRh/1IxNYzHT+/datasheet.pdf
            try:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                params = urllib.parse.parse_qs(parsed.query)
                
                if 'file' in params:
                    file_path = params['file'][0]
                    # file_path is like: //www.alldatasheet.com/datasheet-pdf/view/558226/TI/LM556CN/+_4J_48VRh/1IxNYzHT+/datasheet.pdf
                    if file_path.startswith('//'):
                        # Add https: protocol
                        actual_url = 'https:' + file_path
                    elif file_path.startswith('/'):
                        # Relative path
                        actual_url = 'https://www.alldatasheet.com' + file_path
                    else:
                        # Already has protocol
                        actual_url = file_path
                    
                    # Parse and reconstruct URL to properly encode any spaces or special characters
                    parsed_actual = urllib.parse.urlparse(actual_url)
                    # Split path into segments and encode each one
                    path_parts = parsed_actual.path.split('/')
                    encoded_parts = [urllib.parse.quote(part, safe='') for part in path_parts]
                    encoded_path = '/'.join(encoded_parts)
                    
                    # Reconstruct the URL with encoded path
                    cleaned_url = urllib.parse.urlunparse((
                        parsed_actual.scheme,
                        parsed_actual.netloc,
                        encoded_path,
                        parsed_actual.params,
                        parsed_actual.query,
                        parsed_actual.fragment
                    ))
                    
                    logger.debug(f"   Cleaned AllDataSheet URL: {cleaned_url}")
                    return cleaned_url
            except Exception as e:
                logger.debug(f"   Failed to clean AllDataSheet URL: {e}")
        
        return url
    
    def _extract_pdf_from_page(self, page_url: str) -> Optional[str]:
        """Extract direct PDF download link from product page"""
        try:
            response = self.session.get(page_url, timeout=self.timeout)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for PDF links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # EXCLUDE reliability reports, application notes, evaluation boards
                exclude_patterns = [
                    'reliability-data', 'reliability-report', '/an-', 'application-note',
                    'app-note', 'eval-board', 'reference-design', 'user-guide', 'errata'
                ]
                if any(pattern in href.lower() for pattern in exclude_patterns):
                    continue
                
                # Common datasheet PDF link patterns
                if any(pattern in href.lower() for pattern in [
                    'datasheet', 'data-sheet', 'ds.pdf', 'spec.pdf', 
                    'technical-documentation/data-sheets', 'devicedoc', 'lit/ds'
                ]):
                    # Convert relative URL to absolute
                    full_url = urljoin(page_url, href)
                    
                    # Double-check: must NOT be reliability/app note
                    if any(bad in full_url.lower() for bad in exclude_patterns):
                        continue
                    
                    # Validate it's a real PDF
                    if full_url.endswith('.pdf') and self._validate_pdf_url(full_url):
                        return full_url
            
            return None
        except Exception as e:
            logger.debug(f"      Failed to extract PDF from page: {e}")
            return None
    
    def _extract_pdf_from_alldatasheet(self, url: str) -> Optional[str]:
        """Extract actual PDF URL from AllDataSheet view/download page"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for iframe containing PDF
            for iframe in soup.find_all('iframe', src=True):
                src = iframe['src']
                if '.pdf' in src:
                    return urljoin(url, src)
            
            # Look for direct PDF links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf'):
                    full_url = urljoin(url, href)
                    if self._validate_pdf_url(full_url):
                        return full_url
            
            return None
        except Exception as e:
            logger.debug(f"      Failed to extract from AllDataSheet: {e}")
            return None
    
    def _download_pdf(self, url: str, part_number: str) -> Optional[Path]:
        """Download PDF to cache directory"""
        try:
            logger.debug(f"    Downloading PDF: {url}")
            
            # Shorter timeout for AllDataSheet since it's often down
            timeout = 5 if 'alldatasheet.com' in url.lower() else 10
            
            response = self.session.get(url, timeout=timeout, stream=True)
            
            if response.status_code != 200:
                logger.warning(f"      HTTP {response.status_code}")
                return None
            
            # Check it's actually a PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower():
                logger.warning(f"      Not a PDF: {content_type}")
                return None
            
            # Save to cache
            pdf_path = self.cache_dir / f"{part_number}.pdf"
            
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.debug(f"      ✓ Downloaded: {pdf_path.name} ({pdf_path.stat().st_size // 1024} KB)")
            
            return pdf_path
        except Exception as e:
            logger.warning(f"      Download failed: {e}")
            return None
    
    def _extract_marking_from_pdf(self, pdf_path: Path) -> Optional[Dict]:
        """Extract marking scheme information from PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                # Extract text from first 20 pages (marking info usually in beginning)
                text = ""
                for page_num in range(min(20, len(reader.pages))):
                    text += reader.pages[page_num].extract_text()
                
                # Look for marking scheme information
                marking_info = self._parse_marking_scheme(text)
                
                return marking_info
        except Exception as e:
            logger.debug(f"      Failed to extract marking from PDF: {e}")
            return None
    
    def _parse_marking_scheme(self, pdf_text: str) -> Optional[Dict]:
        """Parse marking scheme from PDF text"""
        # Look for common marking scheme patterns
        marking_patterns = [
            r'package.*mark(?:ing)?.*scheme',
            r'top.*mark(?:ing)?',
            r'device.*mark(?:ing)?',
            r'part.*number.*format',
            r'trace.*code',
            r'date.*code.*format',
            r'lot.*code.*format',
            r'YYWW',  # Common date code format
            r'WW.*YY',  # Week-year format
        ]
        
        # Search for marking scheme sections
        sections = []
        lines = pdf_text.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in marking_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Extract surrounding context (10 lines)
                    start = max(0, i - 5)
                    end = min(len(lines), i + 15)
                    section = '\n'.join(lines[start:end])
                    sections.append(section)
                    break
        
        if sections:
            return {
                'found': True,
                'sections': sections
                # NOTE: Do NOT include raw_text - it causes garbled display in GUI
            }
        
        return None
    
    def _save_metadata(self, pdf_path: Path, url: str, part_number: str, manufacturer: str):
        """Save metadata alongside PDF for future reference"""
        try:
            metadata_path = pdf_path.with_suffix('.json')
            metadata = {
                'url': url,
                'part_number': part_number,
                'manufacturer': manufacturer,
                'downloaded': str(datetime.now())
            }
            import json
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to save metadata: {e}")
    
    def _load_metadata(self, pdf_path: Path) -> Optional[Dict]:
        """Load metadata from JSON file"""
        try:
            metadata_path = pdf_path.with_suffix('.json')
            if metadata_path.exists():
                import json
                with open(metadata_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.debug(f"Failed to load metadata: {e}")
        return None
