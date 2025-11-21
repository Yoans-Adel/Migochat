# Configuration Management Guide

## 📍 Configuration Location

**ALL configuration is centralized in:** `config/.env`

```
config/
├── .env              ← YOUR ACTUAL CONFIGURATION (gitignored)
├── .env.example      ← Template with instructions
├── settings.py       ← Settings access layer
└── config_manager.py ← Configuration loader
```

## 🎯 Single Source of Truth

The `config/.env` file is the **ONLY** place where you set:
- API keys and tokens
- Database URLs
- Webhook URLs
- Application settings

**All services read from this file via `config.settings`**

## 🚀 Quick Setup

### First Time Setup

1. **Copy the template:**
```powershell
Copy-Item config/.env.example config/.env
```

2. **Edit `config/.env`** with your actual values:
```powershell
notepad config/.env
```

3. **Required values:**
   - Facebook: `FB_APP_ID`, `FB_APP_SECRET`, `FB_PAGE_ACCESS_TOKEN`, `FB_VERIFY_TOKEN`
   - WhatsApp: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`
   - Gemini AI: `GEMINI_API_KEY`

## 📖 How to Use Configuration

### In Your Code

```python
from config.settings import settings

# Facebook configuration
app_id = settings.FB_APP_ID
page_token = settings.FB_PAGE_ACCESS_TOKEN

# WhatsApp configuration
wa_token = settings.WHATSAPP_ACCESS_TOKEN

# AI configuration
gemini_key = settings.GEMINI_API_KEY

# Application settings
debug_mode = settings.DEBUG
port = settings.PORT
```

### Available Settings

#### Facebook Messenger
- `settings.FB_APP_ID` - Facebook App ID
- `settings.FB_APP_SECRET` - Facebook App Secret
- `settings.FB_PAGE_ID` - Facebook Page ID
- `settings.FB_PAGE_ACCESS_TOKEN` - Page Access Token
- `settings.FB_SYSTEM_USER_TOKEN` - System User Token (Lead Center)
- `settings.FB_VERIFY_TOKEN` - Webhook verification token
- `settings.FB_LEADCENTER_VERIFY_TOKEN` - Lead Ads verification (same as FB_VERIFY_TOKEN)

#### WhatsApp
- `settings.WHATSAPP_ACCESS_TOKEN` - WhatsApp API token
- `settings.WHATSAPP_PHONE_NUMBER_ID` - Phone number ID
- `settings.WHATSAPP_VERIFY_TOKEN` - Webhook verification token

#### Webhooks
- `settings.MESSENGER_WEBHOOK_URL` - Messenger webhook URL
- `settings.WHATSAPP_WEBHOOK_URL` - WhatsApp webhook URL
- `settings.LEADCENTER_WEBHOOK_URL` - Lead Ads webhook URL

#### Database
- `settings.DATABASE_URL` - Database connection string

#### AI Services
- `settings.GEMINI_API_KEY` - Google Gemini API key
- `settings.GEMINI_MODEL` - Model name (default: gemini-2.5-flash)

#### Application
- `settings.DEBUG` - Debug mode (True/False)
- `settings.ENVIRONMENT` - Environment name (development/production)
- `settings.LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING)
- `settings.TIMEZONE` - Timezone (Africa/Cairo)
- `settings.HOST` - Server host (0.0.0.0)
- `settings.PORT` - Server port (8000)

## 🔧 Common Issues & Solutions

### Issue: "Token not found" or "Missing configuration"

**Cause:** Configuration not loaded or `.env` file missing

**Solution:**
```powershell
# 1. Check if config/.env exists
Test-Path config/.env

# 2. If not, copy template
Copy-Item config/.env.example config/.env

# 3. Edit with your values
notepad config/.env
```

### Issue: Duplicate tokens in different files

**Solution:** We eliminated this! Now there's ONLY ONE `.env` file in `config/`

### Issue: Environment variables not loaded

**Cause:** Application not reading from correct location

**Solution:** Config manager loads from `config/.env` automatically. No action needed.

## 📝 Configuration Best Practices

### ✅ DO:
- Keep `config/.env` with actual values (gitignored)
- Use `config/.env.example` as template for team members
- Update `.env.example` when adding new config variables
- Use `settings` object to access configuration
- Validate required settings on startup

### ❌ DON'T:
- Commit `config/.env` to git (contains secrets)
- Hardcode tokens/keys in code
- Use `os.getenv()` directly (use `settings` instead)
- Create multiple `.env` files in different locations
- Store different values in code vs `.env`

## 🔐 Security Notes

### Sensitive Values (NEVER commit):
- `FB_PAGE_ACCESS_TOKEN`
- `FB_SYSTEM_USER_TOKEN`
- `WHATSAPP_ACCESS_TOKEN`
- `GEMINI_API_KEY`
- `NGROK_AUTH_TOKEN`
- `FB_APP_SECRET`

### Safe to Share (in .env.example):
- `FB_APP_ID` (public)
- `FB_PAGE_ID` (public)
- `WHATSAPP_PHONE_NUMBER_ID` (phone number)
- Configuration structure and defaults

## 🚢 Deployment Configuration

### Local Development (ngrok)
```dotenv
MESSENGER_WEBHOOK_URL=https://your-domain.ngrok-free.dev/webhook/messenger
WHATSAPP_WEBHOOK_URL=https://your-domain.ngrok-free.dev/webhook/whatsapp
```

### Production (Railway)
```dotenv
MESSENGER_WEBHOOK_URL=https://your-app.railway.app/webhook/messenger
WHATSAPP_WEBHOOK_URL=https://your-app.railway.app/webhook/whatsapp
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 🧪 Testing Configuration

### Validate Configuration
```python
from config.settings import settings

# Check if all required settings are present
missing = settings.validate_required_settings()

if missing:
    print(f"Missing configuration: {missing}")
else:
    print("✅ All configuration valid!")
```

### Test in Python REPL
```python
# Test loading
from config.settings import settings

# Check values
print(f"FB App ID: {settings.FB_APP_ID}")
print(f"Debug Mode: {settings.DEBUG}")
print(f"Port: {settings.PORT}")
```

## 📚 Migration from Old Structure

If you have old config files in different locations:

### Old Structure (DEPRECATED):
```
.env                    ← Delete or move
app/config.py          ← Doesn't exist anymore
Server/config.py       ← Doesn't exist anymore
```

### New Structure (CURRENT):
```
config/
├── .env               ← Single source of truth
├── .env.example       ← Template
├── settings.py        ← Access layer
└── config_manager.py  ← Loader
```

### Migration Steps:
1. ✅ Move `.env` to `config/.env` (done automatically)
2. ✅ Update all imports to use `config.settings` (done)
3. ✅ Remove old config files (if any)
4. ✅ Update `.gitignore` (done)

## 🔄 Updating Configuration at Runtime

Configuration can be updated via Settings API:

```python
# Via API endpoint (dashboard)
POST /api/settings
{
  "ai": {
    "gemini_api_key": "new_key",
    "gemini_model": "gemini-2.5-pro"
  }
}
```

This updates both runtime and environment variables.

## 📞 Support

If you encounter configuration issues:
1. Check `config/.env` exists and has values
2. Verify `.env.example` for correct format
3. Check logs for configuration errors
4. Validate required settings using `settings.validate_required_settings()`

---

**Remember:** `config/.env` is the single source of truth for ALL configuration! 🎯
