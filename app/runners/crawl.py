"""Web crawler for discovering pages to test."""

from urllib.parse import urljoin, urlparse
from typing import Set, List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
import re
import logging
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from .playwright_runner import perform_login

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def crawl_site(
    base_url: str,
    max_depth: int = 2,
    max_pages: int = 50,
    same_origin_only: bool = True,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    timeout: int = 10,
    auth: Optional[Dict[str, Any]] = None
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
        auth: Authentication configuration untuk login (optional)
        
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


def crawl_site_with_auth(
    base_url: str,
    max_depth: int = 2,
    max_pages: int = 50,
    same_origin_only: bool = True,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    timeout: int = 10,
    auth: Optional[Dict[str, Any]] = None,
    headless: bool = True
) -> List[str]:
    """
    Crawl website dengan authentication menggunakan Playwright.
    
    Args:
        base_url: URL awal untuk mulai crawling
        max_depth: Kedalaman maksimal crawling (default: 2)
        max_pages: Jumlah halaman maksimal yang akan di-crawl (default: 50)
        same_origin_only: Hanya crawl same-origin URLs (default: True)
        include_patterns: List regex patterns untuk include URLs
        exclude_patterns: List regex patterns untuk exclude URLs
        timeout: Request timeout dalam detik (default: 10)
        auth: Authentication configuration untuk login (optional)
        headless: Run browser in headless mode (default: True)
        
    Returns:
        List of URLs yang ditemukan
    """
    visited: Set[str] = set()
    to_visit: List[tuple] = [(base_url, 0)]  # (url, depth)
    found_urls: List[str] = []
    
    # Parse base domain
    base_parsed = urlparse(base_url)
    base_domain = base_parsed.netloc
    
    logger.info(f"Starting authenticated crawl from {base_url}")
    logger.info(f"Max depth: {max_depth}, Max pages: {max_pages}")
    
    try:
        with sync_playwright() as p:
            browser: Browser = p.chromium.launch(headless=headless)
            context: BrowserContext = browser.new_context(
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (compatible; BlackBoxTester/1.0)"
            )
            page: Page = context.new_page()
            page.set_default_timeout(timeout * 1000)
            
            # Perform login if authentication is enabled
            if auth and auth.get("enabled"):
                try:
                    login_url = auth.get("url") or base_url
                    creds = auth.get("credentials", {}) or {}
                    username = creds.get("username") or creds.get("email") or ""
                    password = creds.get("password") or ""
                    success_indicator = auth.get("success_indicator")
                    
                    logger.info("Performing login before crawling")
                    auth_result = perform_login(
                        page=page,
                        login_url=login_url,
                        username=username,
                        password=password,
                        success_indicator=success_indicator,
                        timeout_ms=timeout * 1000,
                    )
                    
                    if not auth_result.get("success", False):
                        logger.warning("Login failed, continuing with unauthenticated crawl")
                    else:
                        logger.info("Login successful, proceeding with authenticated crawl")
                        
                except Exception as e:
                    logger.error(f"Login error: {e}, continuing with unauthenticated crawl")
            
            # Start crawling with authenticated session
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
                    # Navigate to page with authenticated session
                    resp = page.goto(current_url, wait_until="load", timeout=timeout * 1000)
                    
                    if resp and resp.status >= 400:
                        logger.warning(f"Non-200 status for {current_url}: {resp.status}")
                        continue
                    
                    # Get page content and parse links
                    content = page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
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
                
                except Exception as e:
                    logger.error(f"Error crawling {current_url}: {e}")
                    continue
            
            context.close()
            browser.close()
    
    except Exception as e:
        logger.error(f"Crawler error: {e}")
        # Fallback to regular crawling if Playwright fails
        logger.info("Falling back to regular crawling without authentication")
        return crawl_site(
            base_url=base_url,
            max_depth=max_depth,
            max_pages=max_pages,
            same_origin_only=same_origin_only,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            timeout=timeout
        )
    
    logger.info(f"Authenticated crawling complete. Found {len(found_urls)} URLs")
    return found_urls

