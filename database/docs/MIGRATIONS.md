# 🔄 Database Migrations Guide

**Project**: Migochat  
**Migration Tool**: Alembic (Planned - Not Yet Implemented)  
**Current Status**: Direct SQLAlchemy Models ✅  
**Last Updated**: 2025-11-12

---

## 📋 Overview

Currently, Migochat uses **direct SQLAlchemy model creation** without migrations. This document outlines the current approach and future migration strategy.

---

## 🎯 Current State

### How It Works Now:

```python
# database/engine.py
from database.models import Base
from database.engine import engine

# Create all tables from models
Base.metadata.create_all(bind=engine)
```

**Advantages**:
- ✅ Simple and fast development
- ✅ No migration files to manage
- ✅ Easy schema changes (drop + recreate)

**Disadvantages**:
- ❌ No version control for schema
- ❌ Can't track changes over time
- ❌ Risk of data loss on schema changes
- ❌ No rollback capability

---

## 🚀 Future: Alembic Migrations

### Why Alembic?

Alembic is the standard migration tool for SQLAlchemy, providing:

- ✅ **Version control** for database schema
- ✅ **Auto-generate** migrations from model changes
- ✅ **Upgrade/Downgrade** migrations
- ✅ **Branch management** for parallel development
- ✅ **Production-safe** schema changes

---

## 📦 Setup Alembic (When Needed)

### Step 1: Install Alembic

```bash
# Already in requirements.txt
pip install alembic
```

### Step 2: Initialize Alembic

```bash
cd F:\working - yoans\Migochat

# Initialize Alembic in database/migrations/
alembic init database/migrations
```

**This creates**:
```
database/
  migrations/
    versions/          ← Migration files
    env.py            ← Environment config
    script.py.mako    ← Template for migrations
    README
  alembic.ini         ← Alembic configuration
```

### Step 3: Configure Alembic

Edit `database/migrations/env.py`:

```python
# database/migrations/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import your Base
from database.models import Base

# this is the Alembic Config object
config = context.config

# Set target metadata
target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode."""
    
    # Get database URL from config
    from config.settings import settings
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Run migrations
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Edit `alembic.ini`:

```ini
# alembic.ini

# Database URL (will be overridden by env.py)
sqlalchemy.url = sqlite:///database/bww_assistant.db

# Migration file location
script_location = database/migrations

# Template directory
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
```

---

## 🔧 Migration Workflow

### Create Initial Migration (Baseline)

```bash
# Generate migration from current models
alembic revision --autogenerate -m "Initial database schema"

# This creates:
# database/migrations/versions/20251111_1230_abc123_initial_database_schema.py
```

**Generated migration**:
```python
# database/migrations/versions/20251111_1230_abc123_initial.py
"""Initial database schema

Revision ID: abc123
Revises: 
Create Date: 2025-11-11 12:30:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('psid', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        # ... all columns
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('psid')
    )
    
    # Create other tables...

def downgrade():
    # Drop tables in reverse order
    op.drop_table('lead_activities')
    op.drop_table('messages')
    op.drop_table('users')
    # ...
```

### Apply Migration

```bash
# Apply all pending migrations
alembic upgrade head

# Output:
# INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial database schema
```

### Create New Migration (After Model Changes)

**Example**: Add `email` field to User model

1. **Modify model**:
```python
# database/models.py
class User(Base):
    # ... existing fields
    email: Mapped[Optional[str]] = mapped_column(String(255))  # NEW
```

2. **Generate migration**:
```bash
alembic revision --autogenerate -m "Add email to users"

# Creates: 20251111_1245_def456_add_email_to_users.py
```

3. **Review generated migration**:
```python
def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('users', 'email')
```

4. **Apply migration**:
```bash
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

---

## 📊 Migration Commands Reference

### Check Current Version
```bash
alembic current
# Output: abc123 (head)
```

### Show Migration History
```bash
alembic history
# Output:
# def456 -> abc123 (head), Add email to users
# abc123 -> <base>, Initial database schema
```

### Show Pending Migrations
```bash
alembic heads
alembic show head
```

### Generate SQL (Without Applying)
```bash
# See SQL that would be executed
alembic upgrade head --sql

# Output:
# CREATE TABLE users (...);
# CREATE TABLE messages (...);
```

---

## 🎯 Best Practices

### 1. Always Review Auto-Generated Migrations

Alembic isn't perfect. **Always check**:
- ✅ Column types are correct
- ✅ Constraints are preserved
- ✅ Indexes are created
- ✅ Foreign keys are maintained

### 2. Data Migrations

For complex changes, add data migration:

```python
def upgrade():
    # Schema change
    op.add_column('users', sa.Column('full_name', sa.String(200)))
    
    # Data migration
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE users 
            SET full_name = first_name || ' ' || last_name
        """)
    )
    
    # Cleanup
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

### 3. Test Migrations

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test re-upgrade
alembic upgrade head
```

### 4. Production Deployment

```bash
# 1. Backup database first!
python scripts/db_manager.py backup

# 2. Apply migrations
alembic upgrade head

# 3. Verify
python scripts/db_manager.py health
```

---

## ⚠️ Common Issues

### Issue 1: Alembic Can't Detect Changes

**Cause**: Models not imported in `env.py`

**Solution**:
```python
# database/migrations/env.py
from database.models import Base, User, Message  # Import all models
target_metadata = Base.metadata
```

### Issue 2: Migration Conflicts

**Cause**: Multiple developers creating migrations

**Solution**:
```bash
# Merge migration branches
alembic merge -m "Merge migrations" head1 head2
```

### Issue 3: Can't Downgrade

**Cause**: Data loss in downgrade

**Solution**: Make downgrade data-safe:
```python
def downgrade():
    # Don't drop column with data
    # Instead, mark as deprecated
    op.alter_column('users', 'old_field', 
                    comment='DEPRECATED - use new_field')
```

---

## 🔄 Migration Strategy for Migochat

### Phase 1: Current (No Migrations)
- ✅ Direct model creation
- ✅ Fast development
- ⚠️ Development only

### Phase 2: Baseline Migration (Before Production)
```bash
# Create initial migration
alembic revision --autogenerate -m "Baseline schema"
alembic upgrade head
```

### Phase 3: Production Migrations (Future)
- ✅ All schema changes via migrations
- ✅ Version control
- ✅ Rollback capability

---

## 📝 Migration File Structure (Future)

When Alembic is initialized, it will create this structure:

```
database/
  migrations/                      ← Currently empty (placeholder)
    versions/                      ← Will contain migration files
      20251111_1200_abc123_initial_schema.py
      20251115_1430_def456_add_email_field.py
      20251120_0900_ghi789_add_lead_tags.py
    env.py                        ← Will be created by Alembic
    script.py.mako               ← Will be created by Alembic
    README                        ← Will be created by Alembic
alembic.ini                       ← Will be created at project root
```

**Note**: The `migrations/` folder currently exists but is empty. It will be populated when you run `alembic init database/migrations`.

---

## 🎓 Learning Resources

### Official Docs:
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto-generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

### Video Tutorials:
- [Alembic Crash Course](https://www.youtube.com/watch?v=SdcH6IEi6nE)

---

## ✅ Checklist for Future Migration Setup

### Pre-Setup:
- [ ] Backup current database
- [ ] Document current schema
- [ ] Test on development copy

### Setup:
- [ ] Install Alembic
- [ ] Run `alembic init database/migrations`
- [ ] Configure `env.py` with Base import
- [ ] Update `alembic.ini` with database URL

### Baseline:
- [ ] Generate initial migration: `alembic revision --autogenerate -m "Initial"`
- [ ] Review generated migration
- [ ] Test upgrade/downgrade
- [ ] Commit to Git

### Production:
- [ ] Backup production database
- [ ] Apply baseline: `alembic upgrade head`
- [ ] Verify tables created
- [ ] Document rollback procedure

---

**Current Status**: ⏳ **Migrations Not Yet Implemented**  
**Recommendation**: ✅ **Implement before production deployment**  
**Priority**: 🔴 **High** (Required for production safety)

---

**Documentation Version**: 1.0  
**Last Updated**: 2025-11-11  
**Next Review**: Before production deployment
