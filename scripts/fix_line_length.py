#!/usr/bin/env python3
"""Fix long lines automatically using autopep8"""

import subprocess
import sys
from pathlib import Path


def fix_line_length(file_path: str) -> bool:
    """Fix line length issues in a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Use autopep8 to fix line length issues
        subprocess.run(
            [
                sys.executable, "-m", "autopep8",
                "--in-place",
                "--max-line-length", "79",
                "--select", "E501",
                file_path
            ],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Fixed: {file_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error fixing {file_path}: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function"""
    files_to_fix = [
        "Server/routes/api.py",
        "Server/main.py"
    ]

    project_root = Path(__file__).parent.parent

    print("🔧 Fixing line length issues...")
    print("=" * 60)

    success_count = 0
    for file_path in files_to_fix:
        full_path = project_root / file_path
        if full_path.exists():
            if fix_line_length(str(full_path)):
                success_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")

    print("=" * 60)
    print(f"✅ Successfully fixed {success_count}/{len(files_to_fix)} files")


if __name__ == "__main__":
    main()
