"""Database Configuration - Centralized

This module provides database configuration by importing from the main database package.
All database models, enums, and utilities are in database/ package.
"""

from pathlib import Path
from typing import Generator
from sqlalchemy.orm import sessionmaker, Session

# Import everything from the database package
from database import (
    # Engine and session
    get_engine,
    create_all_tables,
    drop_all_tables,
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
    get_database_manager
)

# Legacy compatibility
DATABASE_DIR = Path("database")
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/bww_assistant.db"
engine = get_engine()

# Create SessionLocal from engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database utility functions (delegated to database package)


def get_session() -> Generator[Session, None, None]:
    """Get database session generator for FastAPI dependency injection"""
    from database import get_db_session
    with get_db_session() as session:
        yield session


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
    import shutil
    from datetime import datetime

    backup_dir = DATABASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)

    db_path = get_database_path()
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"bww_assistant_backup_{timestamp}.db"

    shutil.copy2(db_path, backup_file)
    print(f"✅ Database backup created: {backup_file}")
    return str(backup_file)


def restore_database(backup_file: str) -> None:
    """Restore database from backup"""
    import shutil
    from pathlib import Path

    backup_path = Path(backup_file)
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_file}")

    db_path = get_database_path()
    shutil.copy2(backup_path, db_path)
    print(f"✅ Database restored from: {backup_file}")


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
