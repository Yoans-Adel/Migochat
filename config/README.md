# ⚙️ Configuration Package

> **Centralized configuration management for the application**

---

## 📦 What's This?

This package handles **all** application configuration in one place. No scattered settings, no duplicate configs - just one source of truth.

---

## 📁 Package Contents

```
config/
├── .env                   # Your actual configuration (never commit!)
├── .env.example           # Template file (safe to share)
├── settings.py            # Main API - use this in your code
├── config_manager.py      # Loads & validates configuration
├── database_config.py     # Database models & utilities
├── logging_config.py      # Logging setup
└── __init__.py           # Package exports
```

| File | What It Does |
|------|-------------|
| `.env` | Contains your actual API keys, tokens, and secrets |
| `.env.example` | Template showing what variables are needed |
| `settings.py` | Property-based API for accessing configuration |
| `config_manager.py` | Loads `.env` file and organizes config into sections |
| `database_config.py` | Re-exports database models from `database/` package |
| `logging_config.py` | Sets up rotating log files for different components |

---

## 🚀 Quick Start

### 1️⃣ First Time Setup

```powershell
# Copy the template
Copy-Item config\.env.example config\.env

# Edit with your credentials
notepad config\.env
```

Fill in these required values:
- **Facebook**: `FB_APP_ID`, `FB_APP_SECRET`, `FB_PAGE_ACCESS_TOKEN`
- **WhatsApp**: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`
- **AI**: `GEMINI_API_KEY`

### 2️⃣ Verify Setup

```powershell
python -c "from config.settings import settings; print('✅ Config loaded!')"
```

---

## 💻 How to Use

### Basic Usage

```python
from config.settings import settings

# Access any configuration value
app_id = settings.FB_APP_ID
api_key = settings.GEMINI_API_KEY
port = settings.PORT
debug = settings.DEBUG
```

### Database Models

```python
from config.database_config import User, Message, Conversation, get_session

# Use in your code
with get_session() as session:
    users = session.query(User).all()
```

### Advanced (Config Sections)

```python
from config.config_manager import config_manager

# Get entire sections
facebook = config_manager.get_facebook_config()
whatsapp = config_manager.get_whatsapp_config()

# Get specific value with fallback
api_key = config_manager.get_config("ai", "gemini_api_key", default="fallback")
```

---

## 🎯 Configuration Sections

Your `.env` file is organized into these sections:

### 🔵 Facebook
- App credentials and page tokens
- Webhook verification tokens

### 💚 WhatsApp
- API access tokens
- Phone number configuration

### 🤖 AI (Gemini)
- API key and model selection

### ⚙️ Application
- Debug mode, environment, logging level
- Server host and port

### 🗄️ Database
- Connection strings (SQLite/PostgreSQL)

**See `.env.example` for all available variables.**

---

## 🎨 Architecture

```
┌──────────────────┐
│   Your Code      │
└────────┬─────────┘
         │ import settings
         ↓
┌──────────────────┐
│   settings.py    │  ← Type-safe properties
└────────┬─────────┘
         ↓
┌──────────────────┐
│ config_manager   │  ← Loads & validates
└────────┬─────────┘
         ↓
┌──────────────────┐
│   config/.env    │  ← Single source of truth
└──────────────────┘
```

**Type Safety:**
- `settings.FB_APP_ID` → returns `str`
- `settings.PORT` → returns `int`
- `settings.DEBUG` → returns `bool`

No manual type conversion needed!

---

## ✅ Validation

```python
from config.settings import settings

# Check if all required config exists
missing = settings.validate_required_settings()

if missing:
    print(f"❌ Missing: {missing}")
else:
    print("✅ All good!")
```

---

## 🧪 Testing

```bash
# Run all config tests
pytest tests/test_config.py -v

# Should see: 14/14 tests passing ✅
```

---

## 🔒 Security Rules

### ⚠️ NEVER commit:
- `config/.env` (has your secrets!)
- Any file with real API keys

### ✅ Safe to commit:
- `config/.env.example` (just a template)
- All `.py` files in config/
- This README

**The `.gitignore` already protects `.env` for you.**

---

## 🌍 Environments

### Development
```dotenv
DEBUG=True
ENVIRONMENT=development
```

### Production
```dotenv
DEBUG=False
ENVIRONMENT=production
```

---

## 🔧 Common Issues

### "Token not found"
**Fix:** Copy `.env.example` to `.env` and fill in your values

### Import Error
**Fix:** Use `from config.settings import settings` (not from `app.config` or `Server.config`)

### Config not loading
**Fix:** Make sure `config/.env` exists:
```powershell
Test-Path config\.env  # Should return True
```

---

## 📚 API Quick Reference

### `settings.py`
```python
from config.settings import settings

# Properties (type-safe)
settings.FB_APP_ID: str
settings.GEMINI_API_KEY: str
settings.PORT: int
settings.DEBUG: bool

# Methods
settings.validate_required_settings() -> List[str]
settings.update_webhook_urls(base_url: str) -> None
```

### `config_manager.py`
```python
from config.config_manager import config_manager

config_manager.load_configuration() -> bool
config_manager.validate_configuration() -> List[str]
config_manager.get_facebook_config() -> Dict
config_manager.get_whatsapp_config() -> Dict
config_manager.get_ai_config() -> Dict
```

### `database_config.py`
```python
from config.database_config import (
    User, Message, Conversation,  # Models
    MessageDirection, MessageStatus,  # Enums
    get_session, create_database,  # Utilities
    engine, SessionLocal, Base  # SQLAlchemy
)
```

---

## 📝 Best Practices

### ✅ DO:
```python
# Always use settings object
from config.settings import settings
api_key = settings.GEMINI_API_KEY
```

### ❌ DON'T:
```python
# Don't use os.getenv directly
import os
api_key = os.getenv("GEMINI_API_KEY")  # ❌

# Don't hardcode secrets
API_KEY = "sk-1234..."  # ❌ Very bad!
```

---

## 📊 Package Info

- **Version**: 2.0.0
- **Tests**: ✅ 14/14 passing
- **Type Safety**: ✅ Full typing support

---

## 🔗 Related Files

- **`.env.example`** - See all available configuration variables
- **`__init__.py`** - Package documentation and architecture details
- **`tests/test_config.py`** - Configuration test suite

---

**💡 Remember:** This is your **SINGLE SOURCE OF TRUTH** for configuration!
