# ⚙️ Configuration Package

**Single Source of Truth for All Application Settings**

---

## 📦 Package Structure

```
config/
├── .env                     # Your secrets (NEVER commit!)
├── .env.example             # Template (safe to share)
│
├── settings.py              # 🎯 Main API - Use This!
├── config_manager.py        # Loads from .env file
├── settings_manager.py      # Loads from database (dynamic)
│
├── database_config.py       # Database models re-export
├── logging_config.py        # Logging configuration
└── __init__.py             # Package exports
```

---

## 🎯 Quick Start (The Only Import You Need)

```python
from config import settings

# Access any setting
api_key = settings.GEMINI_API_KEY      # str
port = settings.PORT                    # int
debug = settings.DEBUG                  # bool
```

**That's it!** 99% of the time, you only need `settings`.

---

## 🏗️ Architecture Overview

### Three Configuration Layers:

#### 1️⃣ **Static Settings** (Environment Variables)
- **File**: `config/settings.py`
- **Source**: `config/.env` file
- **Usage**: App-wide constants (API keys, ports, etc.)
- **Changes**: Requires restart

```python
from config import settings
print(settings.FB_APP_ID)  # From .env
```

#### 2️⃣ **Dynamic Settings** (Database-Backed)
- **File**: `config/settings_manager.py`
- **Source**: `app_settings` database table
- **Usage**: Admin-editable runtime settings
- **Changes**: Live updates (no restart)

```python
from config import get_settings_manager

manager = get_settings_manager()
value = manager.get_setting("CUSTOM_FEATURE_FLAG")
manager.set_setting("THEME", "dark")
```

#### 3️⃣ **Configuration Loader** (Internal)
- **File**: `config/config_manager.py`
- **Purpose**: Parses `.env` file into sections
- **Usage**: Internal (used by `settings.py`)

**You don't need to use this directly!**

---

## 🔥 Common Use Cases

### ✅ Get API Keys/Tokens
```python
from config import settings

# Facebook
fb_token = settings.FB_PAGE_ACCESS_TOKEN
fb_app_id = settings.FB_APP_ID

# WhatsApp
wa_token = settings.WHATSAPP_ACCESS_TOKEN

# Gemini AI
ai_key = settings.GEMINI_API_KEY
```

### ✅ Database Access
```python
from config.database_config import User, Message, get_session

with get_session() as db:
    users = db.query(User).all()
```

### ✅ Dynamic Settings (Admin Features)
```python
from config import get_settings_manager

manager = get_settings_manager()

# Get with fallback
theme = manager.get_setting("UI_THEME", default="light")

# Update setting
manager.set_setting(
    key="MAINTENANCE_MODE",
    value="false",
    category="system",
    description="Enable maintenance mode"
)

# Get all settings by category
ai_settings = manager.get_all_settings(category="ai")
```

### ✅ Validation
```python
from config import settings

# Check for missing config
missing = settings.validate_required_settings()
if missing:
    print(f"❌ Missing: {', '.join(missing)}")
```

---

## 📋 Configuration Files

### `.env` File Structure

```dotenv
# Facebook Configuration
FB_APP_ID=your_app_id
FB_APP_SECRET=your_secret
FB_PAGE_ACCESS_TOKEN=your_token
FB_PAGE_ID=your_page_id
FB_VERIFY_TOKEN=your_verify_token

# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN=your_wa_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=your_wa_verify

# AI Configuration
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash

# Application Settings
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
TIMEZONE=Africa/Cairo
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///database/migochat.db
```

**See `.env.example` for complete template!**

---

## 🔑 Settings Priority

When getting a setting value:

```
Database Settings (highest priority)
         ↓
  Environment (.env file)
         ↓
    Hard-coded Defaults (lowest)
```

Example:
```python
# If "GEMINI_API_KEY" exists in database → use that
# Else if in .env → use .env value
# Else → use default ""
```

---

## 🎨 Type Safety

All settings have proper type hints:

```python
from config import settings

# IDE auto-completion works!
settings.FB_APP_ID           # → str
settings.FB_PAGE_ID          # → str
settings.PORT                # → int
settings.DEBUG               # → bool
settings.GEMINI_MODEL        # → str
```

No manual type casting needed!

---

## 🔒 Security Best Practices

### ⚠️ NEVER Commit:
- ❌ `config/.env` (contains secrets!)
- ❌ Any file with real API keys
- ❌ Database files with sensitive data

### ✅ Safe to Commit:
- ✅ `config/.env.example` (template only)
- ✅ All `.py` files in config/
- ✅ This README

**`.gitignore` already protects `.env` for you!**

---

## 🛠️ Setup Instructions

### First Time Setup

```powershell
# 1. Copy template
Copy-Item config\.env.example config\.env

# 2. Edit with your credentials
notepad config\.env

# 3. Verify setup
python -c "from config import settings; print('✅ Config OK!')"
```

### Required Settings

Must fill these in `.env`:

- **Facebook**: `FB_APP_ID`, `FB_PAGE_ACCESS_TOKEN`
- **WhatsApp**: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`
- **AI**: `GEMINI_API_KEY`

---

## 🧪 Testing

```bash
# Run config tests
pytest tests/test_config.py -v

# Should pass all tests ✅
```

---

## 📊 Available Settings

### settings.py Properties

```python
# Facebook
settings.FB_APP_ID: str
settings.FB_APP_SECRET: str
settings.FB_PAGE_ACCESS_TOKEN: str
settings.FB_PAGE_ID: str
settings.FB_VERIFY_TOKEN: str

# WhatsApp
settings.WHATSAPP_ACCESS_TOKEN: str
settings.WHATSAPP_PHONE_NUMBER_ID: str
settings.WHATSAPP_VERIFY_TOKEN: str

# AI
settings.GEMINI_API_KEY: str
settings.GEMINI_MODEL: str

# Application
settings.DEBUG: bool
settings.ENVIRONMENT: str
settings.LOG_LEVEL: str
settings.TIMEZONE: str
settings.HOST: str
settings.PORT: int

# Database
settings.DATABASE_URL: str
```

### settings_manager Methods

```python
manager = get_settings_manager()

# Get setting
manager.get_setting(key: str, default: str = "") -> str

# Set setting
manager.set_setting(
    key: str,
    value: str,
    category: str = "system",
    is_sensitive: bool = False,
    description: str = "",
    updated_by: str = "admin"
) -> bool

# Get all settings
manager.get_all_settings(category: Optional[str] = None) -> List[Dict]

# Delete setting
manager.delete_setting(key: str) -> bool

# Initialize defaults
manager.initialize_default_settings() -> None
```

---

## 🔗 Related Documentation

- **Package Docs**: See `config/__init__.py` for detailed architecture
- **API Reference**: Check individual module docstrings
- **Environment Template**: See `.env.example` for all variables

---

## 💡 Best Practices

### ✅ DO:

```python
# Use settings object
from config import settings
api_key = settings.GEMINI_API_KEY

# Use database for dynamic config
from config import get_settings_manager
manager = get_settings_manager()
feature_flag = manager.get_setting("NEW_FEATURE")
```

### ❌ DON'T:

```python
# Don't use os.getenv directly
import os
api_key = os.getenv("GEMINI_API_KEY")  # ❌

# Don't hardcode secrets
API_KEY = "sk-abc123..."  # ❌ NEVER!

# Don't bypass settings
from config.config_manager import config_manager
val = config_manager.get_config("ai", "gemini_api_key")  # ❌ Use settings instead
```

---

## 🚨 Troubleshooting

### "Setting not found"
```powershell
# Verify .env exists
Test-Path config\.env

# Check content
Get-Content config\.env
```

### "Import error"
```python
# ✅ Correct
from config import settings

# ❌ Wrong
from app.config import settings
from Server.config import settings
```

### "Database settings not saving"
```python
# Make sure database is initialized
from database import create_all_tables
create_all_tables()

# Then try again
from config import get_settings_manager
manager = get_settings_manager()
manager.initialize_default_settings()
```

---

## 📈 Version History

- **v2.0.0**: Added `settings_manager.py` for DB-backed settings
- **v1.0.0**: Initial release with `settings.py` and `config_manager.py`

---

**🎯 Remember: Use `from config import settings` for everything!**
