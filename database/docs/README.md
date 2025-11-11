# 📚 Database Documentation

**Project**: Migochat  
**Database**: SQLite with SQLAlchemy ORM  
**Last Updated**: 2025-11-11

---

## 📋 Overview

This directory contains comprehensive documentation for the Migochat database system.

### Documentation Files:

| File | Description | Status |
|------|-------------|--------|
| [SCHEMA.md](SCHEMA.md) | Database schema & ERD | ✅ Complete |
| [MODELS.md](MODELS.md) | SQLAlchemy models guide | ✅ Complete |
| [MIGRATIONS.md](MIGRATIONS.md) | Migration strategy (Alembic) | ✅ Complete |
| [BACKUP_RESTORE.md](BACKUP_RESTORE.md) | Backup & restore guide | ✅ Complete |

---

## 🎯 Quick Links

### For Developers:
- 📊 [Database Schema](SCHEMA.md#-tables-schema) - Full table definitions
- 📦 [Model Usage](MODELS.md#-best-practices) - How to use ORM models
- 🔗 [Relationships](MODELS.md#-relationship-patterns) - Model relationships

### For DevOps:
- 💾 [Backup Guide](BACKUP_RESTORE.md#-quick-backup-manual) - How to backup database
- 🔄 [Restore Guide](BACKUP_RESTORE.md#-restore-database) - How to restore from backup
- 🔧 [Migration Setup](MIGRATIONS.md#-setup-alembic-when-needed) - When to add migrations

### For Database Admins:
- 🏗️ [ERD Diagram](SCHEMA.md#-entity-relationship-diagram) - Visual schema
- 📈 [Performance Tips](SCHEMA.md#-performance-optimizations) - Query optimization
- 🔒 [Data Integrity](SCHEMA.md#-data-integrity) - Constraints & validation

---

## 🗄️ Database Quick Facts

**Type**: SQLite  
**ORM**: SQLAlchemy 2.0  
**Tables**: 7  
**Location**: `database/bww_assistant.db`  
**Backups**: `database/backups/`

### Current Statistics:
- **Users**: ~0-10,000 (production ready)
- **Messages**: ~0-500,000 (indexed)
- **Size**: ~60 MB (for 10K users)
- **Performance**: < 50ms query time (indexed)

---

## 🚀 Quick Start

### 1. View Schema
```bash
# See all tables
sqlite3 database/bww_assistant.db ".tables"

# Describe users table
sqlite3 database/bww_assistant.db ".schema users"
```

### 2. Backup Database
```bash
python database/scripts/backup.py
```

### 3. Check Health
```bash
python database/scripts/health.py
```

### 4. Rebuild (Development Only)
```bash
python database/scripts/rebuild.py
```

---

## 📖 Documentation Map

### Level 1: Schema Understanding
1. Start with [SCHEMA.md](SCHEMA.md)
2. Understand tables and relationships
3. Review enumerations

### Level 2: Development
1. Read [MODELS.md](MODELS.md)
2. Learn ORM patterns
3. Practice queries

### Level 3: Production
1. Study [BACKUP_RESTORE.md](BACKUP_RESTORE.md)
2. Setup automated backups
3. Test disaster recovery

### Level 4: Advanced
1. Read [MIGRATIONS.md](MIGRATIONS.md)
2. Setup Alembic (when needed)
3. Version control schema changes

---

## 🎓 Learning Path

### Beginner (Week 1):
- [ ] Read SCHEMA.md overview
- [ ] Understand User and Message models
- [ ] Run simple queries

### Intermediate (Week 2-3):
- [ ] Read MODELS.md completely
- [ ] Practice with relationships
- [ ] Write complex queries

### Advanced (Week 4+):
- [ ] Setup Alembic migrations
- [ ] Implement backup automation
- [ ] Optimize query performance

---

## 🔧 Tools & Scripts

### Available Scripts:

| Script | Command | Description |
|--------|---------|-------------|
| Backup | `python database/scripts/backup.py` | Create database backup |
| Health Check | `python database/scripts/health.py` | Verify database health |
| Rebuild | `python database/scripts/rebuild.py` | Rebuild database (dev) |
| CLI | `python database/cli.py [command]` | Unified CLI tool |

### CLI Commands:
```bash
# Backup database
python database/cli.py backup

# Check health
python database/cli.py health

# Rebuild (CAUTION: Deletes all data!)
python database/cli.py rebuild
```

---

## 📊 Database Models Overview

### Core Models:

1. **User** - Customer/Lead tracking
   - PSID-based identification
   - Multi-platform support
   - Lead lifecycle management

2. **Message** - Message storage
   - All platforms (Facebook, WhatsApp)
   - Source attribution (ads, posts)
   - Bi-directional tracking

3. **Conversation** - Thread tracking
   - Active conversations
   - Message counts
   - Activity timestamps

### Supporting Models:

4. **LeadActivity** - Audit trail
5. **Post** - Facebook posts
6. **AdCampaign** - Ad tracking
7. **AppSettings** - Dynamic config

**See [MODELS.md](MODELS.md) for detailed documentation.**

---

## 🔗 Related Documentation

### Project Documentation:
- [Main README](../../README.md) - Project overview
- [API Documentation](../../Server/README.md) - API endpoints
- [Deployment Guide](../../deployment/README.md) - Production setup

### Code Files:
- [models.py](../models.py) - Model definitions
- [enums.py](../enums.py) - Enumeration types
- [engine.py](../engine.py) - Database engine
- [context.py](../context.py) - Session management

---

## 🎯 Common Tasks

### View Database Schema:
```bash
sqlite3 database/bww_assistant.db << EOF
.tables
.schema users
.schema messages
EOF
```

### Export Data:
```bash
# Export users to CSV
sqlite3 -header -csv database/bww_assistant.db \
  "SELECT * FROM users;" > users.csv

# Export messages to JSON (using Python)
python -c "
import sqlite3, json
conn = sqlite3.connect('database/bww_assistant.db')
cursor = conn.execute('SELECT * FROM messages LIMIT 100')
rows = [dict(zip([col[0] for col in cursor.description], row)) 
        for row in cursor.fetchall()]
print(json.dumps(rows, indent=2, default=str))
" > messages.json
```

### Check Database Size:
```bash
# Windows
Get-Item database\bww_assistant.db | Select-Object Name, Length

# Linux/Mac
ls -lh database/bww_assistant.db
```

---

## 🔒 Security Notes

### Sensitive Data:
- ✅ API keys stored in `app_settings` with `is_sensitive=True`
- ✅ No passwords stored (OAuth-based auth)
- ✅ Backups should be encrypted in production

### Access Control:
- ⚠️ SQLite has no built-in access control
- ⚠️ Secure file system permissions required
- ⚠️ Production: Consider PostgreSQL for ACLs

---

## 📝 Maintenance Schedule

### Daily:
- ✅ Automated backup (2 AM)
- ✅ Health check logs

### Weekly:
- ✅ Backup verification
- ✅ Storage space check

### Monthly:
- ✅ Full disaster recovery test
- ✅ Documentation review
- ✅ Schema optimization review

---

## 🆘 Getting Help

### Issues & Questions:

1. **Database Errors**:
   - Check: [BACKUP_RESTORE.md#disaster-recovery-plan](BACKUP_RESTORE.md#-disaster-recovery-plan)
   - Run: `python database/scripts/health.py`

2. **Performance Issues**:
   - Check: [SCHEMA.md#performance-optimizations](SCHEMA.md#-performance-optimizations)
   - Review: Query patterns

3. **Migration Questions**:
   - Read: [MIGRATIONS.md](MIGRATIONS.md)
   - Plan: Before production deployment

---

## 🎉 Contributing

When updating database:

1. Update models in `database/models.py`
2. Update documentation in `database/docs/`
3. Test changes on development copy
4. Create migration (when Alembic is setup)
5. Update this README if needed

---

**Documentation Maintained By**: Development Team  
**Last Updated**: 2025-11-12  
**Version**: 1.1  
**Status**: ✅ Complete & Up-to-date
