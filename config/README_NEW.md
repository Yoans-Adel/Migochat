# 🎯 Migochat Configuration - Unified & Fixed

## 📍 Configuration Location

**ALL configuration is now centralized here:** `config/`

```
config/
├── .env                     ← YOUR SETTINGS (gitignored)
├── .env.example             ← Template to copy
├── settings.py              ← Access layer (use this in code)
├── config_manager.py        ← Loads from .env
├── database_config.py       ← Database setup
├── logging_config.py        ← Logging setup
├── CONFIGURATION_GUIDE.md   ← Complete documentation
└── README_NEW.md           ← This file
```

## ✅ What Was Fixed

### Problems Solved:
1. ❌ **`.env` in root** → ✅ **Moved to `config/.env`**
2. ❌ **Duplicate tokens** → ✅ **Unified single values**
3. ❌ **"Token not found" errors** → ✅ **ConfigManager loads correctly**
4. ❌ **Multiple config files** → ✅ **Single source of truth**
5. ❌ **Inconsistent imports** → ✅ **All use `config.settings`**

### Key Changes:
- Moved `.env` from root → `config/.env`
- Eliminated duplicate `FB_VERIFY_TOKEN` vs `FB_LEADCENTER_VERIFY_TOKEN` (now unified)
- ConfigManager loads from `config/.env` automatically
- All code updated to use `from config.settings import settings`
- Created `.env.example` as template
- Updated `.gitignore` to protect `config/.env`

## 🚀 Quick Setup

### First Time Setup

```powershell
# 1. Copy template
Copy-Item config\.env.example config\.env

# 2. Edit with your values
notepad config\.env

# 3. Fill in required values:
#    - FB_APP_ID, FB_APP_SECRET, FB_PAGE_ACCESS_TOKEN
#    - WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID
#    - GEMINI_API_KEY
```

### Verify Configuration

```powershell
# Test configuration loads
python -c "from config.settings import settings; print(f'✅ Config OK: {settings.FB_APP_ID}')"
```

## 📖 How to Use

### In Your Code

```python
from config.settings import settings

# Facebook
app_id = settings.FB_APP_ID
page_token = settings.FB_PAGE_ACCESS_TOKEN
verify_token = settings.FB_VERIFY_TOKEN

# WhatsApp
wa_token = settings.WHATSAPP_ACCESS_TOKEN
wa_phone = settings.WHATSAPP_PHONE_NUMBER_ID

# AI
gemini_key = settings.GEMINI_API_KEY
model = settings.GEMINI_MODEL

# App
debug = settings.DEBUG
port = settings.PORT
```

### Available Settings

#### 🔵 Facebook Messenger
| Setting | Description |
|---------|-------------|
| `FB_APP_ID` | Facebook App ID |
| `FB_APP_SECRET` | Facebook App Secret |
| `FB_PAGE_ID` | Facebook Page ID |
| `FB_PAGE_ACCESS_TOKEN` | Page Access Token (for sending) |
| `FB_SYSTEM_USER_TOKEN` | System User Token (Lead Center) |
| `FB_VERIFY_TOKEN` | Webhook verification (unified) |
| `FB_LEADCENTER_VERIFY_TOKEN` | Same as FB_VERIFY_TOKEN |

#### 💚 WhatsApp
| Setting | Description |
|---------|-------------|
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp API token |
| `WHATSAPP_PHONE_NUMBER_ID` | Phone number ID |
| `WHATSAPP_VERIFY_TOKEN` | Webhook verification |

#### 🤖 AI Services
| Setting | Description |
|---------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `GEMINI_MODEL` | Model name (default: gemini-2.5-flash) |

#### 🌐 Webhooks
| Setting | Description |
|---------|-------------|
| `MESSENGER_WEBHOOK_URL` | Messenger webhook URL |
| `WHATSAPP_WEBHOOK_URL` | WhatsApp webhook URL |
| `LEADCENTER_WEBHOOK_URL` | Lead Ads webhook (same as Messenger) |

#### 🗄️ Database
| Setting | Description |
|---------|-------------|
| `DATABASE_URL` | Database connection string |

#### ⚙️ Application
| Setting | Description |
|---------|-------------|
| `DEBUG` | Debug mode (True/False) |
| `ENVIRONMENT` | Environment (development/production) |
| `LOG_LEVEL` | Logging level (INFO/DEBUG/WARNING) |
| `TIMEZONE` | Timezone (Africa/Cairo) |
| `HOST` | Server host (0.0.0.0) |
| `PORT` | Server port (8000) |

## 🔧 Common Issues

### "Token not found" or "Configuration missing"

**Cause:** `config/.env` doesn't exist or empty

**Solution:**
```powershell
# Copy template
Copy-Item config\.env.example config\.env

# Edit with your values
notepad config\.env
```

### "Module not found: config.settings"

**Cause:** Wrong import path

**Fix:**
```python
# ❌ Wrong
from app.config import settings
from Server.config import settings

# ✅ Correct
from config.settings import settings
```

### Environment variables not loading

**Cause:** ConfigManager looks for `config/.env` (correct location)

**Verify:**
```powershell
# Check file exists
Test-Path config\.env

# If False, copy template
Copy-Item config\.env.example config\.env
```

## 🔐 Security

### ⚠️ NEVER Commit These:
- `config/.env` (contains secrets)
- Any file with actual tokens/keys

### ✅ Safe to Commit:
- `config/.env.example` (template only)
- All `.py` files in `config/`
- `CONFIGURATION_GUIDE.md`

## 📝 Best Practices

### ✅ DO:
- Use `config.settings` to access configuration
- Keep `config/.env` with actual values (gitignored)
- Update `.env.example` when adding new variables
- Validate settings on startup

### ❌ DON'T:
- Hardcode tokens in code
- Use `os.getenv()` directly
- Create multiple `.env` files
- Commit `config/.env` to git

## 🧪 Testing Configuration

```python
from config.settings import settings

# Validate all required settings
missing = settings.validate_required_settings()

if missing:
    print(f"❌ Missing: {missing}")
else:
    print("✅ All configuration valid!")
```

## 🚢 Deployment

### Local (ngrok)
```dotenv
MESSENGER_WEBHOOK_URL=https://your-domain.ngrok-free.dev/webhook/messenger
```

### Production (Railway)
```dotenv
MESSENGER_WEBHOOK_URL=https://your-app.railway.app/webhook/messenger
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 📚 Documentation

For complete details, see: [`CONFIGURATION_GUIDE.md`](./CONFIGURATION_GUIDE.md)

---

**Remember:** `config/.env` is the **ONLY** place for configuration! 🎯
