"""Unit tests for Playwright runner."""

import pytest
import tempfile
import os
from app.runners.playwright_runner import run_page_smoke, run_yaml_scenario


@pytest.mark.integration
def test_smoke_runner_basic():
    """Test basic smoke runner functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_page_smoke("https://example.com", tmpdir, timeout=15000)
        
        assert result["status"] == "PASS"
        assert result["load_ms"] is not None
        assert result["load_ms"] > 0
        assert len(result["assertions"]) > 0
        assert result["http_status"] == 200
        
        # Check screenshot was created
        assert result["screenshot"] is not None
        assert os.path.exists(result["screenshot"])


@pytest.mark.integration
def test_smoke_runner_assertions():
    """Test that smoke runner performs assertions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_page_smoke("https://example.com", tmpdir)
        
        assertions = result["assertions"]
        assert len(assertions) > 0
        
        # Check for specific assertions
        assertion_names = [a["assert"] for a in assertions]
        assert "title_not_empty" in assertion_names
        assert "has_h1" in assertion_names


@pytest.mark.integration
def test_smoke_runner_invalid_url():
    """Test smoke runner with invalid URL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_page_smoke("https://invalid-url-that-does-not-exist-12345.com", tmpdir, timeout=5000)
        
        assert result["status"] == "ERROR"
        assert result["error"] is not None


@pytest.mark.integration
def test_yaml_scenario_basic():
    """Test YAML scenario execution."""
    scenario = {
        "name": "Test Scenario",
        "steps": [
            {"action": "goto", "url": "https://example.com"},
            {"action": "expect_title", "contains": "Example"},
            {"action": "screenshot", "path": "test.png"}
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_yaml_scenario(scenario, "https://example.com", tmpdir)
        
        assert result["steps_executed"] == 3
        assert result["steps_passed"] > 0
        assert result["name"] == "Test Scenario"


@pytest.mark.integration  
def test_yaml_scenario_with_assertions():
    """Test YAML scenario with assertions."""
    scenario = {
        "name": "Assertion Test",
        "steps": [
            {"action": "goto", "url": "https://example.com"},
            {"action": "expect_text", "selector": "h1", "contains": "Example"}
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_yaml_scenario(scenario, "https://example.com", tmpdir)
        
        assert result["steps_executed"] == 2
        assert result["steps_failed"] == 0

