#!/usr/bin/env python3
"""
Bww-AI-Assistant - Log Management Utility
أداة إدارة ملفات السجلات
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.environ['PYTHONPATH'] = str(project_root)

# Import centralized logging configuration
from config.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def clean_old_logs(days_to_keep=7):
    """Clean up old log files older than specified days"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logger.info("📁 Logs directory doesn't exist, nothing to clean")
        return

    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    cleaned_count = 0

    logger.info(f"🧹 Cleaning log files older than {days_to_keep} days...")

    for log_file in logs_dir.glob("*.log"):
        try:
            # Get file modification time
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)

            if file_time < cutoff_date:
                logger.info(f"🗑️ Removing old log file: {log_file.name}")
                log_file.unlink()
                cleaned_count += 1
        except Exception as e:
            logger.error(f"❌ Error processing {log_file.name}: {e}")

    logger.info(f"✅ Cleaned {cleaned_count} old log files")

def show_log_status():
    """Show current log files status"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logger.info("📁 Logs directory doesn't exist")
        return

    logger.info("📋 Current Log Files Status:")
    logger.info("=" * 50)

    log_files = list(logs_dir.glob("*.log"))
    if not log_files:
        logger.info("📭 No log files found")
        return

    total_size = 0
    for log_file in sorted(log_files):
        try:
            size = log_file.stat().st_size
            total_size += size
            size_mb = size / (1024 * 1024)
            modified = datetime.fromtimestamp(log_file.stat().st_mtime)

            logger.info(f"📄 {log_file.name}")
            logger.info(f"   Size: {size_mb:.2f} MB")
            logger.info(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Error reading {log_file.name}: {e}")

    total_mb = total_size / (1024 * 1024)
    logger.info(f"📊 Total logs size: {total_mb:.2f} MB")

def create_log_summary():
    """Create a summary of recent log activity"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logger.info("📁 Logs directory doesn't exist")
        return

    logger.info("📊 Recent Log Activity Summary:")
    logger.info("=" * 50)

    # Count log entries by type
    log_types = {}
    total_entries = 0

    for log_file in logs_dir.glob("*.log"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                log_types[log_file.stem] = len(lines)
                total_entries += len(lines)
        except Exception as e:
            logger.error(f"❌ Error reading {log_file.name}: {e}")

    for log_type, count in sorted(log_types.items()):
        logger.info(f"📄 {log_type}: {count:,} entries")

    logger.info(f"📊 Total entries: {total_entries:,}")

def main():
    """Main function"""
    logger.info("🎯 Bww-AI-Assistant Log Management Utility")
    logger.info("=" * 60)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "clean":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            clean_old_logs(days)
        elif command == "status":
            show_log_status()
        elif command == "summary":
            create_log_summary()
        else:
            logger.error(f"❌ Unknown command: {command}")
            logger.info("Available commands: clean, status, summary")
    else:
        # Default: show status and summary
        show_log_status()
        logger.info("")
        create_log_summary()
        logger.info("")
        logger.info("💡 Usage:")
        logger.info("  python scripts/log_manager.py status    # Show log files status")
        logger.info("  python scripts/log_manager.py summary   # Show log activity summary")
        logger.info("  python scripts/log_manager.py clean 7  # Clean logs older than 7 days")

if __name__ == "__main__":
    main()
