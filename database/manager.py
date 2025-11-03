"""
Database Manager Module
High-level database operations and management
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.engine import (
    get_engine,
    get_session,
    create_all_tables,
    drop_all_tables,
    get_database_path,
    database_exists
)
from database.models import User, Message, Conversation, LeadActivity, Post, AdCampaign

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Centralized database management"""
    
    def __init__(self):
        self._initialized = False
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """
        Initialize database connection and create tables
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self._initialized:
                self.logger.info("Database already initialized")
                return True
            
            self.logger.info("🗄️  Initializing database...")
            
            # Get engine (creates it if needed)
            engine = get_engine()
            
            # Create tables if they don't exist
            if not database_exists():
                self.logger.info("Database file doesn't exist, creating tables...")
                create_all_tables()
            else:
                self.logger.info(f"Database exists at: {get_database_path()}")
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            self._initialized = True
            self.logger.info("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
            return False
    
    def create_tables(self) -> bool:
        """Create all database tables"""
        try:
            self.logger.info("Creating database tables...")
            return create_all_tables()
        except Exception as e:
            self.logger.error(f"Error creating tables: {e}", exc_info=True)
            return False
    
    def drop_tables(self) -> bool:
        """Drop all database tables (DANGEROUS!)"""
        try:
            self.logger.warning("⚠️  Dropping all tables...")
            return drop_all_tables()
        except Exception as e:
            self.logger.error(f"Error dropping tables: {e}", exc_info=True)
            return False
    
    def rebuild_database(self) -> bool:
        """
        Rebuild database from scratch (drop and recreate)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.warning("🔄 Rebuilding database...")
            
            # Drop existing tables
            if not self.drop_tables():
                return False
            
            # Create new tables
            if not self.create_tables():
                return False
            
            self._initialized = True
            self.logger.info("✅ Database rebuilt successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Database rebuild failed: {e}", exc_info=True)
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check database health and connectivity
        
        Returns:
            dict: Health check results
        """
        try:
            engine = get_engine()
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            # Get database stats
            stats = self.get_database_stats()
            
            return {
                "status": "healthy",
                "database_path": str(get_database_path()),
                "database_exists": database_exists(),
                "initialized": self._initialized,
                **stats
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            dict: Database statistics
        """
        try:
            # Use context manager for safe session handling
            from database.context import get_db_session
            
            with get_db_session() as session:
                stats = {
                    "total_users": session.query(User).count(),
                    "total_messages": session.query(Message).count(),
                    "total_conversations": session.query(Conversation).count(),
                    "total_lead_activities": session.query(LeadActivity).count(),
                    "total_posts": session.query(Post).count(),
                    "total_ad_campaigns": session.query(AdCampaign).count(),
                    "active_users": session.query(User).filter(User.is_active.is_(True)).count(),
                    "active_conversations": session.query(Conversation).filter(Conversation.is_active.is_(True)).count(),
                }
                
                return stats
            
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}", exc_info=True)
            return {}
    
    def close(self):
        """Close database connections"""
        try:
            from database.engine import close_engine
            close_engine()
            self._initialized = False
            self.logger.info("Database connections closed")
        except Exception as e:
            self.logger.error(f"Error closing database: {e}", exc_info=True)


# Global database manager instance
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance (singleton)
    
    Returns:
        DatabaseManager: Global database manager
    """
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager()
    
    return _db_manager


# Convenience functions
def initialize_database() -> bool:
    """Initialize database"""
    return get_database_manager().initialize()


def rebuild_database() -> bool:
    """Rebuild database from scratch"""
    return get_database_manager().rebuild_database()


def get_db_stats() -> Dict[str, Any]:
    """Get database statistics"""
    return get_database_manager().get_database_stats()


def check_db_health() -> Dict[str, Any]:
    """Check database health"""
    return get_database_manager().health_check()
