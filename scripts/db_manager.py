#!/usr/bin/env python3
"""
Bww-AI-Assistant - Database Management Utility
أداة إدارة قاعدة البيانات
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.environ['PYTHONPATH'] = str(project_root)

# Import centralized logging configuration
from config.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def create_database():
    """Create a fresh database"""
    try:
        from config.database_config import create_database, DATABASE_DIR

        logger.info("🗄️ Creating fresh database...")

        # Create database directory if it doesn't exist
        DATABASE_DIR.mkdir(exist_ok=True)

        # Create database tables
        create_database()

        logger.info("✅ Fresh database created successfully")
        logger.info(f"📁 Database location: {DATABASE_DIR.absolute()}")

    except Exception as e:
        logger.error(f"❌ Error creating database: {e}")
        raise

def backup_database():
    """Create a backup of the current database"""
    try:
        from config.database_config import backup_database

        logger.info("💾 Creating database backup...")
        backup_file = backup_database()
        logger.info(f"✅ Backup created: {backup_file}")

    except Exception as e:
        logger.error(f"❌ Error creating backup: {e}")
        raise

def restore_database(backup_file):
    """Restore database from backup"""
    try:
        from config.database_config import restore_database

        if not Path(backup_file).exists():
            logger.error(f"❌ Backup file not found: {backup_file}")
            return

        logger.info(f"🔄 Restoring database from: {backup_file}")
        restore_database(backup_file)
        logger.info("✅ Database restored successfully")

    except Exception as e:
        logger.error(f"❌ Error restoring database: {e}")
        raise

def drop_database():
    """Drop all database tables"""
    try:
        from config.database_config import drop_database

        logger.warning("⚠️ Dropping all database tables...")
        drop_database()
        logger.info("✅ Database tables dropped successfully")

    except Exception as e:
        logger.error(f"❌ Error dropping database: {e}")
        raise

def check_database_health():
    """Check database health"""
    try:
        from config.database_config import check_database_health

        logger.info("🔍 Checking database health...")
        health = check_database_health()

        if health["status"] == "healthy":
            logger.info("✅ Database is healthy")
            logger.info(f"📊 Tables: {len(health['tables'])}")
            logger.info(f"🔗 Connection: {health['connection']}")
        else:
            logger.error(f"❌ Database is unhealthy: {health['error']}")

        return health

    except Exception as e:
        logger.error(f"❌ Error checking database health: {e}")
        return {"status": "unhealthy", "error": str(e)}

def clean_database():
    """Clean database by dropping and recreating"""
    try:
        logger.info("🧹 Cleaning database...")

        # Create backup first
        backup_database()

        # Drop and recreate
        drop_database()
        create_database()

        logger.info("✅ Database cleaned successfully")

    except Exception as e:
        logger.error(f"❌ Error cleaning database: {e}")
        raise

def show_database_status():
    """Show database status and information"""
    try:
        from config.database_config import DATABASE_DIR, DATABASE_URL

        logger.info("📊 Database Status:")
        logger.info("=" * 50)
        logger.info(f"📁 Database directory: {DATABASE_DIR.absolute()}")
        logger.info(f"🔗 Database URL: {DATABASE_URL}")

        # Check if database file exists
        db_file = DATABASE_DIR / "bww_ai_assistant.db"
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(db_file.stat().st_mtime)
            logger.info(f"📄 Database file: {db_file.name}")
            logger.info(f"📏 Size: {size_mb:.2f} MB")
            logger.info(f"📅 Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            logger.info("📭 Database file: Not found")

        # Check health
        health = check_database_health()
        logger.info(f"🏥 Health status: {health['status']}")

        # List backups
        backup_dir = DATABASE_DIR / "backups"
        if backup_dir.exists():
            backups = list(backup_dir.glob("*.db"))
            logger.info(f"💾 Backups: {len(backups)} files")
            for backup in sorted(backups)[-3:]:  # Show last 3 backups
                size_mb = backup.stat().st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(backup.stat().st_mtime)
                logger.info(f"   • {backup.name} ({size_mb:.2f} MB, {modified.strftime('%Y-%m-%d')})")

    except Exception as e:
        logger.error(f"❌ Error showing database status: {e}")

def main():
    """Main function"""
    logger.info("🎯 Bww-AI-Assistant Database Management Utility")
    logger.info("=" * 60)

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
                logger.error("❌ Please provide backup file path")
                logger.info("Usage: python scripts/db_manager.py restore <backup_file>")
        elif command == "drop":
            drop_database()
        elif command == "clean":
            clean_database()
        elif command == "health":
            check_database_health()
        elif command == "status":
            show_database_status()
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Available commands: create, backup, restore, drop, clean, health, status")
    else:
        # Default: show status
        show_database_status()
        logger.info("")
        logger.info("💡 Usage:")
        logger.info("  python scripts/db_manager.py status     # Show database status")
        logger.info("  python scripts/db_manager.py create     # Create fresh database")
        logger.info("  python scripts/db_manager.py backup     # Create backup")
        logger.info("  python scripts/db_manager.py restore <file>  # Restore from backup")
        logger.info("  python scripts/db_manager.py clean      # Clean database")
        logger.info("  python scripts/db_manager.py health     # Check database health")

if __name__ == "__main__":
    main()
