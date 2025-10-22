"""Unit tests for YAML loader."""

import pytest
import tempfile
import os
from app.services.yaml_loader import (
    load_yaml_spec,
    validate_yaml_spec,
    create_sample_yaml,
    YAMLTestSpec
)


def test_create_sample_yaml():
    """Test sample YAML creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = os.path.join(tmpdir, "sample.yaml")
        create_sample_yaml(yaml_path)
        
        assert os.path.exists(yaml_path)
        
        # Should be able to load it
        spec = load_yaml_spec(yaml_path)
        assert spec.base_url == "https://example.com"
        assert len(spec.scenarios) > 0


def test_load_valid_yaml():
    """Test loading valid YAML spec."""
    yaml_path = "tests/sample_specs/example.yaml"
    
    if os.path.exists(yaml_path):
        spec = load_yaml_spec(yaml_path)
        
        assert isinstance(spec, YAMLTestSpec)
        assert spec.base_url.startswith("http")
        assert len(spec.scenarios) > 0


def test_validate_yaml_spec():
    """Test YAML spec validation."""
    data = {
        "base_url": "https://example.com",
        "scenarios": [
            {
                "name": "Test",
                "steps": [
                    {"action": "goto", "url": "/"}
                ]
            }
        ]
    }
    
    spec = validate_yaml_spec(data)
    assert spec.base_url == "https://example.com"
    assert len(spec.scenarios) == 1


def test_validate_invalid_yaml():
    """Test that invalid YAML raises error."""
    data = {
        "base_url": "not-a-url",  # Invalid URL
        "scenarios": []
    }
    
    with pytest.raises(Exception):
        validate_yaml_spec(data)


def test_yaml_action_validation():
    """Test that invalid actions are caught."""
    data = {
        "base_url": "https://example.com",
        "scenarios": [
            {
                "name": "Test",
                "steps": [
                    {"action": "invalid_action", "url": "/"}
                ]
            }
        ]
    }
    
    with pytest.raises(Exception):
        validate_yaml_spec(data)


def test_yaml_auth_validation_required_fields():
    """Auth enabled must require url and credentials."""
    data = {
        "base_url": "https://example.com",
        "scenarios": [{"name": "Test", "steps": [{"action": "goto", "url": "/"}]}],
        "auth": {"enabled": True}
    }
    with pytest.raises(Exception):
        validate_yaml_spec(data)


def test_yaml_auth_validation_valid():
    """Valid auth block should pass validation."""
    data = {
        "base_url": "https://example.com",
        "scenarios": [{"name": "Test", "steps": [{"action": "goto", "url": "/"}]}],
        "auth": {
            "enabled": True,
            "url": "https://example.com/login",
            "credentials": {"username": "user@example.com", "password": "secret"},
            "success_indicator": "#dashboard"
        }
    }
    spec = validate_yaml_spec(data)
    assert spec.auth and spec.auth.enabled is True
