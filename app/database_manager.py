"""
BWW Assistant - Database Manager Facade
This file maintains backward compatibility by re-exporting
the new database module's manager functionality.

DEPRECATED: This file exists for backward compatibility only.
New code should import directly from the database package:
    from database import get_database_manager, initialize_database, etc.
"""

import logging
from typing import Dict, Any

# Import everything from the new database module
from database import (
    get_database_manager as _get_database_manager,
    initialize_database as _initialize_database,
    get_session as _get_session,
    get_db_session_with_commit,
    DatabaseManager,
)

logger = logging.getLogger(__name__)

# For backward compatibility, expose the same interface
db_manager = _get_database_manager()

def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    DEPRECATED: Import from database package instead:
        from database import get_database_manager
    """
    return _get_database_manager()

def initialize_database() -> bool:
    """
    Initialize database.
    
    DEPRECATED: Import from database package instead:
        from database import initialize_database
    """
    return _initialize_database()

def get_session():
    """
    Get database session.
    
    DEPRECATED: Import from database package instead:
        from database import get_session
    """
    return _get_session()

def get_session_context():
    """
    Get database session with context manager.
    
    DEPRECATED: Import from database package instead:
        from database import get_db_session_with_commit
    """
    return get_db_session_with_commit()

# Re-export for convenience
__all__ = [
    "db_manager",
    "get_database_manager",
    "initialize_database",
    "get_session",
    "get_session_context",
    "DatabaseManager",
]
