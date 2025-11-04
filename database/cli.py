#!/usr/bin/env python3
"""
BWW Assistant - Database Management CLI
Professional database management utility
"""
import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.scripts.rebuild import rebuild_database_cli
from database.scripts.backup import backup_database_cli
from database.scripts.health import health_check_cli

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def show_banner():
    """Display application banner"""
    print("=" * 60)
    print("🗄️  BWW ASSISTANT - DATABASE MANAGEMENT")
    print("   Professional Database CLI Utility")
    print("=" * 60)
    print()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="BWW Assistant Database Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s rebuild          Rebuild database from scratch
  %(prog)s backup           Create database backup
  %(prog)s health           Check database health
  %(prog)s stats            Show database statistics
        """
    )

    parser.add_argument(
        "command",
        choices=["rebuild", "backup", "health", "stats"],
        help="Command to execute"
    )

    parser.add_argument(
        "--backup-dir",
        type=str,
        help="Backup directory path (for backup command)"
    )

    args = parser.parse_args()

    # Show banner
    show_banner()

    # Execute command
    success = False

    if args.command == "rebuild":
        success = rebuild_database_cli()

    elif args.command == "backup":
        success = backup_database_cli(args.backup_dir)

    elif args.command == "health":
        success = health_check_cli()

    elif args.command == "stats":
        success = health_check_cli()  # Stats are included in health check

    # Exit with appropriate code
    print()
    if success:
        logger.info("✅ Operation completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Operation failed")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)
