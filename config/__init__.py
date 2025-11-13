"""
Configuration Package

This package contains all configuration modules for the application.
"""

from typing import Any

# Import config modules
from . import database_config
from . import logging_config

__all__ = [
    "database_config",
    "logging_config",
]


def get_config(key: str) -> Any:
    """
    Get configuration value by key.
    
    Args:
        key: Configuration key
        
    Returns:
        Configuration value
    """
    # Placeholder for dynamic config loading
    pass
