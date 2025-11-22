# 🚂 Railway Environment Variables Setup

## 🎯 Critical Variables for Production

### ✅ Required Variables

Copy these to Railway dashboard → Your Project → Variables:

```bash
# Facebook Messenger (CRITICAL)
FB_APP_ID=2111286849402188
FB_APP_SECRET=0b3eae1493568a45960feca1fbbc5714
FB_PAGE_ID=862544323603883
FB_PAGE_ACCESS_TOKEN=EAAeANEatdUwBQJT4oSKEhXcFjcgJce8PJTBIk20oGSnof0VpfSYQMrFlK9LngMAzV1lJv2IqhX6Rd7JyOyBzBuAMDRSiFeiUNfLtXpZBFKZBEjJwN38rgURwpj8UpImlFgUUElC2zA6twCxZAAg4OaFIrFTPM0WUHcUHMfUWbozK0HYRziS3xeZCxPAvpAQstVbI6ZAnc3JKZAuCXzcGbUkeo9GwZDZD
FB_SYSTEM_USER_TOKEN=EAAeANEatdUwBP1HW2wjJ5xMn45wQTNKMk5xPP4t1b4ZA1ZCax4eZBP4Hp3Aj5aZC9zZBli5orGfIwohJxZBAZBxMwjpsJqu4ZCeB20apTuzQIENfxjEDgVlh1PWIH8fD4RlqtfBrncepZAest9MwGIKeo0hlZAZCDInYbwrgOlFhWDPCzCvidY3q4mGn5yUgmGGV37q2PZBi9ohR3Tqhm6fhejcQyAgvfYvHiDv5OESTOTqzz
FB_VERIFY_TOKEN=BWW_MESSENGER_VERIFY_TOKEN_2025
FB_LEADCENTER_VERIFY_TOKEN=BWW_MESSENGER_VERIFY_TOKEN_2025

# WhatsApp Business API (CRITICAL)
WHATSAPP_ACCESS_TOKEN=EAAeANEatdUwBQIjiXlsAgvlacJKjabZCTZARNieQmYXJNupSrB5e690K5ZBXa8dKdfut94W4GdMaDG23Cv1g1EdPgZCDd3eCwJZA8q3C2SigSJBIGQwdpz8m1b7aitrZA0TlvLl2u5nSOId7a1UV981fxjGqfZCzVkgQjN8opUMtZBZCbhxZBKZCiUltDnPlbV15Gma8vMSjR7kKjQUttdk1kvNIaD1etE424UZCluBUGfDVI1wSTFIGOfJYaY3Y3ZBRkq3Xc3OfErd3uIsJAZCfAQZC7eLqcZByIqaZAJNYimd8hsgwZD
WHATSAPP_PHONE_NUMBER_ID=767028226502871
WHATSAPP_VERIFY_TOKEN=BWW_WHATSAPP_VERIFY_TOKEN_2025

# Webhook URLs (Railway Production)
MESSENGER_WEBHOOK_URL=https://migochat-production.up.railway.app/webhook/messenger
LEADCENTER_WEBHOOK_URL=https://migochat-production.up.railway.app/webhook/messenger
WHATSAPP_WEBHOOK_URL=https://migochat-production.up.railway.app/webhook/whatsapp

# Database (Railway will auto-configure PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# AI Services (CRITICAL)
GEMINI_API_KEY=AIzaSyDmez5TYMbM0MHXJb4ndC0hXJ9XwNt0ydU
GEMINI_MODEL=gemini-2.5-flash

# Application Settings (Production)
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
TIMEZONE=Africa/Cairo
HOST=0.0.0.0
PORT=8000

# BWW Store Integration
BWW_STORE_SECRET_KEY=BwwSecretKey2025
BWW_STORE_BASE_URL=https://api-v1.bww-store.com/api/v1
```

## 🔧 How to Add Variables to Railway

### Method 1: Railway Dashboard (Recommended)
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Select your project: **migochat-production**
3. Click on **Variables** tab
4. Click **+ New Variable**
5. Copy-paste each variable from above
6. Click **Deploy** to apply changes

### Method 2: Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Add variables
railway variables set FB_PAGE_ACCESS_TOKEN="your_token_here"
railway variables set GEMINI_API_KEY="your_key_here"
# ... etc
```

## ⚠️ Critical Checks

### 1. Token Validation
Make sure your tokens are:
- ✅ **Not expired** (Facebook tokens expire after 60 days)
- ✅ **Have correct permissions** (pages_messaging, leads_retrieval, whatsapp_business_messaging)
- ✅ **Not truncated** (full token length should be 200+ characters)

### 2. Webhook Configuration
On Facebook Developer Console:
1. Go to **App Dashboard** → **Webhooks**
2. Set Callback URL: `https://migochat-production.up.railway.app/webhook/messenger`
3. Verify Token: `BWW_MESSENGER_VERIFY_TOKEN_2025`
4. Subscribe to fields: `messages`, `messaging_postbacks`, `leadgen`

On WhatsApp Manager:
1. Go to **Configuration**
2. Set Webhook URL: `https://migochat-production.up.railway.app/webhook/whatsapp`
3. Verify Token: `BWW_WHATSAPP_VERIFY_TOKEN_2025`

### 3. Database Setup
If using Railway PostgreSQL:
```bash
# Railway will auto-provision PostgreSQL
# DATABASE_URL will be: postgresql://user:pass@host:port/dbname

# Run migrations after deployment
railway run python -m alembic upgrade head
```

## 🐛 Troubleshooting

### Messenger Failed
- **Check**: FB_PAGE_ACCESS_TOKEN is valid and not expired
- **Verify**: Token has `pages_messaging` permission
- **Test**: Visit https://developers.facebook.com/tools/debug/accesstoken/

### Database Disconnected
- **Check**: DATABASE_URL is correctly set
- **Verify**: PostgreSQL service is running
- **Test**: Railway logs should show database connection

### AI Service Error
- **Check**: GEMINI_API_KEY is valid
- **Verify**: API key has quota available
- **Test**: Visit https://aistudio.google.com/app/apikey

## 📊 Monitoring

Check Railway logs:
```bash
railway logs
```

Check dashboard status:
https://migochat-production.up.railway.app/dashboard

## 🔄 Token Refresh

Facebook Page Access Tokens expire after 60 days. To refresh:

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your App
3. Get Token → Get User Access Token
4. Select permissions: `pages_messaging`, `leads_retrieval`, `pages_read_engagement`
5. Generate Access Token
6. Exchange for Page Token:
```bash
curl -X GET "https://graph.facebook.com/v24.0/me/accounts?access_token=USER_ACCESS_TOKEN"
```
7. Update FB_PAGE_ACCESS_TOKEN in Railway

---

**Last Updated**: November 22, 2025
**Railway Project**: migochat-production
**Production URL**: https://migochat-production.up.railway.app
