"""Database Configuration - Centralized

This module provides database configuration by importing from the main database package.
All database models, enums, and utilities are in database/ package.
"""

from pathlib import Path

# Import everything from the database package
from database import (
    # Engine and session
    get_engine,
    get_session,
    get_db_session,
    create_all_tables,
    drop_all_tables,
    database_exists,
    get_database_path,
    # Models
    Base,
    User,
    Message,
    Conversation,
    LeadActivity,
    Post,
    AdCampaign,
    AppSettings,
    # Enums
    MessageDirection,
    MessageStatus,
    MessageSource,
    LeadStage,
    CustomerLabel,
    CustomerType,
    PostType,
    Governorate,
    # Utilities
    enum_to_value,
    enum_to_name,
    safe_enum_comparison,
    DatabaseManager,
    get_database_manager
)

# Legacy compatibility
DATABASE_DIR = Path("database")
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/bww_ai_assistant.db"
engine = get_engine()
SessionLocal = get_session

# Database utility functions (delegated to database package)


def create_database():
    """Create all database tables"""
    create_all_tables()
    print("✅ Database tables created successfully")


def drop_database():
    """Drop all database tables"""
    drop_all_tables()
    print("✅ Database tables dropped successfully")


def backup_database():
    """Create a backup of the database"""
    manager = get_database_manager()
    return manager.backup_database()


def restore_database(backup_file: str) -> None:
    """Restore database from backup"""
    manager = get_database_manager()
    manager.restore_database(backup_file)


def check_database_health():
    """Check database health and connectivity"""
    manager = get_database_manager()
    return manager.health_check()


__all__ = [
    # Engine
    'engine',
    'SessionLocal',
    'DATABASE_URL',
    'DATABASE_DIR',
    # Functions
    'get_session',
    'get_db_session',
    'create_database',
    'drop_database',
    'backup_database',
    'restore_database',
    'check_database_health',
    # Models
    'Base',
    'User',
    'Message',
    'Conversation',
    'LeadActivity',
    'Post',
    'AdCampaign',
    'AppSettings',
    # Enums
    'MessageDirection',
    'MessageStatus',
    'MessageSource',
    'LeadStage',
    'CustomerLabel',
    'CustomerType',
    'PostType',
    'Governorate',
    # Utilities
    'enum_to_value',
    'enum_to_name',
]
