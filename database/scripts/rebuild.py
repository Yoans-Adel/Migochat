#!/usr/bin/env python3
"""
Database Rebuild Script
Rebuild database from scratch
"""
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.manager import get_database_manager
from database.engine import get_database_path, database_exists

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def rebuild_database_cli():
    """Rebuild database from command line"""
    logger.info("=" * 60)
    logger.info("🔄 BWW Assistant - Database Rebuild")
    logger.info("=" * 60)
    
    # Get database manager
    db_manager = get_database_manager()
    
    # Check if database exists
    db_path = get_database_path()
    if database_exists():
        logger.warning(f"⚠️  Database exists at: {db_path}")
        logger.warning("⚠️  This will DELETE all existing data!")
        
        response = input("\n❓ Are you sure you want to rebuild? (yes/no): ")
        if response.lower() != "yes":
            logger.info("❌ Rebuild cancelled")
            return False
    
    # Rebuild database
    logger.info("\n🔨 Rebuilding database...")
    
    if db_manager.rebuild_database():
        logger.info("\n✅ Database rebuilt successfully!")
        logger.info(f"📁 Database location: {db_path}")
        
        # Show stats
        stats = db_manager.get_database_stats()
        logger.info("\n📊 Database Statistics:")
        for key, value in stats.items():
            logger.info(f"   {key}: {value}")
        
        return True
    else:
        logger.error("\n❌ Database rebuild failed")
        return False


if __name__ == "__main__":
    success = rebuild_database_cli()
    sys.exit(0 if success else 1)
