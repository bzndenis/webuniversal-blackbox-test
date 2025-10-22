"""Pydantic schemas for API and data validation."""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrawlConfig(BaseModel):
    """Configuration for crawling."""
    base_url: HttpUrl
    max_depth: int = Field(default=2, ge=1, le=10)
    max_pages: int = Field(default=50, ge=1, le=500)
    same_origin_only: bool = True
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    timeout: int = Field(default=10, ge=1, le=60)


class TestConfig(BaseModel):
    """Configuration for test execution."""
    headless: bool = True
    timeout: int = Field(default=10000, ge=1000, le=60000)
    take_screenshots: bool = True
    test_forms: bool = False
    yaml_spec_path: Optional[str] = None


class PageResult(BaseModel):
    """Result for a single page test."""
    url: str
    status: str
    http_status: Optional[int] = None
    load_ms: Optional[int] = None
    console_errors: List[Dict[str, Any]] = []
    console_warnings: List[str] = []
    network_failures: List[Dict[str, Any]] = []
    assertions: List[Dict[str, Any]] = []
    forms_found: int = 0
    forms_tested: int = 0
    buttons_found: int = 0
    screenshot: Optional[str] = None
    timestamp: str
    error: Optional[str] = None


class TestRunSummary(BaseModel):
    """Summary of a test run."""
    run_id: str
    total_pages: int
    passed: int
    failed: int
    errors: int
    total_console_errors: int
    total_network_failures: int
    avg_load_time: float
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class TestRunRequest(BaseModel):
    """Request to start a test run."""
    crawl_config: CrawlConfig
    test_config: TestConfig = TestConfig()

