#!/usr/bin/env python3
"""
BWW Assistant Chatbot - Environment Setup
إعداد البيئة الافتراضية والتبعيات
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.environ['PYTHONPATH'] = str(project_root)

# Import centralized logging configuration
from config.logging_config import setup_logging, get_logger

# Lazy logging initialization
_logger_initialized = False
logger = None

def _init_logger():
    global logger, _logger_initialized
    if not _logger_initialized:
        setup_logging()
        logger = get_logger(__name__)
        _logger_initialized = True
    return logger


def create_virtual_environment():
    """إنشاء البيئة الافتراضية"""
    log = _init_logger()
    try:
        log.info("🐍 إنشاء البيئة الافتراضية...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        log.info("✅ تم إنشاء البيئة الافتراضية بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"❌ خطأ في إنشاء البيئة الافتراضية: {e}")
        return False


def install_dependencies():
    """تثبيت التبعيات"""
    log = _init_logger()
    try:
        log.info("📦 تثبيت التبعيات...")

        # تحديد مسار pip الصحيح حسب نظام التشغيل
        if os.name == 'nt':  # Windows
            pip_path = "venv/Scripts/pip"
        else:  # Unix/Linux/MacOS
            pip_path = "venv/bin/pip"

        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        log.info("✅ تم تثبيت التبعيات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"❌ خطأ في تثبيت التبعيات: {e}")
        return False


def create_directories():
    """إنشاء المجلدات المطلوبة"""
    log = _init_logger()
    try:
        log.info("📁 إنشاء المجلدات المطلوبة...")

        directories = [
            "logs",
            "data",
            "uploads",
            "temp"
        ]

        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            log.info(f"✅ تم إنشاء مجلد: {directory}")

        return True
    except Exception as e:
        log.error(f"❌ خطأ في إنشاء المجلدات: {e}")
        return False


def create_env_file():
    """إنشاء ملف .env"""
    log = _init_logger()
    try:
        log.info("⚙️ إنشاء ملف .env...")

        # Check if file exists and is read-only
        env_path = Path(".env")
        if env_path.exists():
            # Check if writable
            if not os.access(env_path, os.W_OK):
                log.error("❌ ملف .env موجود وفي وضع القراءة فقط")
                return False

        env_content = """# Facebook Configuration
FB_APP_ID=2111286849402188
FB_APP_SECRET=your_facebook_app_secret
FB_PAGE_ACCESS_TOKEN=your_page_access_token
FB_VERIFY_TOKEN=BWW_MESSENGER_VERIFY_TOKEN_2025

# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=767028226502871
WHATSAPP_VERIFY_TOKEN=BWW_WHATSAPP_VERIFY_TOKEN_2025

# Database
DATABASE_URL=sqlite:///./bww_assistant_chatbot.db

# Application Settings
DEBUG=False
TIMEZONE=Africa/Cairo
HOST=0.0.0.0
PORT=8000

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key
"""

        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)

        log.info("✅ تم إنشاء ملف .env")
        return True
    except PermissionError:
        log.error("❌ لا توجد صلاحيات للكتابة على ملف .env")
        return False
    except OSError as e:
        log.error(f"❌ خطأ في نظام الملفات: {e}")
        return False
    except Exception as e:
        log.error(f"❌ خطأ في إنشاء ملف .env: {e}")
        return False


def setup_environment():
    """إعداد البيئة الكاملة"""
    log = _init_logger()
    try:
        log.info("🎯 إعداد بيئة BWW Assistant Chatbot...")

        steps = [
            ("إنشاء المجلدات", create_directories),
            ("إنشاء البيئة الافتراضية", create_virtual_environment),
            ("تثبيت التبعيات", install_dependencies),
            ("إنشاء ملف .env", create_env_file)
        ]

        for step_name, step_func in steps:
            log.info(f"الخطوة: {step_name}")
            if not step_func():
                log.error(f"فشل في الخطوة: {step_name}")
                return False

        log.info("✅ تم إعداد البيئة بنجاح!")
        log.info("الخطوات التالية:")
        log.info("1. تحرير ملف .env بالمعلومات الصحيحة")
        log.info("2. تشغيل: python scripts/run.py")

        return True

    except Exception as e:
        log.error(f"❌ خطأ في إعداد البيئة: {e}")
        return False


if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
