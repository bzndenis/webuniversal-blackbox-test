"""Unit tests for reporter service."""

import pytest
import tempfile
import os
import json
import csv
from app.services.reporter import (
    generate_html_report,
    generate_csv_report,
    generate_json_report,
    generate_all_reports
)


@pytest.fixture
def sample_results():
    """Sample test results for testing."""
    return [
        {
            "url": "https://example.com",
            "status": "PASS",
            "http_status": 200,
            "load_ms": 1500,
            "console_errors": [],
            "console_warnings": [],
            "network_failures": [],
            "assertions": [
                {"assert": "title_not_empty", "pass": True},
                {"assert": "has_h1", "pass": True}
            ],
            "forms_found": 1,
            "buttons_found": 2,
            "timestamp": "2024-01-01T12:00:00"
        },
        {
            "url": "https://example.com/page2",
            "status": "HTTP_404",
            "http_status": 404,
            "load_ms": 500,
            "console_errors": [{"text": "Error loading resource"}],
            "console_warnings": [],
            "network_failures": [],
            "assertions": [
                {"assert": "title_not_empty", "pass": True}
            ],
            "forms_found": 0,
            "buttons_found": 0,
            "timestamp": "2024-01-01T12:01:00"
        }
    ]


def test_generate_html_report(sample_results):
    """Test HTML report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "report.html")
        generate_html_report(sample_results, output_path, "test_run_123")
        
        assert os.path.exists(output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Black-Box Test Report" in content
            assert "test_run_123" in content
            assert "example.com" in content


def test_generate_csv_report(sample_results):
    """Test CSV report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "report.csv")
        generate_csv_report(sample_results, output_path)
        
        assert os.path.exists(output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            assert len(rows) == 3  # Header + 2 results
            assert rows[0][0] == "URL"
            assert "example.com" in rows[1][0]


def test_generate_json_report(sample_results):
    """Test JSON report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "report.json")
        generate_json_report(sample_results, output_path, "test_run_123")
        
        assert os.path.exists(output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            assert data["run_id"] == "test_run_123"
            assert "summary" in data
            assert "results" in data
            assert len(data["results"]) == 2


def test_generate_all_reports(sample_results):
    """Test generating all report formats."""
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = generate_all_reports(sample_results, tmpdir, "test_run_123")
        
        assert "html" in paths
        assert "csv" in paths
        assert "json" in paths
        
        assert os.path.exists(paths["html"])
        assert os.path.exists(paths["csv"])
        assert os.path.exists(paths["json"])


def test_empty_results():
    """Test report generation with empty results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "report.html")
        generate_html_report([], output_path, "test_run_empty")
        
        assert os.path.exists(output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Black-Box Test Report" in content

