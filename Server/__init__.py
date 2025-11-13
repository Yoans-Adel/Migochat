"""
BWW Assistant Server Module
FastAPI-based server for Facebook Messenger Platform integration
"""

__version__ = "1.0.0"
__author__ = "BWW Assistant Team"

from config.settings import settings
from config.config_manager import config_manager, get_config_manager

__all__ = [
    "settings",
    "config_manager",
    "get_config_manager",
]
