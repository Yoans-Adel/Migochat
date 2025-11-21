#!/usr/bin/env python3
"""
Bww-Assistant-chatbot Facebook Messenger Platform
Main entry point for running the application
"""

import uvicorn

from config.settings import settings

if __name__ == "__main__":
    print("🚀 Starting Bww-Assistant-chatbot Facebook Messenger Platform...")
    print(f"📱 Facebook App ID: {settings.FB_APP_ID}")
    print(f"🌐 Server: http://{settings.HOST}:{settings.PORT}")
    print(f"🔗 Webhook URL: http://{settings.HOST}:{settings.PORT}/webhook")
    print(f"📊 Dashboard: http://{settings.HOST}:{settings.PORT}/dashboard")
    print("=" * 60)

    uvicorn.run(
        "Server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
