"""
BWW Assistant Chatbot - Database Package
Professional database management with modular architecture
"""

# Public API imports
from database.enums import (
    MessageSource,
    PostType,
    LeadStage,
    CustomerLabel,
    CustomerType,
    Governorate,
    MessageDirection,
    MessageStatus
)

from database.models import (
    Base,
    User,
    Message,
    Conversation,
    LeadActivity,
    Post,
    AdCampaign,
    AppSettings
)

from database.engine import (
    get_engine,
    get_session,
    create_all_tables,
    drop_all_tables,
    database_exists,
    get_database_path
)

from database.manager import (
    DatabaseManager,
    get_database_manager,
    initialize_database,
    rebuild_database
)

from database.context import (
    get_db_session,
    get_db_session_with_commit,
    DatabaseSessionManager,
    get_safe_session,
    execute_db_operation
)

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
    "AppSettings",
    # Engine
    "get_engine",
    "get_session",
    "create_all_tables",
    "drop_all_tables",
    "database_exists",
    "get_database_path",
    # Manager
    "DatabaseManager",
    "get_database_manager",
    "initialize_database",
    "rebuild_database",
    # Context
    "get_db_session",
    "get_db_session_with_commit",
    "DatabaseSessionManager",
    "get_safe_session",
    "execute_db_operation",
]
