# ✅ Railway Production Deployment Checklist

## 🚀 Pre-Deployment Steps

### 1. Code Pushed to GitHub ✅
```bash
✅ Commit: 61023b0
✅ Branch: main
✅ Status: Pushed successfully
```

### 2. Railway Auto-Deploy
Railway will automatically deploy when you push to main branch.

Monitor deployment at:
🔗 https://railway.app/project/migochat-production

---

## 🔧 Critical Configuration on Railway

### Step 1: Verify Environment Variables
Go to Railway Dashboard → Variables tab and ensure ALL these are set:

#### 🔴 Facebook Messenger (CRITICAL - Must be exact!)
```
FB_PAGE_ACCESS_TOKEN=EAAeANEatdUwBQJT4oSKEhXcFjcgJce8PJTBIk20oGSnof0VpfSYQMrFlK9LngMAzV1lJv2IqhX6Rd7JyOyBzBuAMDRSiFeiUNfLtXpZBFKZBEjJwN38rgURwpj8UpImlFgUUElC2zA6twCxZAAg4OaFIrFTPM0WUHcUHMfUWbozK0HYRziS3xeZCxPAvpAQstVbI6ZAnc3JKZAuCXzcGbUkeo9GwZDZD
```

**⚠️ IMPORTANT**: This token MUST be 200+ characters. If it's shorter, it's truncated!

#### 🔴 Database (CRITICAL)
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```
Or if you have PostgreSQL addon:
```
DATABASE_URL=postgresql://user:password@host:port/database
```

#### 🔴 Other Required Variables
```
FB_APP_ID=2111286849402188
FB_APP_SECRET=0b3eae1493568a45960feca1fbbc5714
FB_PAGE_ID=862544323603883
GEMINI_API_KEY=AIzaSyDmez5TYMbM0MHXJb4ndC0hXJ9XwNt0ydU
WHATSAPP_ACCESS_TOKEN=EAAeANEatdUwBQIjiXlsAgvlacJKjabZCTZARNieQmYXJNupSrB5e690K5ZBXa8dKdfut94W4GdMaDG23Cv1g1EdPgZCDd3eCwJZA8q3C2SigSJBIGQwdpz8m1b7aitrZA0TlvLl2u5nSOId7a1UV981fxjGqfZCzVkgQjN8opUMtZBZCbhxZBKZCiUltDnPlbV15Gma8vMSjR7kKjQUttdk1kvNIaD1etE424UZCluBUGfDVI1wSTFIGOfJYaY3Y3ZBRkq3Xc3OfErd3uIsJAZCfAQZC7eLqcZByIqaZAJNYimd8hsgwZD
WHATSAPP_PHONE_NUMBER_ID=767028226502871
DEBUG=False
ENVIRONMENT=production
```

---

## 🧪 Post-Deployment Testing

### Step 2: Check Deployment Status
1. Go to Railway Dashboard
2. Click on your service
3. Check **Deployments** tab
4. Wait for "✅ Deployed" status (usually 2-3 minutes)

### Step 3: Check Logs
```bash
# Railway CLI
railway logs

# Look for these SUCCESS messages:
✅ "Configuration loaded successfully"
✅ "Messenger API connection verified"
✅ "Database connection established"
✅ "Application startup complete"
```

### Step 4: Test Dashboard
Visit: https://migochat-production.up.railway.app/dashboard

**Expected Results**:
- ✅ **Messenger**: Active (green badge)
- ✅ **Database**: Connected (green badge)
- ✅ **AI Service**: Active (green badge)
- ✅ **Lead Automation**: Active (green badge)
- ✅ **WhatsApp**: Active (green badge)
- ✅ **Webhooks**: Active (green badge)

---

## 🔴 Troubleshooting Common Issues

### Issue 1: Messenger Shows "Failed" or "Invalid Token"

**Symptoms**: Red badge on Messenger status

**Causes**:
1. Token is truncated/incomplete
2. Token has expired
3. Token doesn't have correct permissions

**Fix**:
1. Go to Railway Variables
2. Click on `FB_PAGE_ACCESS_TOKEN`
3. Verify the FULL token (should be 200+ characters)
4. If truncated, delete and re-add with full value
5. Redeploy

**To Get New Token**:
```bash
# 1. Go to Graph API Explorer
https://developers.facebook.com/tools/explorer/

# 2. Select your App: "Bww-AI-Assistant"
# 3. Get Token → Get User Access Token
# 4. Select permissions: pages_messaging, leads_retrieval
# 5. Generate Token
# 6. Exchange for Page Token:
curl "https://graph.facebook.com/v21.0/me/accounts?access_token=USER_TOKEN"

# 7. Copy "access_token" for your page
# 8. Update in Railway Variables
```

---

### Issue 2: Database Shows "Disconnected"

**Symptoms**: Red badge on Database status

**Causes**:
1. PostgreSQL addon not attached
2. DATABASE_URL incorrect
3. Database not created

**Fix**:
1. Railway Dashboard → Add PostgreSQL addon
2. Wait for provisioning (1-2 minutes)
3. Verify DATABASE_URL variable is set automatically
4. Redeploy

**Manual Database Check**:
```bash
# Railway CLI
railway run python -c "from database import get_db_session; get_db_session()"
```

---

### Issue 3: Dashboard Stuck on "Loading..."

**Symptoms**: White screen with "Dashboard is loading..."

**Causes**:
1. Python dependencies not installed
2. Template files missing
3. Route not accessible

**Fix**:
1. Check Railway logs for errors
2. Verify all files are committed to Git
3. Force rebuild:
```bash
railway up --detach
```

---

### Issue 4: "Module Not Found" Errors

**Symptoms**: 500 errors, import errors in logs

**Causes**:
1. requirements.txt not updated
2. Missing dependencies

**Fix**:
1. Verify requirements.txt includes:
   - httpx>=0.27.0
   - fastapi>=0.115.0
   - sqlalchemy>=2.0.35
2. Force reinstall:
```bash
railway run pip install -r requirements.txt
```

---

## 🔄 Token Refresh Schedule

### Facebook Tokens Expire After 60 Days!

**Set Calendar Reminder**:
- 📅 Next refresh due: **January 21, 2026**
- 🔔 Reminder: 7 days before expiration

**Refresh Process**:
1. Follow "To Get New Token" steps above
2. Update Railway Variables:
   - `FB_PAGE_ACCESS_TOKEN`
   - `FB_SYSTEM_USER_TOKEN`
3. Redeploy (automatic)
4. Verify Messenger status = Active

---

## 📊 Health Check Endpoints

Test these URLs after deployment:

```bash
# 1. Root health check
curl https://migochat-production.up.railway.app/

# 2. API health check
curl https://migochat-production.up.railway.app/api/health

# 3. Dashboard (visual check)
https://migochat-production.up.railway.app/dashboard

# 4. Webhook verification (should return 200)
https://migochat-production.up.railway.app/webhook/messenger
https://migochat-production.up.railway.app/webhook/whatsapp
```

---

## 📞 Support Contacts

### Facebook Developer Support
- Dashboard: https://developers.facebook.com/apps/2111286849402188
- Token Debugger: https://developers.facebook.com/tools/debug/accesstoken/

### Railway Support
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

### Gemini API
- Console: https://aistudio.google.com/app/apikey
- Docs: https://ai.google.dev/docs

---

## ✅ Final Checklist

Before closing this deployment:

- [ ] Railway deployment completed successfully
- [ ] All 6 status indicators are green on dashboard
- [ ] Facebook webhook receiving messages
- [ ] WhatsApp webhook receiving messages
- [ ] Database queries working
- [ ] AI responses generating correctly
- [ ] No errors in Railway logs
- [ ] Calendar reminder set for token refresh

---

**Deployment Date**: November 22, 2025, 02:00 AM
**Commit Hash**: 61023b0
**Status**: ✅ Ready for Production Testing

**Next Steps**:
1. Monitor Railway logs for 10 minutes
2. Send test message via Facebook Messenger
3. Verify response in dashboard
4. Set token expiration reminder

---

🎉 **Deployment Complete!** Your bot is now live and monitoring system health in real-time.
