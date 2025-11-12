# BWW Assistant Server - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Configure Environment

Create or edit `config/.env`:

```env
# Facebook Configuration (Required)
FB_APP_ID=your_app_id
FB_APP_SECRET=your_app_secret
FB_PAGE_ACCESS_TOKEN=your_page_access_token
FB_PAGE_ID=your_page_id
FB_VERIFY_TOKEN=BWW_MESSENGER_VERIFY_TOKEN_2025

# Database (Optional - uses SQLite by default)
DATABASE_URL=sqlite:///database/bww_ai_assistant.db

# Server Configuration (Optional)
HOST=0.0.0.0
PORT=8000
DEBUG=True
ENVIRONMENT=development

# AI Configuration (Optional)
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Initialize Database

```bash
# Create database tables
python database/cli.py rebuild
```

### 4. Start Server

```bash
# From project root (recommended)
python run.py
```

Your server is now running at:

- **Dashboard**: <http://localhost:8000/dashboard>
- **API Docs**: <http://localhost:8000/docs>
- **Health Check**: <http://localhost:8000/health>

## 📖 Next Steps

### Configure Facebook Webhook

1. Go to Facebook Developer Console
2. Navigate to Messenger Settings
3. Set Webhook URL: `https://your-domain.com/webhook/messenger`
4. Set Verify Token: `BWW_MESSENGER_VERIFY_TOKEN_2025`
5. Subscribe to events: `messages`, `messaging_postbacks`, `message_reads`, `message_deliveries`

### Test the Server

```bash
# Check health
curl http://localhost:8000/health

# Get stats
curl http://localhost:8000/api/stats

# Get users
curl http://localhost:8000/api/users
```

### Access Dashboard

Open browser: <http://localhost:8000/dashboard>

Features:

- View all users and conversations
- Monitor message activity
- Track lead stages
- View Facebook Lead Center integration
- Analyze message sources (posts, ads, comments)

## 🔧 Advanced Configuration

### Production Deployment

```env
# Production settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING

# Use PostgreSQL (recommended for production)
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Enable WhatsApp

```env
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_VERIFY_TOKEN=BWW_WHATSAPP_VERIFY_TOKEN_2025
```

### Enable Lead Center

```env
FB_LEADCENTER_VERIFY_TOKEN=BWW_LEADCENTER_VERIFY_TOKEN_2025
```

## 🐛 Troubleshooting

### Port Already in Use

```powershell
# Windows PowerShell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Not Found

```bash
# Rebuild database
python database/cli.py rebuild
```

### Import Errors

```bash
# Make sure you're in project root
cd f:\working - yoans\Migochat

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Facebook API Errors

- **401 Unauthorized**: Check `FB_PAGE_ACCESS_TOKEN`
- **400 Bad Request**: Verify Facebook User ID (PSID)
- **403 Forbidden**: Check `FB_VERIFY_TOKEN`

## 📚 Documentation

- **Server README**: `Server/README.md`
- **Database Module**: `database/README.md`
- **Facebook API Alignment**: `database/FACEBOOK_API_SUMMARY.md`
- **API Documentation**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## 💡 Development Tips

### Auto-Reload

Server automatically reloads when DEBUG=True:

```env
DEBUG=True
```

### View Logs

```bash
# View application logs
tail -f logs/app_*.log

# View error logs
tail -f logs/error_*.log

# View webhook logs
tail -f logs/webhook_*.log
```

### Database Management

```bash
# Health check
python database/cli.py health

# Backup database
python database/cli.py backup

# Rebuild database (careful - deletes data!)
python database/cli.py rebuild
```

## 🎯 Key Features

✅ **Facebook Messenger Integration**

- Webhook endpoints for all event types
- Message sending and receiving
- User profile management
- PSID-based user identification

✅ **Facebook Lead Center**

- Lead creation and syncing
- Lead stage tracking
- Lead activity monitoring
- Automated lead management

✅ **Message Source Tracking**

- Track messages from posts
- Track messages from ads
- Track messages from comments
- Conversion analytics

✅ **WhatsApp Business API**

- Send text messages
- Send template messages
- Send interactive messages
- Send list messages

✅ **AI Integration**

- Google Gemini AI
- Contextual responses
- User profile awareness
- Conversation history

✅ **Dashboard & Analytics**

- User management
- Message tracking
- Lead analytics
- Source analytics

## 🔗 Useful Links

- **FastAPI Documentation**: <https://fastapi.tiangolo.com/>
- **Facebook Messenger Platform**: <https://developers.facebook.com/docs/messenger-platform>
- **Facebook Lead Center**: <https://developers.facebook.com/docs/marketing-api/leads-access>
- **WhatsApp Business API**: <https://developers.facebook.com/docs/whatsapp>

---

**Need Help?** Check the full documentation in `Server/README.md`
