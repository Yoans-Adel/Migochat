"""
BWW Assistant - Database Context Facade
This file maintains backward compatibility by re-exporting
the new database module's context manager functionality.

DEPRECATED: This file exists for backward compatibility only.
New code should import directly from the database package:
    from database import get_db_session, get_db_session_with_commit, etc.
"""

import logging

# Import everything from the new database module
from database import (
    get_db_session,
    get_db_session_with_commit,
    DatabaseSessionManager,
    execute_db_operation,
)

logger = logging.getLogger(__name__)

# Global session manager instance (for backward compatibility)
session_manager = DatabaseSessionManager()

# Convenience functions (for backward compatibility)
def get_safe_session(auto_commit: bool = False):
    """
    Get safe database session.

    DEPRECATED: Import from database package instead:
        from database import get_db_session, get_db_session_with_commit
    """
    if auto_commit:
        return get_db_session_with_commit()
    else:
        return get_db_session()

# Re-export for convenience
__all__ = [
    "get_db_session",
    "get_db_session_with_commit",
    "DatabaseSessionManager",
    "execute_db_operation",
    "session_manager",
    "get_safe_session",
]
