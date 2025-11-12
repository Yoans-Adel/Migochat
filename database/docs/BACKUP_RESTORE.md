# 💾 Database Backup & Restore Guide

**Project**: Migochat  
**Database**: SQLite  
**Backup Strategy**: File-based + SQL dumps  
**Last Updated**: 2025-11-11

---

## 📋 Overview

Migochat uses SQLite database which requires specific backup strategies different from client-server databases.

### Backup Methods:
1. ✅ **File Copy** - Simple and fast
2. ✅ **SQL Dump** - Human-readable and portable
3. ✅ **Online Backup** - SQLite `.backup` command
4. ⚠️ **Automated Backups** - Scheduled via scripts

---

## 🎯 Quick Backup (Manual)

### Method 1: File Copy (Simplest)

```bash
# Windows (PowerShell)
Copy-Item "database\bww_assistant.db" "database\backups\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"

# Linux/Mac
cp database/bww_assistant.db "database/backups/backup_$(date +%Y%m%d_%H%M%S).db"
```

**Advantages**:
- ✅ Fastest method
- ✅ Exact database copy
- ✅ Easy to restore

**Disadvantages**:
- ⚠️ Requires database to be idle
- ⚠️ Not human-readable

---

### Method 2: SQL Dump (Recommended)

```bash
# Using SQLite CLI
sqlite3 database/bww_assistant.db .dump > database/backups/backup_20251111.sql

# Compressed backup
sqlite3 database/bww_assistant.db .dump | gzip > database/backups/backup_20251111.sql.gz
```

**Advantages**:
- ✅ Human-readable SQL
- ✅ Can edit before restore
- ✅ Version-controllable (if needed)
- ✅ Portable across SQLite versions

**Disadvantages**:
- ⚠️ Slower than file copy
- ⚠️ Larger file size (unless compressed)

---

### Method 3: Online Backup (SQLite Command)

```python
# Python script (recommended)
import sqlite3
from datetime import datetime

def backup_database():
    source = sqlite3.connect('database/bww_assistant.db')
    backup_file = f'database/backups/backup_{datetime.now():%Y%m%d_%H%M%S}.db'
    backup = sqlite3.connect(backup_file)
    
    # Online backup (safe while database is in use)
    source.backup(backup)
    
    backup.close()
    source.close()
    print(f"✅ Backup created: {backup_file}")

if __name__ == "__main__":
    backup_database()
```

**Advantages**:
- ✅ **Safe while database is in use**
- ✅ Transactionally consistent
- ✅ Fast
- ✅ Exact copy

---

## 🔧 Using Built-in Backup Script

### Run Backup Script

```bash
# Using Python directly
python database/scripts/backup.py

# Or via CLI
python database/cli.py backup

# With custom backup directory
python database/cli.py backup --backup-dir "E:\Backups\Migochat"
```

### Backup Script Code

See: `database/scripts/backup.py`

```python
#!/usr/bin/env python3
"""Database backup utility"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def backup_database_cli(backup_dir: str = None) -> bool:
    """
    Create database backup
    
    Args:
        backup_dir: Optional backup directory path
        
    Returns:
        True if backup successful
    """
    try:
        # Default backup directory
        if not backup_dir:
            backup_dir = Path(__file__).parent.parent / "backups"
        else:
            backup_dir = Path(backup_dir)
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Database file
        db_file = Path(__file__).parent.parent / "bww_assistant.db"
        
        if not db_file.exists():
            logger.error(f"Database file not found: {db_file}")
            return False
        
        # Backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.db"
        
        # Method 1: Simple file copy
        logger.info("Creating backup via file copy...")
        shutil.copy2(db_file, backup_file)
        
        # Method 2: SQL dump (additional)
        sql_backup = backup_dir / f"backup_{timestamp}.sql"
        logger.info("Creating SQL dump...")
        
        with sqlite3.connect(db_file) as conn:
            with open(sql_backup, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
        
        logger.info(f"✅ Database backup successful!")
        logger.info(f"   - Binary backup: {backup_file}")
        logger.info(f"   - SQL dump: {sql_backup}")
        logger.info(f"   - Backup size: {backup_file.stat().st_size / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False
```

---

## 🔄 Restore Database

### Method 1: From File Backup

```bash
# 1. Stop application first!

# 2. Backup current database (just in case)
Copy-Item "database\bww_assistant.db" "database\bww_assistant.db.backup"

# 3. Restore from backup
Copy-Item "database\backups\backup_20251111_120000.db" "database\bww_assistant.db" -Force

# 4. Restart application
```

### Method 2: From SQL Dump

```bash
# 1. Create new database from dump
sqlite3 database/bww_assistant_new.db < database/backups/backup_20251111.sql

# 2. Verify restore
sqlite3 database/bww_assistant_new.db "SELECT COUNT(*) FROM users;"

# 3. Replace current database
Move-Item database\bww_assistant.db database\bww_assistant.db.old -Force
Move-Item database\bww_assistant_new.db database\bww_assistant.db -Force
```

### Method 3: Python Restore Script

```python
# database/scripts/restore.py
import sqlite3
import shutil
from pathlib import Path

def restore_database(backup_file: str):
    """Restore database from backup"""
    db_file = Path("database/bww_assistant.db")
    backup = Path(backup_file)
    
    if not backup.exists():
        print(f"❌ Backup file not found: {backup}")
        return False
    
    # Backup current database
    if db_file.exists():
        current_backup = db_file.parent / f"{db_file.stem}_before_restore.db"
        shutil.copy2(db_file, current_backup)
        print(f"✅ Current database backed up to: {current_backup}")
    
    # Restore
    shutil.copy2(backup, db_file)
    print(f"✅ Database restored from: {backup}")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python restore.py <backup_file>")
        sys.exit(1)
    
    restore_database(sys.argv[1])
```

**Usage**:
```bash
python database/scripts/restore.py database/backups/backup_20251111_120000.db
```

---

## 📊 Automated Backup Strategy

### Backup Schedule (Recommended)

| Frequency | Retention | Method |
|-----------|-----------|--------|
| **Hourly** | 24 hours | File copy (last 24) |
| **Daily** | 7 days | SQL dump |
| **Weekly** | 4 weeks | Compressed SQL |
| **Monthly** | 12 months | Full backup |

### Windows Task Scheduler

```powershell
# Create scheduled task for daily backup
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "F:\working - yoans\Migochat\database\scripts\backup.py"

$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Migochat Database Backup" -Description "Daily database backup"
```

### Linux Cron Job

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/Migochat && python database/scripts/backup.py

# Weekly backup at Sunday 3 AM
0 3 * * 0 cd /path/to/Migochat && python database/scripts/backup.py --weekly
```

### Backup Script with Rotation

```python
# database/scripts/backup_rotated.py
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def rotate_backups(backup_dir: Path, keep_days: int = 7):
    """Delete backups older than keep_days"""
    cutoff = datetime.now() - timedelta(days=keep_days)
    
    for backup in backup_dir.glob("backup_*.db"):
        # Extract timestamp from filename
        try:
            timestamp_str = backup.stem.replace("backup_", "")
            backup_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            
            if backup_time < cutoff:
                backup.unlink()
                print(f"🗑️ Deleted old backup: {backup.name}")
        except:
            continue

def backup_with_rotation():
    """Backup database and rotate old backups"""
    # Create backup
    backup_database_cli()
    
    # Rotate old backups (keep 7 days)
    backup_dir = Path("database/backups")
    rotate_backups(backup_dir, keep_days=7)
```

---

## 🔒 Backup Best Practices

### 1. **3-2-1 Rule**
- ✅ **3** copies of data (original + 2 backups)
- ✅ **2** different media types (local + cloud)
- ✅ **1** offsite backup (cloud storage)

### 2. **Verify Backups**

```bash
# Test restore on separate database
sqlite3 test_restore.db < database/backups/backup_latest.sql

# Verify tables
sqlite3 test_restore.db "SELECT name FROM sqlite_master WHERE type='table';"

# Verify row counts
sqlite3 test_restore.db "SELECT COUNT(*) FROM users;"
```

### 3. **Encrypt Sensitive Backups**

```bash
# Encrypt backup with GPG
gpg --symmetric --cipher-algo AES256 backup_20251111.db

# Creates: backup_20251111.db.gpg

# Decrypt when needed
gpg --decrypt backup_20251111.db.gpg > backup_restored.db
```

### 4. **Cloud Backup**

```python
# Upload to cloud (example with rclone)
import subprocess

def upload_to_cloud(backup_file: str):
    """Upload backup to cloud storage"""
    subprocess.run([
        "rclone", "copy", 
        backup_file, 
        "gdrive:Migochat/Backups/"
    ])
```

---

## 📁 Backup Directory Structure

```
database/
  backups/
    backup_20251111_020000.db      ← Daily backup (file)
    backup_20251111_020000.sql     ← Daily backup (SQL)
    backup_20251110_020000.db      ← Previous day
    backup_20251109_020000.db      ← 2 days ago
    ...
    weekly/
      backup_20251105_020000.db    ← Weekly backup
      backup_20251029_020000.db
    monthly/
      backup_20251101_020000.db    ← Monthly backup
```

---

## ⚠️ Important Notes

### SQLite Specific Considerations:

1. **No concurrent writes**: SQLite locks entire database during writes
2. **Backup while running**: Use `.backup` command or Python `backup()` method
3. **WAL mode**: If using WAL mode, backup both `.db` and `.db-wal` files
4. **Corruption**: Regular `PRAGMA integrity_check;` recommended

### Check Database Integrity:

```bash
sqlite3 database/bww_assistant.db "PRAGMA integrity_check;"
# Output should be: ok
```

---

## 🚨 Disaster Recovery Plan

### If Database Corrupted:

1. **Stop application immediately**
2. **Copy corrupted database** (for forensics)
3. **Find latest good backup**
4. **Restore from backup**
5. **Verify data integrity**
6. **Resume operations**

### Recovery Script:

```bash
# 1. Stop app
# Railway: pause deployment

# 2. Backup corrupted DB
Copy-Item database\bww_assistant.db database\corrupted_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# 3. Restore from backup
Copy-Item database\backups\backup_20251111_020000.db database\bww_assistant.db -Force

# 4. Verify
python database/scripts/health.py

# 5. Restart app
# Railway: resume deployment
```

---

## ✅ Backup Checklist

### Daily:
- [ ] Automated backup runs successfully
- [ ] Backup file created in `database/backups/`
- [ ] Backup size is reasonable (not 0 bytes)
- [ ] Old backups rotated (keep last 7 days)

### Weekly:
- [ ] Manual backup verification
- [ ] Test restore on development copy
- [ ] Upload weekly backup to cloud
- [ ] Check backup storage space

### Monthly:
- [ ] Full disaster recovery test
- [ ] Review backup strategy
- [ ] Update documentation
- [ ] Verify offsite backups accessible

---

**Current Backup Location**: `F:\working - yoans\Migochat\database\backups\`  
**Backup Script**: `database/scripts/backup.py`  
**Recommended Frequency**: Daily at 2 AM  
**Retention**: 7 days (local), 30 days (weekly), 12 months (monthly)

---

**Documentation Version**: 1.0  
**Last Updated**: 2025-11-11  
**Next Review**: Monthly
