#!/usr/bin/env python3
"""
Database Health Check Script
Check database health and statistics
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


def health_check_cli():
    """Perform database health check from command line"""
    logger.info("=" * 60)
    logger.info("🏥 BWW Assistant - Database Health Check")
    logger.info("=" * 60)
    
    # Check if database exists
    db_path = get_database_path()
    if not database_exists():
        logger.error(f"\n❌ Database not found at: {db_path}")
        logger.info("\n💡 Run rebuild script to create database:")
        logger.info("   python database/scripts/rebuild.py")
        return False
    
    logger.info(f"\n📁 Database: {db_path}")
    logger.info(f"📊 Size: {db_path.stat().st_size:,} bytes")
    
    # Get database manager
    db_manager = get_database_manager()
    
    # Initialize database
    logger.info("\n🔄 Connecting to database...")
    if not db_manager.initialize():
        logger.error("\n❌ Failed to initialize database")
        return False
    
    # Perform health check
    logger.info("\n🏥 Running health check...")
    health_status = db_manager.health_check()
    
    # Display results
    logger.info("\n" + "=" * 60)
    logger.info("📋 HEALTH CHECK RESULTS")
    logger.info("=" * 60)
    
    status = health_status.get("status", "unknown")
    if status == "healthy":
        logger.info("✅ Status: HEALTHY")
    else:
        logger.error(f"❌ Status: {status.upper()}")
        if "error" in health_status:
            logger.error(f"   Error: {health_status['error']}")
        return False
    
    # Display database info
    logger.info(f"\n📁 Database Path: {health_status.get('database_path', 'N/A')}")
    logger.info(f"✓ Database Exists: {health_status.get('database_exists', False)}")
    logger.info(f"✓ Initialized: {health_status.get('initialized', False)}")
    
    # Display statistics
    logger.info("\n📊 DATABASE STATISTICS:")
    stats_keys = [
        'total_users',
        'active_users',
        'total_messages',
        'total_conversations',
        'active_conversations',
        'total_lead_activities',
        'total_posts',
        'total_ad_campaigns'
    ]
    
    for key in stats_keys:
        if key in health_status:
            label = key.replace('_', ' ').title()
            value = health_status[key]
            logger.info(f"   {label}: {value:,}")
    
    logger.info("\n✅ Health check completed successfully!")
    return True


if __name__ == "__main__":
    success = health_check_cli()
    sys.exit(0 if success else 1)
