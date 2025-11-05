#!/usr/bin/env python3
"""
Database Backup Script
Create backups of the database
"""
import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.engine import get_database_path, database_exists  # noqa: E402

from typing import Optional  # noqa: E402


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def backup_database_cli(backup_dir: Optional[str] = None) -> bool:
    """
    Create database backup from command line

    Args:
        backup_dir: Optional backup directory path
    """
    logger.info("=" * 60)
    logger.info("💾 BWW Assistant - Database Backup")
    logger.info("=" * 60)

    # Check if database exists
    db_path = get_database_path()
    if not database_exists():
        logger.error(f"❌ Database not found at: {db_path}")
        return False

    # Setup backup directory
    backup_path_obj: Path
    if backup_dir is None:
        backup_path_obj = db_path.parent / "backups"
    else:
        backup_path_obj = Path(backup_dir)

    backup_path_obj.mkdir(parents=True, exist_ok=True)

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"bww_assistant_backup_{timestamp}.db"
    backup_file_path = backup_path_obj / backup_filename

    try:
        logger.info(f"\n📁 Source: {db_path}")
        logger.info(f"💾 Backup: {backup_file_path}")
        logger.info("\n🔄 Creating backup...")

        # Copy database file
        shutil.copy2(db_path, backup_file_path)

        # Get backup size
        backup_size = backup_file_path.stat().st_size

        logger.info("\n✅ Backup created successfully!")
        logger.info(f"📊 Size: {backup_size:,} bytes")
        logger.info(f"📁 Location: {backup_file_path}")

        # List recent backups
        backups = sorted(backup_path_obj.glob("bww_assistant_backup_*.db"), reverse=True)
        if len(backups) > 1:
            logger.info(f"\n📚 Recent backups ({len(backups)} total):")
            for i, backup in enumerate(backups[:5], 1):
                size = backup.stat().st_size
                logger.info(f"   {i}. {backup.name} ({size:,} bytes)")

        return True

    except Exception as e:
        logger.error(f"\n❌ Backup failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = backup_database_cli()
    sys.exit(0 if success else 1)
