"""
BWW Assistant - Database Module Facade
This file maintains backward compatibility with the old app.database imports
by re-exporting everything from the new database package.
"""

# Import everything from the new database module
from database import (
    # Enums
    MessageSource,
    PostType,
    LeadStage,
    CustomerLabel,
    CustomerType,
    Governorate,
    MessageDirection,
    MessageStatus,
    
    # Models
    Base,
    User,
    Message,
    Conversation,
    LeadActivity,
    Post,
    AdCampaign,
    
    # Engine functions
    get_engine,
    get_session,
    create_all_tables,
    drop_all_tables,
    database_exists,
    get_database_path,
    
    # Manager functions
    get_database_manager,
    initialize_database,
    rebuild_database,
    
    # Context managers
    get_db_session,
    get_db_session_with_commit,
    DatabaseSessionManager,
    execute_db_operation,
)

# Backward compatibility aliases
def create_database():
    """
    Legacy function for backward compatibility.
    Creates database tables using the new Database Manager.
    """
    return initialize_database()

# Re-export for convenience
__all__ = [
    # Enums
    "MessageSource",
    "PostType",
    "LeadStage",
    "CustomerLabel",
    "CustomerType",
    "Governorate",
    "MessageDirection",
    "MessageStatus",
    
    # Models
    "Base",
    "User",
    "Message",
    "Conversation",
    "LeadActivity",
    "Post",
    "AdCampaign",
    
    # Functions
    "get_engine",
    "get_session",
    "create_all_tables",
    "drop_all_tables",
    "database_exists",
    "get_database_path",
    "get_database_manager",
    "initialize_database",
    "rebuild_database",
    "create_database",
    
    # Context managers
    "get_db_session",
    "get_db_session_with_commit",
    "DatabaseSessionManager",
    "execute_db_operation",
]
