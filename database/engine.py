"""
Database Engine Module
SQLAlchemy engine and session management
"""
import logging
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from database.models import Base

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_DIR = Path(__file__).parent
DATABASE_FILE = DATABASE_DIR / "bww_assistant.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Global engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine (singleton)"""
    global _engine
    
    if _engine is None:
        logger.info(f"Creating database engine: {DATABASE_URL}")
        
        # Ensure database directory exists
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Create engine with optimized settings for SQLite
        _engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False  # Set to True for SQL debugging
        )
        
        logger.info("Database engine created successfully")
    
    return _engine


def get_session_factory():
    """Get or create session factory (singleton)"""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        logger.info("Session factory created successfully")
    
    return _SessionLocal


def get_session() -> Session:
    """
    Get a new database session
    
    Returns:
        Session: SQLAlchemy session object
        
    Example:
        >>> session = get_session()
        >>> users = session.query(User).all()
        >>> session.close()
    """
    SessionLocal = get_session_factory()
    return SessionLocal()


def create_all_tables():
    """
    Create all database tables
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        engine = get_engine()
        logger.info("Creating all database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}", exc_info=True)
        return False


def drop_all_tables():
    """
    Drop all database tables (DANGEROUS!)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        engine = get_engine()
        logger.warning("⚠️  Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All database tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Error dropping database tables: {e}", exc_info=True)
        return False


def close_engine():
    """Close database engine and dispose of connections"""
    global _engine, _SessionLocal
    
    if _engine is not None:
        logger.info("Closing database engine...")
        _engine.dispose()
        _engine = None
        _SessionLocal = None
        logger.info("Database engine closed")


def get_database_path() -> Path:
    """Get the path to the database file"""
    return DATABASE_FILE


def database_exists() -> bool:
    """Check if database file exists"""
    return DATABASE_FILE.exists()
