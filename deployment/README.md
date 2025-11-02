# Railway Deployment# Deployment Folder

Simple deployment to Railway for permanent HTTPS URL.Simple deployment configs for Railway/Render.

## Quick Deploy## Quick Deploy

```bashPush to GitHub, then connect Railway or Render.

# 1. Validate

python deployment/check.pyThat's it!


# 2. Push to GitHub
git push

# 3. Deploy on Railway
# - Go to railway.app
# - Connect GitHub
# - Add environment variables
# - Deploy!
```

## Files

- `Procfile` - Process command
- `runtime.txt` - Python 3.13.2
- `railway.json` - Railway config
- `check.py` - Validation script

## Environment Variables

Copy these from your `.env` to Railway:

- FB_APP_ID
- FB_APP_SECRET
- FB_PAGE_ACCESS_TOKEN
- FB_VERIFY_TOKEN
- WHATSAPP_ACCESS_TOKEN
- WHATSAPP_PHONE_NUMBER_ID
- WHATSAPP_VERIFY_TOKEN
- GEMINI_API_KEY
- DEBUG
- TIMEZONE

## After Deployment

Configure Meta webhooks with your Railway URL:

- Messenger: `https://your-app.railway.app/webhook/messenger`
- WhatsApp: `https://your-app.railway.app/webhook/whatsapp`
