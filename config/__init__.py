"""
⚙️ Migochat Configuration Package
==================================

Centralized configuration management for the Migochat application.

This package provides a **Single Source of Truth** for all application settings,
following industry best practices for configuration management, security, and
dependency injection.

Architecture
------------
The configuration system is built on three layers:

1. **Storage Layer** (`config/.env`)
   - Environment variables and secrets
   - Git-ignored for security
   - Template provided via `.env.example`

2. **Loader Layer** (`config_manager.py`)
   - Loads configuration from .env file
   - Validates required fields
   - Caches configuration in memory
   - Provides typed access methods

3. **API Layer** (`settings.py`)
   - Property-based type-safe access
   - Clean interface for application code
   - Auto-completion support in IDEs

Quick Start
-----------
```python
from config.settings import settings

# Type-safe property access
app_id = settings.FB_APP_ID           # str
port = settings.PORT                  # int
debug = settings.DEBUG                # bool
```

Database Access
---------------
```python
from config.database_config import User, Message, get_session

# Use database models
with get_session() as session:
    users = session.query(User).all()
```

Advanced Usage
--------------
```python
from config.config_manager import config_manager

# Get entire configuration section
fb_config = config_manager.get_facebook_config()

# Validate configuration
missing = config_manager.validate_configuration()
if missing:
    raise RuntimeError(f"Missing config: {missing}")
```

Modules
-------
- **settings**: Main configuration API (use this in your code)
- **config_manager**: Configuration loader and validator
- **database_config**: Database models and session management
- **logging_config**: Centralized logging configuration

Security
--------
⚠️ NEVER commit `config/.env` - it contains secrets!
✅ Always use `config/.env.example` as template

See Also
--------
- README.md: Complete configuration documentation
- .env.example: Configuration template with all variables
"""

# =============================================================================
# Configuration Modules
# =============================================================================

from . import config_manager
from . import database_config
from . import logging_config
from . import settings_manager

# =============================================================================
# Settings API (Primary Interface)
# =============================================================================

from .settings import settings

# =============================================================================
# Settings Manager (Database-backed Dynamic Settings)
# =============================================================================

from .settings_manager import (
    SettingsManager,
    get_settings_manager,
)

# =============================================================================
# Configuration Manager Functions (Advanced Usage)
# =============================================================================

from .config_manager import (
    config_manager as get_config_manager,
    get_config,
    load_configuration,
    validate_configuration,
)

# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Primary API (Most Common Usage)
    "settings",
    
    # Settings Manager (DB-backed)
    "settings_manager",
    "SettingsManager",
    "get_settings_manager",
    
    # Configuration Manager
    "config_manager",
    "get_config_manager",
    "get_config",
    "load_configuration",
    "validate_configuration",
    
    # Module Imports
    "database_config",
    "logging_config",
]

# Package Metadata
__version__ = "2.0.0"
__author__ = "Migochat Team"
__description__ = "Centralized configuration management for Migochat"
