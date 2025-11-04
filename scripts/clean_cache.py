#!/usr/bin/env python3
"""
Cache Cleanup Script for Bww-AI-Assistant
Cleans all cache files and __pycache__ directories
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def get_project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent

def find_pycache_directories(root_dir):
    """Find all __pycache__ directories (exclude venv)"""
    pycache_dirs = []
    for root, dirs, files in os.walk(root_dir):
        # Skip venv directories
        if 'venv' in root or '.venv' in root or 'Lib' in root:
            continue
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))
    return pycache_dirs

def find_cache_files(root_dir):
    """Find all .pyc, .pyo, and .pyd files (exclude venv)"""
    cache_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip venv directories
        if 'venv' in root or '.venv' in root or 'Lib' in root:
            continue
        for file in files:
            if file.endswith(('.pyc', '.pyo', '.pyd')):
                cache_files.append(os.path.join(root, file))
    return cache_files

def find_temp_files(root_dir):
    """Find temporary files in temp/ directory"""
    temp_dir = root_dir / "temp"
    if not temp_dir.exists():
        return []

    temp_files = []
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            temp_files.append(os.path.join(root, file))
    return temp_files

def clean_pycache():
    """Clean all __pycache__ directories"""
    project_root = get_project_root()
    pycache_dirs = find_pycache_directories(project_root)

    if not pycache_dirs:
        print("✅ No __pycache__ directories found")
        return 0

    cleaned_count = 0
    print(f"\n🗑️  Found {len(pycache_dirs)} __pycache__ directories to clean")

    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print(f"  ✅ Removed: {pycache_dir}")
            cleaned_count += 1
        except Exception as e:
            print(f"  ❌ Error removing {pycache_dir}: {e}")

    return cleaned_count

def clean_cache_files():
    """Clean all .pyc, .pyo, .pyd files"""
    project_root = get_project_root()
    cache_files = find_cache_files(project_root)

    if not cache_files:
        print("✅ No cache files found")
        return 0

    cleaned_count = 0
    print(f"\n🗑️  Found {len(cache_files)} cache files to clean")

    for cache_file in cache_files:
        try:
            os.remove(cache_file)
            print(f"  ✅ Removed: {cache_file}")
            cleaned_count += 1
        except Exception as e:
            print(f"  ❌ Error removing {cache_file}: {e}")

    return cleaned_count

def clean_temp_files():
    """Clean temporary files in temp/ directory"""
    project_root = get_project_root()
    temp_dir = project_root / "temp"

    if not temp_dir.exists():
        print("✅ No temp/ directory found")
        return 0

    temp_files = find_temp_files(project_root)

    if not temp_files:
        print("✅ No temporary files to clean")
        return 0

    cleaned_count = 0
    print(f"\n🗑️  Found {len(temp_files)} temporary files to clean")

    for temp_file in temp_files:
        try:
            os.remove(temp_file)
            print(f"  ✅ Removed: {temp_file}")
            cleaned_count += 1
        except Exception as e:
            print(f"  ❌ Error removing {temp_file}: {e}")

    return cleaned_count

def clean_pytest_cache():
    """Clean pytest cache directory"""
    project_root = get_project_root()
    pytest_cache = project_root / ".pytest_cache"

    if not pytest_cache.exists():
        print("✅ No .pytest_cache directory found")
        return 0

    try:
        shutil.rmtree(pytest_cache)
        print("\n🗑️  Removed .pytest_cache directory")
        return 1
    except Exception as e:
        print(f"\n❌ Error removing .pytest_cache: {e}")
        return 0

def clean_coverage_files():
    """Clean coverage reports and data files"""
    project_root = get_project_root()
    cleaned_count = 0

    # Clean htmlcov directory
    htmlcov_dir = project_root / "htmlcov"
    if htmlcov_dir.exists():
        try:
            shutil.rmtree(htmlcov_dir)
            print("\n🗑️  Removed htmlcov/ directory")
            cleaned_count += 1
        except Exception as e:
            print(f"\n❌ Error removing htmlcov/: {e}")

    # Clean .coverage file
    coverage_file = project_root / ".coverage"
    if coverage_file.exists():
        try:
            os.remove(coverage_file)
            print("🗑️  Removed .coverage file")
            cleaned_count += 1
        except Exception as e:
            print(f"❌ Error removing .coverage: {e}")

    if cleaned_count == 0:
        print("✅ No coverage files found")

    return cleaned_count

def clean_empty_dirs():
    """Clean empty directories in temp/"""
    project_root = get_project_root()
    temp_dir = project_root / "temp"

    if not temp_dir.exists():
        return 0

    cleaned_count = 0
    # Walk bottom-up to remove nested empty directories
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                # Check if directory is empty
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"🗑️  Removed empty directory: {dir_path}")
                    cleaned_count += 1
            except Exception as e:
                print(f"❌ Error removing {dir_path}: {e}")

    if cleaned_count == 0:
        print("✅ No empty directories found")

    return cleaned_count

def clean_all(keep_temp=True):
    """Clean all cache files"""
    print("=" * 60)
    print("🧹 Cache Cleanup Script - Bww-AI-Assistant")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    total_cleaned = 0

    # Clean __pycache__ directories
    pycache_count = clean_pycache()
    total_cleaned += pycache_count

    # Clean .pyc, .pyo, .pyd files
    cache_count = clean_cache_files()
    total_cleaned += cache_count

    # Clean pytest cache
    pytest_count = clean_pytest_cache()
    total_cleaned += pytest_count

    # Clean coverage files
    coverage_count = clean_coverage_files()
    total_cleaned += coverage_count

    # Clean empty directories
    empty_dirs_count = clean_empty_dirs()
    total_cleaned += empty_dirs_count

    # Clean temp files (optional)
    if not keep_temp:
        temp_count = clean_temp_files()
        total_cleaned += temp_count
    else:
        print("\n📁 Skipping temp/ files (use --all to clean them)")

    print("\n" + "=" * 60)
    print(f"✅ Cleanup complete! Removed {total_cleaned} items")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    # Check for --all flag to clean temp files too
    keep_temp = "--all" not in sys.argv

    try:
        clean_all(keep_temp=keep_temp)
    except KeyboardInterrupt:
        print("\n\n❌ Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during cleanup: {e}")
        sys.exit(1)

