# BWW Assistant - Server Module

## 📁 Server Architecture

Professional FastAPI server for BWW Assistant chatbot with Facebook Messenger, WhatsApp, and Lead Center integration.

## 🏗️ Structure

```Structure
Server/
├── README.md              # This file - comprehensive documentation
├── QUICKSTART.md          # 5-minute quick start guide
├── __init__.py            # Module initialization
├── run.py                 # Main server entry point (uvicorn)
├── main.py                # FastAPI application setup
├── config.py              # Settings class with properties
├── config_manager.py      # Configuration management
└── routes/                # Route re-exports (from app/routes/)
    └── __init__.py
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (edit config/.env)
# Add your Facebook credentials

# 3. Initialize database
python database/cli.py rebuild

# 4. Start server
python run.py
```

**Server runs at**: <http://localhost:8000>

- Dashboard: <http://localhost:8000/dashboard>
- API Docs: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

For detailed setup, see **[QUICKSTART.md](QUICKSTART.md)**

## 🔧 Configuration

Server configuration is managed through `config/.env`:

```env
# Facebook Settings (Required)
FB_APP_ID=your_app_id
FB_APP_SECRET=your_app_secret
FB_PAGE_ACCESS_TOKEN=your_page_token
FB_PAGE_ID=your_page_id
FB_VERIFY_TOKEN=BWW_MESSENGER_VERIFY_TOKEN_2025

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
ENVIRONMENT=development

# Database Settings
DATABASE_URL=sqlite:///database/bww_assistant.db

# AI Settings (Optional)
GEMINI_API_KEY=your_gemini_key

# WhatsApp Settings (Optional)
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
```

## 📡 API Endpoints

### Core Endpoints

- `GET /` - Dashboard home
- `GET /health` - Health check
- `GET /info` - Server information
- `GET /docs` - Swagger API documentation
- `GET /redoc` - ReDoc documentation

### Webhook Endpoints

- `GET/POST /webhook/messenger` - Facebook Messenger
- `GET/POST /webhook/whatsapp` - WhatsApp Business
- `GET/POST /webhook/leadgen` - Facebook Lead Center

### Dashboard Routes

- `GET /dashboard` - Main dashboard
- `GET /dashboard/users` - User management
- `GET /dashboard/messages` - Message history
- `GET /dashboard/leads` - Lead tracking
- `GET /dashboard/settings` - Settings page

### API Routes

- `GET /api/users` - List all users
- `GET /api/users/{psid}` - Get user profile
- `PUT /api/users/{psid}` - Update user
- `GET /api/messages` - List messages
- `POST /api/messages/send` - Send message
- `GET /api/conversations` - List conversations
- `GET /api/leads` - List leads
- `GET /api/stats` - Get statistics

## 🔒 Security

### Webhook Verification

All webhooks verify requests using Facebook's challenge/verify token system.

### Environment Security

- Store credentials in `config/.env` (not in code)
- Never commit `.env` to version control
- Use `.env.example` as template

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong verify tokens
- [ ] Use HTTPS for webhooks
- [ ] Regularly rotate access tokens

## 📊 Monitoring & Logging

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs Location

All logs in `logs/` directory:

- `app_*.log` - Application
- `error_*.log` - Errors
- `webhook_*.log` - Webhooks
- `messenger_*.log` - Messenger
- `database_*.log` - Database

## � Troubleshooting

### Port Already in Use

```powershell
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Import Errors

```bash
# Ensure in project root
cd /path/to/Migochat
python run.py
```

### Database Issues

```bash
# Rebuild database
python database/cli.py rebuild

# Check health
python database/cli.py health
```

### Facebook API Errors

- **401 Unauthorized** → Check `FB_PAGE_ACCESS_TOKEN`
- **403 Forbidden** → Verify `FB_VERIFY_TOKEN`
- **400 Bad Request** → Invalid PSID or payload

## � Related Documentation

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- **Database Module**: `../database/README.md` - Database documentation
- **Facebook API**: `../database/FACEBOOK_API_SUMMARY.md` - API alignment guide
- **API Documentation**: <http://localhost:8000/docs> (when server is running)

## � External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Facebook Messenger Platform](https://developers.facebook.com/docs/messenger-platform)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Facebook Lead Center](https://developers.facebook.com/docs/marketing-api/leads-access)

---

**Server Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Python**: 3.13.2+  
**Framework**: FastAPI 0.115.0+
