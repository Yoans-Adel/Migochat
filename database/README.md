# BWW Assistant - Database Module

Professional database management module for the BWW Assistant chatbot application.

## 📁 Structure

```Structure
database/
├── __init__.py              # Public API entry point
├── enums.py                 # All enumeration types
├── models.py                # SQLAlchemy ORM models
├── engine.py                # Database engine & session management
├── manager.py               # High-level database operations
├── context.py               # Context managers for safe session handling
├── cli.py                   # Master CLI utility
├── README.md                # This file
├── bww_assistant.db         # SQLite database file (generated)
├── scripts/                 # CLI utilities
│   ├── __init__.py
│   ├── rebuild.py          # Rebuild database from scratch
│   ├── backup.py           # Create database backups
│   └── health.py           # Health check and statistics
└── backups/                # Database backups folder (generated)
```

## 🚀 Quick Start

### Using the Master CLI

The easiest way to manage the database is through the master CLI:

```bash
# Check database health
python database/cli.py health

# Rebuild database (drops all data!)
python database/cli.py rebuild

# Create backup
python database/cli.py backup

# Show statistics
python database/cli.py stats
```

### Using Individual Scripts

```bash
# Health check
python database/scripts/health.py

# Rebuild database
python database/scripts/rebuild.py

# Create backup
python database/scripts/backup.py
```

## 📦 Module Usage

### Basic Usage

```python
from database import (
    # Models
    User, Message, Conversation, LeadActivity, Post, AdCampaign,
    
    # Enums
    MessageSource, PostType, LeadStage, CustomerLabel,
    
    # Functions
    initialize_database,
    get_session,
    get_db_session,
)

# Initialize database
initialize_database()

# Use context manager for safe database access
with get_db_session() as db:
    users = db.query(User).all()
    print(f"Total users: {len(users)}")
```

### Context Managers

The module provides several context managers for safe database operations:

```python
from database import (
    get_db_session,
    get_db_session_with_commit,
    DatabaseSessionManager,
    execute_db_operation,
)

# 1. Basic session (no auto-commit)
with get_db_session() as db:
    user = db.query(User).first()
    # Read operations only

# 2. Session with auto-commit
with get_db_session_with_commit() as db:
    new_user = User(psid="123", first_name="John")
    db.add(new_user)
    # Automatically commits on success

# 3. Session manager with retry logic
manager = DatabaseSessionManager(max_retries=3)
with manager.get_session(auto_commit=True) as db:
    # Operations with automatic retry on failure
    pass

# 4. Execute operation with retry
def create_user(db, psid, name):
    user = User(psid=psid, first_name=name)
    db.add(user)
    return user

user = execute_db_operation(create_user, "123", "John")
```

### Database Manager

```python
from database import get_database_manager

# Get database manager instance
db_manager = get_database_manager()

# Initialize database
db_manager.initialize()

# Create tables
db_manager.create_tables()

# Rebuild database (drops all tables)
db_manager.rebuild_database()

# Health check
health = db_manager.health_check()
print(f"Status: {health['status']}")

# Get statistics
stats = db_manager.get_database_stats()
print(f"Total users: {stats['total_users']}")
```

## 🗄️ Database Models

### User

Lead/customer information with tracking fields.

```python
from database import User, LeadStage, CustomerLabel

user = User(
    psid="123456789",
    first_name="John",
    last_name="Doe",
    platform="facebook",
    lead_stage=LeadStage.INTAKE,
    customer_label=CustomerLabel.NEW_CUSTOMER,
)
```

### Message

Message tracking with source attribution.

```python
from database import Message, MessageSource, MessageDirection

message = Message(
    user_id=1,
    sender_id="123456789",
    recipient_id="page_id",
    message_text="Hello!",
    direction=MessageDirection.INBOUND,
    message_source=MessageSource.AD,
    post_id=1,
)
```

### Conversation

Conversation thread management.

### LeadActivity

Lead stage/status change tracking.

### Post

Facebook post tracking with product information.

### AdCampaign

Ad campaign tracking for attribution.

## 🔧 Configuration

The database uses SQLite by default with the following location:

```database
database/bww_assistant.db
```

To change the database location, modify `DATABASE_FILE` in `database/engine.py`.

## 🛡️ Best Practices

1. **Always use context managers** for database operations:

   ```python
   # ✅ Good
   with get_db_session() as db:
       users = db.query(User).all()
   
   # ❌ Bad
   session = get_session()
   users = session.query(User).all()
   session.close()  # Easy to forget!
   ```

2. **Use auto-commit for write operations**:

   ```python
   with get_db_session_with_commit() as db:
       user = User(psid="123", first_name="John")
       db.add(user)
       # Auto-commits on success
   ```

3. **Handle errors properly**:

   ```python
   try:
       with get_db_session_with_commit() as db:
           # Operations
           pass
   except Exception as e:
       logger.error(f"Database error: {e}")
       # Handle error
   ```

4. **Use the retry wrapper for critical operations**:

   ```python
   from database import execute_db_operation
   
   result = execute_db_operation(my_operation, arg1, arg2)
   ```

## 🔄 Import Usage

All imports should be done directly from the `database` package:

```python
# Correct way to import
from database import User, Message, get_session

# Import models
from database import User, Message, Conversation, LeadStage

# Import enums
from database import MessageDirection, MessageStatus, MessageSource

# Import engine functions
from database import get_session, create_all_tables
```

**Note:** The old `app.database` module has been removed. All code now uses direct imports from the `database` package.

## 📊 CLI Usage Examples

```bash
# Check database health and statistics
python database/cli.py health

# Rebuild database (interactive confirmation)
python database/cli.py rebuild

# Create timestamped backup
python database/cli.py backup

# Backup to specific directory
python database/cli.py backup --backup-dir ./my-backups/
```

## 🐛 Troubleshooting

### Database not found

```bash
python database/scripts/rebuild.py
```

### Import errors

Make sure you're running commands from the project root:

```bash
cd /path/to/Migochat
python database/cli.py health
```

### Connection issues

Check the database file exists and has proper permissions:

```bash
ls -la database/bww_assistant.db
```

## 📝 Development

### Adding New Models

1. Add model to `database/models.py`
2. Add relationships if needed
3. Update `database/__init__.py` exports
4. Rebuild database: `python database/cli.py rebuild`

### Adding New Enums

1. Add enum to `database/enums.py`
2. Update `database/__init__.py` exports
3. Use in models as needed

## 🔒 Security Notes

- Database file should not be committed to version control (add to `.gitignore`)
- Backup files should be stored securely
- Use environment variables for sensitive database credentials (if not using SQLite)

## 📚 Additional Resources

- SQLAlchemy Documentation: <https://docs.sqlalchemy.org/>
- SQLite Documentation: <https://www.sqlite.org/docs.html>
- FastAPI Database Guide: <https://fastapi.tiangolo.com/tutorial/sql-databases/>
