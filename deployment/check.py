#!/usr/bin/env python3
"""
Deployment Readiness Check
Validates all files are ready for Railway deployment
"""
import sys
from pathlib import Path


def check_files():
    """Check required files exist"""
    print("📋 Checking deployment files...\n")
    
    required = {
        "requirements.txt": "Python dependencies",
        "deployment/Procfile": "Process configuration",
        "deployment/runtime.txt": "Python version",
        "deployment/railway.json": "Railway settings",
        "Server/main.py": "FastAPI application",
        ".env": "Environment variables"
    }
    
    missing = []
    for file, desc in required.items():
        path = Path(file)
        if path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0


def check_imports():
    """Check imports work"""
    print("\n🔍 Checking imports...\n")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from Server.main import app
        from Server.config import settings
        print("  ✅ All imports working")
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def show_env_vars():
    """Show required environment variables"""
    print("\n📝 Required environment variables:\n")
    
    vars_needed = [
        "FB_APP_ID",
        "FB_APP_SECRET", 
        "FB_PAGE_ACCESS_TOKEN",
        "FB_VERIFY_TOKEN",
        "WHATSAPP_ACCESS_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID",
        "WHATSAPP_VERIFY_TOKEN",
        "GEMINI_API_KEY",
        "DEBUG",
        "TIMEZONE"
    ]
    
    for var in vars_needed:
        print(f"  • {var}")


def main():
    print("=" * 60)
    print("🚀 DEPLOYMENT READINESS CHECK")
    print("=" * 60)
    print()
    
    files_ok = check_files()
    imports_ok = check_imports()
    show_env_vars()
    
    print("\n" + "=" * 60)
    
    if files_ok and imports_ok:
        print("✅ DEPLOYMENT READY!")
        print("=" * 60)
        print("\n📦 Next steps:")
        print("\n1. Push to GitHub:")
        print("   git add .")
        print("   git commit -m 'Ready for deployment'")
        print("   git push")
        print("\n2. Deploy on Railway:")
        print("   - Go to https://railway.app")
        print("   - Connect GitHub repo")
        print("   - Add environment variables")
        print("   - Deploy!")
        print("\n3. Configure webhooks with your Railway URL")
        print()
        return 0
    else:
        print("❌ Fix issues above before deploying")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
