"""Web crawler for discovering pages to test."""

from urllib.parse import urljoin, urlparse
from typing import Set, List, Optional
import requests
from bs4 import BeautifulSoup
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def crawl_site(
    base_url: str,
    max_depth: int = 2,
    max_pages: int = 50,
    same_origin_only: bool = True,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    timeout: int = 10
) -> List[str]:
    """
    Crawl website dan kumpulkan daftar URL.
    
    Args:
        base_url: URL awal untuk mulai crawling
        max_depth: Kedalaman maksimal crawling (default: 2)
        max_pages: Jumlah halaman maksimal yang akan di-crawl (default: 50)
        same_origin_only: Hanya crawl same-origin URLs (default: True)
        include_patterns: List regex patterns untuk include URLs
        exclude_patterns: List regex patterns untuk exclude URLs
        timeout: Request timeout dalam detik (default: 10)
        
    Returns:
        List of URLs yang ditemukan
    """
    visited: Set[str] = set()
    to_visit: List[tuple] = [(base_url, 0)]  # (url, depth)
    found_urls: List[str] = []
    
    # Parse base domain
    base_parsed = urlparse(base_url)
    base_domain = base_parsed.netloc
    
    logger.info(f"Starting crawl from {base_url}")
    logger.info(f"Max depth: {max_depth}, Max pages: {max_pages}")
    
    while to_visit and len(found_urls) < max_pages:
        current_url, depth = to_visit.pop(0)
        
        # Skip if already visited or depth exceeded
        if current_url in visited or depth > max_depth:
            continue
        
        # Check include patterns
        if include_patterns:
            if not any(re.search(pattern, current_url) for pattern in include_patterns):
                logger.debug(f"Skipping {current_url} - doesn't match include patterns")
                continue
        
        # Check exclude patterns
        if exclude_patterns:
            if any(re.search(pattern, current_url) for pattern in exclude_patterns):
                logger.debug(f"Skipping {current_url} - matches exclude pattern")
                continue
        
        visited.add(current_url)
        found_urls.append(current_url)
        logger.info(f"[{len(found_urls)}/{max_pages}] Crawling: {current_url} (depth: {depth})")
        
        # Stop crawling deeper if max depth reached
        if depth >= max_depth:
            continue
        
        try:
            # Fetch page
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; BlackBoxTester/1.0)'
            }
            resp = requests.get(current_url, timeout=timeout, headers=headers, allow_redirects=True)
            
            if resp.status_code != 200:
                logger.warning(f"Non-200 status for {current_url}: {resp.status_code}")
                continue
            
            # Only parse HTML content
            content_type = resp.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logger.debug(f"Skipping non-HTML content: {current_url}")
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Convert to absolute URL
                absolute_url = urljoin(current_url, href)
                parsed = urlparse(absolute_url)
                
                # Remove fragments
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_url += f"?{parsed.query}"
                
                # Skip non-http(s) schemes
                if parsed.scheme not in ['http', 'https']:
                    continue
                
                # Same origin check
                if same_origin_only and parsed.netloc != base_domain:
                    continue
                
                # Add to queue if not visited
                if clean_url not in visited and clean_url not in [url for url, _ in to_visit]:
                    to_visit.append((clean_url, depth + 1))
        
        except requests.RequestException as e:
            logger.error(f"Error crawling {current_url}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error crawling {current_url}: {e}")
            continue
    
    logger.info(f"Crawling complete. Found {len(found_urls)} URLs")
    return found_urls

