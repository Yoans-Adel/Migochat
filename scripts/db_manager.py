#!/usr/bin/env python3
"""
Bww-AI-Assistant - Database Management Utility
أداة إدارة قاعدة البيانات
"""

import os
import sys
from pathlib import Path
from datetime import datetime

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


def create_database():
    """Create a fresh database"""
    log = _init_logger()
    try:
        from config.database_config import create_database, DATABASE_DIR

        log.info("🗄️ Creating fresh database...")

        # Create database directory if it doesn't exist
        DATABASE_DIR.mkdir(exist_ok=True)

        # Create database tables
        create_database()

        log.info("✅ Fresh database created successfully")
        log.info(f"📁 Database location: {DATABASE_DIR.absolute()}")

    except Exception as e:
        log.error(f"❌ Error creating database: {e}")
        raise


def backup_database():
    """Create a backup of the current database"""
    log = _init_logger()
    try:
        from config.database_config import backup_database

        log.info("💾 Creating database backup...")
        backup_file = backup_database()
        log.info(f"✅ Backup created: {backup_file}")

    except Exception as e:
        log.error(f"❌ Error creating backup: {e}")
        raise


def restore_database(backup_file):
    """Restore database from backup"""
    log = _init_logger()
    try:
        from config.database_config import restore_database

        if not Path(backup_file).exists():
            log.error(f"❌ Backup file not found: {backup_file}")
            return

        log.info(f"🔄 Restoring database from: {backup_file}")
        restore_database(backup_file)
        log.info("✅ Database restored successfully")

    except Exception as e:
        log.error(f"❌ Error restoring database: {e}")
        raise


def drop_database():
    """Drop all database tables"""
    log = _init_logger()
    try:
        from config.database_config import drop_database

        log.warning("⚠️ Dropping all database tables...")
        drop_database()
        log.info("✅ Database tables dropped successfully")

    except Exception as e:
        log.error(f"❌ Error dropping database: {e}")
        raise


def check_database_health():
    """Check database health"""
    log = _init_logger()
    try:
        from config.database_config import check_database_health

        log.info("🔍 Checking database health...")
        health = check_database_health()

        if health["status"] == "healthy":
            log.info("✅ Database is healthy")
            log.info(f"📊 Tables: {len(health['tables'])}")
            log.info(f"🔗 Connection: {health['connection']}")
        else:
            log.error(f"❌ Database is unhealthy: {health['error']}")

        return health

    except Exception as e:
        log.error(f"❌ Error checking database health: {e}")
        return {"status": "unhealthy", "error": str(e)}


def clean_database():
    """Clean database by dropping and recreating"""
    log = _init_logger()
    try:
        log.info("🧹 Cleaning database...")

        # Create backup first
        backup_database()

        # Drop and recreate
        drop_database()
        create_database()

        log.info("✅ Database cleaned successfully")

    except Exception as e:
        log.error(f"❌ Error cleaning database: {e}")
        raise


def show_database_status():
    """Show database status and information"""
    log = _init_logger()
    try:
        from config.database_config import DATABASE_DIR, DATABASE_URL

        log.info("📊 Database Status:")
        log.info("=" * 50)
        log.info(f"📁 Database directory: {DATABASE_DIR.absolute()}")
        log.info(f"🔗 Database URL: {DATABASE_URL}")

        # Check if database file exists
        db_file = DATABASE_DIR / "bww_ai_assistant.db"
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(db_file.stat().st_mtime)
            log.info(f"📄 Database file: {db_file.name}")
            log.info(f"📏 Size: {size_mb:.2f} MB")
            log.info(f"📅 Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            log.info("📛 Database file: Not found")

        # Check health
        health = check_database_health()
        log.info(f"🏥 Health status: {health['status']}")

        # List backups
        backup_dir = DATABASE_DIR / "backups"
        if backup_dir.exists():
            backups = list(backup_dir.glob("*.db"))
            log.info(f"💾 Backups: {len(backups)} files")
            for backup in sorted(backups)[-3:]:  # Show last 3 backups
                size_mb = backup.stat().st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(backup.stat().st_mtime)
                log.info(f"   • {backup.name} ({size_mb:.2f} MB, {modified.strftime('%Y-%m-%d')}))")

    except Exception as e:
        log.error(f"❌ Error showing database status: {e}")


def main():
    """Main function"""
    log = _init_logger()
    log.info("🎯 Bww-AI-Assistant Database Management Utility")
    log.info("=" * 60)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "create":
            create_database()
        elif command == "backup":
            backup_database()
        elif command == "restore":
            if len(sys.argv) > 2:
                restore_database(sys.argv[2])
            else:
                log.error("❌ Please provide backup file path")
                log.info("Usage: python scripts/db_manager.py restore <backup_file>")
        elif command == "drop":
            drop_database()
        elif command == "clean":
            clean_database()
        elif command == "health":
            check_database_health()
        elif command == "status":
            show_database_status()
        else:
            log.error(f"❌ Unknown command: {command}")
            log.info("Available commands: create, backup, restore, drop, clean, health, status")
    else:
        # Default: show status
        show_database_status()
        log.info("")
        log.info("💡 Usage:")
        log.info("  python scripts/db_manager.py status     # Show database status")
        log.info("  python scripts/db_manager.py create     # Create fresh database")
        log.info("  python scripts/db_manager.py backup     # Create backup")
        log.info("  python scripts/db_manager.py restore <file>  # Restore from backup")
        log.info("  python scripts/db_manager.py clean      # Clean database")
        log.info("  python scripts/db_manager.py health     # Check database health")


if __name__ == "__main__":
    main()
