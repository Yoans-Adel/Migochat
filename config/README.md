# ⚙️ Configuration Package

**Centralized Configuration Management**

---

## 📋 Overview

This package manages all configuration for the application using the **Single Source of Truth** principle. All settings, environment variables, and configuration logic are centralized here.

---

## 🗂️ Package Structure

```
config/
├── .env                     # Environment variables (gitignored) ⚠️
├── .env.example             # Template for environment setup ✅
├── __init__.py              # Package initialization & exports
├── settings.py              # Main settings API (property-based)
├── config_manager.py        # Configuration loader & validator
├── database_config.py       # Database configuration wrapper
└── logging_config.py        # Centralized logging setup
```

### File Purposes

| File | Purpose | Usage |
|------|---------|-------|
| **`.env`** | Actual secrets & config | Never commit! |
| **`.env.example`** | Template for team | Safe to commit |
| **`settings.py`** | Settings access layer | Import in code |
| **`config_manager.py`** | Loads from .env | Auto-loaded |
| **`database_config.py`** | Database setup | Import models |
| **`logging_config.py`** | Logging setup | Auto-configured |

---

## 🚀 Quick Start

### First Time Setup

```powershell
# 1. Copy environment template
Copy-Item config\.env.example config\.env

# 2. Edit configuration with your values
notepad config\.env

# 3. Fill in required credentials:
#    - Facebook: FB_APP_ID, FB_APP_SECRET, FB_PAGE_ACCESS_TOKEN
#    - WhatsApp: WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID
#    - AI: GEMINI_API_KEY
```

### Verify Configuration

```powershell
# Test that configuration loads correctly
python -c "from config.settings import settings; print(f'✅ Config loaded: App ID={settings.FB_APP_ID}')"
```

---

## 💻 Usage in Code

### Import Settings (Recommended)

```python
from config.settings import settings

# Access configuration properties
app_id = settings.FB_APP_ID
gemini_key = settings.GEMINI_API_KEY
port = settings.PORT
debug = settings.DEBUG
```

### Import Database Models

```python
from config.database_config import User, Message, Conversation
from config.database_config import get_session, check_database_health

# Use models in your code
with get_session() as session:
    users = session.query(User).all()
```

### Advanced Configuration Manager

```python
from config.config_manager import config_manager

# Get entire configuration section
fb_config = config_manager.get_facebook_config()
whatsapp_config = config_manager.get_whatsapp_config()

# Get specific value with default
api_key = config_manager.get_config("ai", "gemini_api_key", default="fallback")
```

---

## 📖 Configuration Reference

### Configuration Sections

The configuration is organized into logical sections:

#### Facebook Integration
- App credentials (ID, Secret)
- Page tokens and IDs
- Webhook verification tokens

#### WhatsApp Integration
- API tokens
- Phone number IDs
- Webhook verification

#### AI Services
- Gemini API configuration
- Model selection

#### Application Settings
- Environment (development/production)
- Debug mode
- Logging configuration
- Server settings

#### Database
- Connection strings
- SQLite/PostgreSQL support

**See `.env.example` for complete list of all available variables.**

---

## 🔒 Security Best Practices

### ⚠️ NEVER Commit These Files:
- `config/.env` - Contains actual secrets
- Any file with real API keys or tokens
- Backup files with sensitive data

### ✅ Safe to Commit:
- `config/.env.example` - Template only (no real secrets)
- All `.py` configuration files
- This README

### 🛡️ Protection Setup

The `.gitignore` is already configured:
```gitignore
# Environment files
.env
.env.*
config/.env

# Allow template
!config/.env.example
```

---

## 🎯 Architecture & Design

### Single Source of Truth Principle

All configuration flows through one clear path:

```
.env file → config_manager.py → settings.py → Your Code
```

**Benefits:**
- ✅ No duplicate configuration
- ✅ Centralized validation
- ✅ Type-safe access via properties
- ✅ Easy to test and mock
- ✅ Clear dependency injection

### Configuration Layers

```
┌─────────────────────────────────────┐
│         Your Application            │
│  (app/, routes/, services/)         │
└───────────────┬─────────────────────┘
                │ from config.settings import settings
                ↓
┌─────────────────────────────────────┐
│       settings.py (API Layer)       │
│    Property-based type-safe access  │
└───────────────┬─────────────────────┘
                │
                ↓
┌─────────────────────────────────────┐
│   config_manager.py (Loader)        │
│    Loads, validates, caches config  │
└───────────────┬─────────────────────┘
                │ load_dotenv()
                ↓
┌─────────────────────────────────────┐
│       config/.env (Storage)         │
│      Single source of truth         │
└─────────────────────────────────────┘
```

### Type Safety

The `settings.py` module provides full type safety:

```python
# Type-safe property access
app_id: str = settings.FB_APP_ID        # Returns str
port: int = settings.PORT               # Returns int
debug: bool = settings.DEBUG            # Returns bool

# No need for manual type conversion!
```

---

## 🧪 Validation & Testing

### Configuration Validation

```python
from config.settings import settings

# Validate all required settings
missing_fields = settings.validate_required_settings()

if missing_fields:
    print(f"❌ Missing configuration: {', '.join(missing_fields)}")
else:
    print("✅ All configuration valid!")
```

### Health Check

```python
from config.config_manager import config_manager

# Check configuration health
summary = config_manager.get_configuration_summary()
print(summary)
```

### Testing

Run configuration tests:
```powershell
pytest tests/test_config.py -v
```

All tests should pass (14/14):
```
✅ test_config_import
✅ test_config_has_required_fields
✅ test_config_manager_loads
✅ test_database_url_format
✅ test_debug_mode_is_boolean
✅ test_api_keys_are_strings
✅ test_whatsapp_config_complete
✅ test_env_file_exists
✅ test_config_validation
✅ test_load_configuration
✅ test_get_config
✅ test_configuration_is_cached
✅ test_messenger_api_url
✅ test_whatsapp_api_version
```

---

## 🌍 Environment Support

### Development
- Set `DEBUG=True` in `.env`
- Use local database or development database
- Webhook URLs point to ngrok or local tunnel

### Production
- Set `DEBUG=False` and `ENVIRONMENT=production`
- Use production database credentials
- Webhook URLs point to production domain

### Dynamic Configuration
```python
from config.settings import settings

# Update webhooks dynamically
settings.update_webhook_urls("https://your-domain.com")
```

---

## 🔧 Common Issues & Solutions

### Issue: "Token not found" or Empty Configuration

**Cause:** `config/.env` file doesn't exist or is empty

**Solution:**
```powershell
# Copy template
Copy-Item config\.env.example config\.env

# Edit with your actual values
notepad config\.env
```

---

### Issue: ImportError: cannot import name 'settings'

**Cause:** Wrong import path

**Fix:**
```python
# ❌ Wrong (old structure)
from app.config import settings
from Server.config import settings

# ✅ Correct (current structure)
from config.settings import settings
```

---

### Issue: Configuration not loading

**Cause:** ConfigManager couldn't find `config/.env`

**Verify:**
```powershell
# Check file exists
Test-Path config\.env   # Should return True

# Test configuration loading
python -c "from config.config_manager import config_manager; print(config_manager.load_configuration())"
```

---

### Issue: Validation fails on startup

**Cause:** Missing required environment variables

**Debug:**
```python
from config.settings import settings

# Check which fields are missing
missing = settings.validate_required_settings()
print(f"Missing fields: {missing}")
```

**Fix:** Add missing values to `config/.env`

---

## 📚 API Reference

### `settings.py`

Property-based settings access:

```python
from config.settings import settings

# Facebook properties
settings.FB_APP_ID: str
settings.FB_APP_SECRET: str
settings.FB_PAGE_ACCESS_TOKEN: str
settings.FB_VERIFY_TOKEN: str

# WhatsApp properties
settings.WHATSAPP_ACCESS_TOKEN: str
settings.WHATSAPP_PHONE_NUMBER_ID: str

# AI properties
settings.GEMINI_API_KEY: str
settings.GEMINI_MODEL: str

# Application properties
settings.DEBUG: bool
settings.PORT: int
settings.ENVIRONMENT: str
settings.LOG_LEVEL: str

# Methods
settings.validate_required_settings() -> List[str]
settings.update_webhook_urls(base_url: str) -> None
```

### `config_manager.py`

Configuration management:

```python
from config.config_manager import config_manager

# Load configuration
config_manager.load_configuration() -> bool

# Validate configuration
config_manager.validate_configuration() -> List[str]

# Get configuration
config_manager.get_config(section: str, key: str = None, default: Any = None) -> Any

# Section getters
config_manager.get_facebook_config() -> Dict[str, str]
config_manager.get_whatsapp_config() -> Dict[str, str]
config_manager.get_ai_config() -> Dict[str, str]
config_manager.get_app_config() -> Dict[str, Any]

# Update webhooks
config_manager.update_webhook_urls(base_url: str) -> None

# Status checks
config_manager.is_loaded() -> bool
config_manager.is_validated() -> bool
config_manager.get_configuration_summary() -> Dict[str, Any]
```

### `database_config.py`

Database configuration & models:

```python
from config.database_config import (
    # Models
    User, Message, Conversation, LeadActivity,
    Post, AdCampaign, AppSettings,
    
    # Enums
    MessageDirection, MessageStatus, MessageSource,
    LeadStage, CustomerLabel, CustomerType,
    PostType, Governorate,
    
    # Utilities
    get_session, create_database, drop_database,
    backup_database, restore_database,
    check_database_health,
    
    # SQLAlchemy
    engine, SessionLocal, Base
)
```

---

## 📝 Best Practices

### ✅ DO:

1. **Use `config.settings` for all configuration access**
   ```python
   from config.settings import settings
   api_key = settings.GEMINI_API_KEY  # Type-safe!
   ```

2. **Keep `config/.env` with actual secrets (gitignored)**
   ```bash
   # This file is automatically ignored by git
   config/.env
   ```

3. **Update `.env.example` when adding new variables**
   ```dotenv
   # Add new variable to .env.example (without real value)
   NEW_API_KEY=your_key_here
   ```

4. **Validate configuration on application startup**
   ```python
   from config.settings import settings
   
   missing = settings.validate_required_settings()
   if missing:
       raise RuntimeError(f"Missing config: {missing}")
   ```

5. **Use environment-specific settings**
   ```python
   if settings.ENVIRONMENT == "production":
       # Production logic
   else:
       # Development logic
   ```

### ❌ DON'T:

1. **Don't use `os.getenv()` directly in application code**
   ```python
   # ❌ Bad
   import os
   api_key = os.getenv("GEMINI_API_KEY")
   
   # ✅ Good
   from config.settings import settings
   api_key = settings.GEMINI_API_KEY
   ```

2. **Don't hardcode credentials in code**
   ```python
   # ❌ Very bad!
   API_KEY = "AIzaSyC..."
   
   # ✅ Good
   api_key = settings.GEMINI_API_KEY
   ```

3. **Don't commit `config/.env` to version control**
   ```bash
   # Already protected by .gitignore
   # Never force add: git add -f config/.env  ❌
   ```

4. **Don't create duplicate configuration files**
   ```
   ❌ .env
   ❌ .env.local
   ❌ .env.development
   ❌ config.json
   
   ✅ config/.env (single source of truth)
   ```

---

## 🔄 Migration History

### Previous Structure (Removed)
```
Server/
├── config.py              ❌ Moved to config/settings.py
└── config_manager.py      ❌ Moved to config/config_manager.py

app/
└── config.py              ❌ Removed (duplicate)

config/
└── database_config.py     ❌ Had duplicate models (now wrapper)
```

### Current Structure (Clean)
```
config/
├── .env                   ✅ Single source of truth
├── settings.py            ✅ Main API
├── config_manager.py      ✅ Loader
├── database_config.py     ✅ Clean wrapper
└── logging_config.py      ✅ Logging setup
```

### Import Updates
All code now uses:
```python
from config.settings import settings  # ✅ Standard everywhere
```

---

## 🎓 Related Documentation

- **`.env.example`** - Template file with all configuration variables
- **`__init__.py`** - Package documentation with architecture details
- Python documentation for `dotenv`, `typing`, and configuration patterns

### Configuration Testing

```bash
# Run all configuration tests
pytest tests/test_config.py -v

# Test specific configuration aspect
pytest tests/test_config.py::TestServerConfig -v
```

---

## ✅ Package Status

- **Version**: 2.0.0
- **Tests**: ✅ 14/14 passing
- **Type Safety**: ✅ Full typing support
- **Documentation**: ✅ Complete

---

**Remember:** This package is the **SINGLE SOURCE OF TRUTH** for all configuration! 🎯
