#!/usr/bin/env python3
"""
Bww-Assistant-chatbot Facebook Messenger Platform
Main entry point for running the application
"""

import uvicorn
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Server.config import settings  # noqa: E402

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
