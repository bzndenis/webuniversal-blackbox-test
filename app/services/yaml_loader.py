"""YAML test scenario loader with validation."""

import yaml
from pydantic import BaseModel, Field
from pydantic import field_validator, model_validator
from pydantic.config import ConfigDict
from typing import List, Dict, Any, Optional, Union
import os


class YAMLStep(BaseModel):
    """Single test step in a YAML scenario."""
    action: str
    url: Optional[str] = None
    selector: Optional[str] = None
    value: Optional[str] = None
    key: Optional[str] = None
    path: Optional[str] = None
    equals: Optional[Union[str, int]] = None
    contains: Optional[str] = None
    ms: Optional[int] = None
    
    # For expect_status
    status_in: Optional[List[int]] = Field(None, alias='in')
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        """Validate action type."""
        valid_actions = [
            'goto', 'click', 'fill', 'press', 'screenshot',
            'expect_title', 'expect_text', 'expect_status',
            'wait'
        ]
        if v not in valid_actions:
            raise ValueError(f"Invalid action: {v}. Must be one of {valid_actions}")
        return v
    
    model_config = ConfigDict(populate_by_name=True)


class YAMLScenario(BaseModel):
    """Test scenario with multiple steps."""
    name: str
    steps: List[YAMLStep]


class YAMLAuth(BaseModel):
    """Authentication configuration."""
    enabled: bool = False
    url: Optional[str] = None
    credentials: Optional[Dict[str, str]] = None
    success_indicator: Optional[str] = None

    @model_validator(mode='after')
    def validate_auth(self):
        """Ensure required fields exist when auth is enabled."""
        if self.enabled:
            if not self.url:
                raise ValueError("auth.url is required when auth.enabled is true")
            creds = self.credentials or {}
            if not creds:
                raise ValueError("auth.credentials is required when auth.enabled is true")
            if not (creds.get('username') or creds.get('email')):
                raise ValueError("auth.credentials must include 'username' or 'email'")
            if not creds.get('password'):
                raise ValueError("auth.credentials must include 'password'")
        return self


class YAMLTestSpec(BaseModel):
    """Complete YAML test specification."""
    base_url: str
    scenarios: List[YAMLScenario]
    auth: Optional[YAMLAuth] = None
    
    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v):
        """Validate base URL format."""
        if not v.startswith('http://') and not v.startswith('https://'):
            raise ValueError("base_url must start with http:// or https://")
        return v


def load_yaml_spec(file_path: str) -> YAMLTestSpec:
    """
    Load and validate YAML test specification.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Validated YAMLTestSpec object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    try:
        spec = YAMLTestSpec(**data)
        return spec
    except Exception as e:
        raise ValueError(f"Invalid YAML spec: {e}")


def validate_yaml_spec(data: Dict[str, Any]) -> YAMLTestSpec:
    """
    Validate YAML spec from dictionary.
    
    Args:
        data: Dictionary containing YAML data
        
    Returns:
        Validated YAMLTestSpec object
    """
    return YAMLTestSpec(**data)


def create_sample_yaml(output_path: str) -> None:
    """
    Create a sample YAML test specification file.
    
    Args:
        output_path: Path where to save sample YAML
    """
    sample = {
        'base_url': 'https://example.com',
        'scenarios': [
            {
                'name': 'Homepage basic check',
                'steps': [
                    {'action': 'goto', 'url': '/'},
                    {'action': 'expect_title', 'contains': 'Example'},
                    {'action': 'expect_text', 'selector': 'h1', 'contains': 'Example'},
                    {'action': 'screenshot', 'path': 'homepage.png'}
                ]
            },
            {
                'name': 'Link navigation test',
                'steps': [
                    {'action': 'goto', 'url': '/'},
                    {'action': 'click', 'selector': 'a'},
                    {'action': 'expect_status', 'in': [200, 301, 302]},
                    {'action': 'screenshot', 'path': 'after_click.png'}
                ]
            }
        ],
        'auth': {
            'enabled': False,
            'url': 'https://example.com/login',
            'credentials': {
                'username': 'user@example.com',
                'password': 'secret'
            },
            'success_indicator': '#dashboard, text=Dashboard'
        }
    }
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(sample, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

