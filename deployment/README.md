# 🚀 Railway Deployment Guide# Railway Deployment# Deployment Folder



Complete guide for deploying BWW AI Assistant to Railway.app with HTTPS.Simple deployment to Railway for permanent HTTPS URL.Simple deployment configs for Railway/Render.



---## Quick Deploy## Quick Deploy



## 📋 Prerequisites```bashPush to GitHub, then connect Railway or Render.



- ✅ GitHub account# 1. Validate

- ✅ Railway account (https://railway.app)

- ✅ All environment variables from `.env` filepython deployment/check.pyThat's it!

- ✅ Project passing deployment check



---# 2. Push to GitHub

git push

## 🔍 Step 1: Pre-Deployment Validation

# 3. Deploy on Railway

Run the deployment check script to ensure everything is ready:# - Go to railway.app

# - Connect GitHub

```bash# - Add environment variables

python deployment/check.py# - Deploy!

``````



**Expected Output:**## Files

```

✅ DEPLOYMENT READY!- `Procfile` - Process command

```- `runtime.txt` - Python 3.13.2

- `railway.json` - Railway config

If you see any errors, fix them before proceeding.- `check.py` - Validation script



---## Environment Variables



## 📦 Step 2: Push to GitHubCopy these from your `.env` to Railway:



```bash- FB_APP_ID

# Ensure all changes are committed- FB_APP_SECRET

git add .- FB_PAGE_ACCESS_TOKEN

git commit -m "Production ready for Railway deployment 🚀"- FB_VERIFY_TOKEN

git push origin main- WHATSAPP_ACCESS_TOKEN

```- WHATSAPP_PHONE_NUMBER_ID

- WHATSAPP_VERIFY_TOKEN

---- GEMINI_API_KEY

- DEBUG

## 🚂 Step 3: Deploy on Railway- TIMEZONE



### 3.1 Create New Project## After Deployment



1. Go to [railway.app](https://railway.app)Configure Meta webhooks with your Railway URL:

2. Click **"New Project"**

3. Select **"Deploy from GitHub repo"**- Messenger: `https://your-app.railway.app/webhook/messenger`

4. Choose your repository: `Migochat`- WhatsApp: `https://your-app.railway.app/webhook/whatsapp`

5. Railway will auto-detect Python and start building

### 3.2 Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

#### **Required Variables:**

```bash
# Facebook Configuration
FB_APP_ID=your_facebook_app_id
FB_APP_SECRET=your_facebook_app_secret
FB_PAGE_ACCESS_TOKEN=your_page_access_token
FB_PAGE_ID=your_facebook_page_id
FB_SYSTEM_USER_TOKEN=your_system_user_token
FB_VERIFY_TOKEN=your_webhook_verify_token
FB_LEADCENTER_VERIFY_TOKEN=your_leadcenter_verify_token

# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_whatsapp_verify_token

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key

# Application Settings
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
TIMEZONE=Africa/Cairo

# Database (Railway will auto-provide PORT)
DATABASE_URL=sqlite:///database/bww_assistant.db
```

#### **Optional Variables:**

```bash
# BWW Store Integration (if using)
BWW_STORE_SECRET_KEY=your_bww_store_key
BWW_STORE_BASE_URL=https://api.bww-store.com

# Webhook URLs (update after getting Railway domain)
MESSENGER_WEBHOOK_URL=https://your-app.railway.app/webhook/messenger
WHATSAPP_WEBHOOK_URL=https://your-app.railway.app/webhook/whatsapp
LEADCENTER_WEBHOOK_URL=https://your-app.railway.app/webhook/leadcenter
```

### 3.3 Deploy

1. Click **"Deploy"** button
2. Wait for build to complete (~2-3 minutes)
3. Railway will provide your URL: `https://your-app.railway.app`

Railway auto-detects configuration from:
- `railway.json` - Build and deploy settings
- `Procfile` - Start command: `uvicorn Server.main:app --host 0.0.0.0 --port $PORT`
- `runtime.txt` - Python 3.13.2

---

## 🔗 Step 4: Configure Facebook/WhatsApp Webhooks

### 4.1 Get Your Railway URL

After deployment, Railway provides your app URL:
```
https://migochat-production-xxxx.up.railway.app
```

### 4.2 Configure Facebook Messenger Webhook

1. Go to [Facebook Developers Console](https://developers.facebook.com)
2. Select your app → **Messenger** → **Settings**
3. Click **"Add Callback URL"**
4. Enter:
   - **Callback URL**: `https://your-app.railway.app/webhook/messenger`
   - **Verify Token**: (same as `FB_VERIFY_TOKEN` in Railway)
5. Click **"Verify and Save"**
6. Subscribe to webhook fields:
   - ✅ messages
   - ✅ messaging_postbacks
   - ✅ messaging_optins
   - ✅ message_deliveries
   - ✅ message_reads

### 4.3 Configure WhatsApp Webhook

1. Go to [Facebook Developers Console](https://developers.facebook.com)
2. Select your app → **WhatsApp** → **Configuration**
3. Click **"Edit"** on Webhook
4. Enter:
   - **Callback URL**: `https://your-app.railway.app/webhook/whatsapp`
   - **Verify Token**: (same as `WHATSAPP_VERIFY_TOKEN` in Railway)
5. Click **"Verify and Save"**
6. Subscribe to: ✅ messages

---

## ✅ Step 5: Verify Deployment

### Test Health Endpoint

```bash
curl https://your-app.railway.app/
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "BWW Assistant"
}
```

### Test Dashboard

Open: `https://your-app.railway.app/dashboard`

### Test API

```bash
curl https://your-app.railway.app/api/stats
```

### Send Test Message

Send a test message from Messenger or WhatsApp and check Railway logs.

---

## 📊 Monitor Deployment

### View Logs

In Railway dashboard → **Logs** tab

Monitor:
- Incoming webhook events
- API requests
- Errors and warnings

### Check Metrics

Monitor in Railway dashboard:
- ✅ CPU usage
- ✅ Memory usage
- ✅ Request count

---

## 🐛 Troubleshooting

### Build Fails

Check `requirements.txt` is in root directory:
```bash
ls requirements.txt
```

### Webhook Verification Fails

1. Verify tokens match in Railway and Facebook
2. Test webhook URL:
```bash
curl "https://your-app.railway.app/webhook/messenger?hub.verify_token=YOUR_TOKEN&hub.challenge=test"
```
3. Check Railway logs

### Database Not Persisting

Railway provides ephemeral storage. For persistent database:

**Add Railway PostgreSQL:**
1. Railway dashboard → **New** → **Database** → **PostgreSQL**
2. Connect to your service
3. Update `DATABASE_URL` in variables

---

## 🔄 Update Deployment

```bash
# Push changes - Railway auto-deploys
git add .
git commit -m "Update feature"
git push origin main
```

### Manual Redeploy

Railway dashboard → **Deployments** → **Redeploy**

### Rollback

Select previous deployment → **Redeploy**

---

## 🔒 Security Checklist

Before going live:

- ✅ `DEBUG=False` in production
- ✅ All secrets in Railway variables (not in code)
- ✅ HTTPS enabled (Railway provides SSL)
- ✅ Webhook tokens are strong and unique
- ✅ Logs don't expose sensitive data

---

## 💰 Railway Pricing

- **Free Tier**: $5 credit/month
- **Pro Plan**: $20/month (recommended for production)

---

## ✅ Success Checklist

- ✅ `python deployment/check.py` passed
- ✅ Code pushed to GitHub
- ✅ Railway project created
- ✅ Environment variables configured
- ✅ Build successful
- ✅ Health check passes
- ✅ Dashboard accessible
- ✅ Webhooks verified
- ✅ Test messages working

---

## 🎉 Congratulations!

Your BWW AI Assistant is now live on Railway! 🚀

**Next Steps:**
- Monitor logs for 24 hours
- Test all features
- Configure custom domain (optional)
- Set up monitoring alerts

---

**Deployed with ❤️ using Railway**
