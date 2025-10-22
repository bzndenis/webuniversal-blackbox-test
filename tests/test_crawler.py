"""Unit tests for web crawler."""

import pytest
from app.runners.crawl import crawl_site


@pytest.mark.integration
def test_crawl_basic():
    """Test basic crawling functionality."""
    urls = crawl_site(
        "https://example.com",
        max_depth=1,
        max_pages=5,
        timeout=15
    )
    
    assert len(urls) > 0
    assert "https://example.com" in urls or "https://example.com/" in urls


@pytest.mark.integration
def test_crawl_same_origin():
    """Test same-origin enforcement."""
    urls = crawl_site(
        "https://example.com",
        max_depth=2,
        max_pages=10,
        same_origin_only=True
    )
    
    # All URLs should be from example.com
    for url in urls:
        assert "example.com" in url


def test_crawl_max_pages():
    """Test max pages limit."""
    urls = crawl_site(
        "https://example.com",
        max_depth=3,
        max_pages=3,
        timeout=15
    )
    
    assert len(urls) <= 3


@pytest.mark.integration
def test_crawl_with_patterns():
    """Test include/exclude patterns."""
    urls = crawl_site(
        "https://example.com",
        max_depth=2,
        max_pages=10,
        exclude_patterns=[r'/admin/', r'/login']
    )
    
    # Should not contain admin or login URLs
    for url in urls:
        assert '/admin/' not in url
        assert '/login' not in url

