# Configuration Directory

## 📋 Overview

This directory contains **all** centralized configuration for the BWW AI Assistant application. All settings, database configs, logging, and environment variables are managed here.

## 🗂️ Structure

```
config/
├── __init__.py              # Package initialization, exports settings
├── settings.py              # Main settings API (property-based access)
├── config_manager.py        # Configuration manager (loads from .env)
├── database_config.py       # Database configuration (imports from database/)
├── logging_config.py        # Centralized logging configuration
└── .env                     # Environment variables (git-ignored)
```

## 🔧 Usage

### Import Settings

```python
# Recommended - Direct import
from config.settings import settings

# Use settings
print(settings.FB_APP_ID)
print(settings.GEMINI_API_KEY)
print(settings.DATABASE_URL)
```

### Import Database Config

```python
# Import models
from config.database_config import User, Message, Conversation

# Import utilities
from config.database_config import get_session, check_database_health
```

### Import Config Manager

```python
# Advanced usage
from config.config_manager import config_manager

# Get entire section
fb_config = config_manager.get_facebook_config()

# Get specific value
api_key = config_manager.get_config("ai", "gemini_api_key")
```

## ⚙️ Configuration Sections

### 1. Facebook Configuration
- `FB_APP_ID` - Facebook App ID
- `FB_APP_SECRET` - Facebook App Secret
- `FB_PAGE_ACCESS_TOKEN` - Page Access Token
- `FB_PAGE_ID` - Facebook Page ID
- `FB_SYSTEM_USER_TOKEN` - System User Token
- `FB_VERIFY_TOKEN` - Messenger Webhook Verify Token
- `FB_LEADCENTER_VERIFY_TOKEN` - Lead Center Verify Token

### 2. WhatsApp Configuration
- `WHATSAPP_ACCESS_TOKEN` - WhatsApp Business API Token
- `WHATSAPP_PHONE_NUMBER_ID` - WhatsApp Phone Number ID
- `WHATSAPP_VERIFY_TOKEN` - WhatsApp Webhook Verify Token

### 3. Webhook Configuration
- `MESSENGER_WEBHOOK_URL` - Messenger webhook URL
- `WHATSAPP_WEBHOOK_URL` - WhatsApp webhook URL
- `LEADCENTER_WEBHOOK_URL` - Lead Center webhook URL

### 4. Database Configuration
- `DATABASE_URL` - SQLite database URL

### 5. Application Configuration
- `DEBUG` - Debug mode (True/False)
- `ENVIRONMENT` - Environment (development/production)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/ERROR)
- `TIMEZONE` - Application timezone
- `HOST` - Server host
- `PORT` - Server port

### 6. AI Configuration
- `GEMINI_API_KEY` - Google Gemini API Key
- `GEMINI_MODEL` - Gemini model name (default: gemini-2.5-flash)

### 7. BWW Store Configuration
- `BWW_STORE_SECRET_KEY` - BWW Store API Secret
- `BWW_STORE_BASE_URL` - BWW Store API Base URL

### 8. API Configuration
- `MESSENGER_API_URL` - Facebook Graph API URL
- `WEBHOOK_URL` - Webhook endpoint path

## 📝 Environment Variables

Create a `config/.env` file with:

```env
# Facebook
FB_APP_ID=your_app_id
FB_APP_SECRET=your_app_secret
FB_PAGE_ACCESS_TOKEN=your_page_token
FB_PAGE_ID=your_page_id
FB_SYSTEM_USER_TOKEN=your_system_token
FB_VERIFY_TOKEN=BWW_MESSENGER_VERIFY_TOKEN_2025
FB_LEADCENTER_VERIFY_TOKEN=BWW_LEADCENTER_VERIFY_TOKEN_2025

# WhatsApp
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=BWW_WHATSAPP_VERIFY_TOKEN_2025

# AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

# BWW Store
BWW_STORE_SECRET_KEY=BwwSecretKey2025
BWW_STORE_BASE_URL=https://api-v1.bww-store.com/api/v1

# Application
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=INFO
TIMEZONE=Africa/Cairo
HOST=0.0.0.0
PORT=8000
```

## 🔄 Migration from Old Structure

### Before (Duplicated Configuration)
```
Server/
  ├── config.py              ❌ Moved to config/settings.py
  └── config_manager.py      ❌ Moved to config/config_manager.py

config/
  └── database_config.py     ❌ Had duplicate models (now imports from database/)
```

### After (Centralized Configuration)
```
config/
  ├── settings.py            ✅ Main settings API
  ├── config_manager.py      ✅ Configuration loader
  ├── database_config.py     ✅ Clean wrapper (imports from database/)
  └── logging_config.py      ✅ Logging setup
```

### Import Changes
```python
# Old imports (removed)
from Server.config import settings          ❌
from Server.config_manager import config    ❌

# New imports (use these)
from config.settings import settings        ✅
from config.config_manager import config    ✅
```

## ✅ Benefits

1. **Single Source of Truth** - All config in one place
2. **No Duplication** - Removed duplicate database models
3. **Clear Separation** - Config vs. Server logic
4. **Easy to Find** - Developers know where to look
5. **Type Safety** - Property-based access with type hints
6. **Validation** - Built-in config validation
7. **Maintainability** - Easier to update and test

## 🧪 Testing

All configuration tests pass:
```bash
pytest tests/test_config.py -v
# ✅ 14/14 tests passing
```

## 🚀 Production Ready

- ✅ All duplicates removed
- ✅ Clean imports updated
- ✅ All tests passing
- ✅ Type-safe configuration
- ✅ Environment-based settings
- ✅ Proper validation
- ✅ Documentation complete

---

**Last Updated**: 2025-01-14
**Status**: Production Ready ✅
