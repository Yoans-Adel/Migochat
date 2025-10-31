"""
Run All Tests Script
Quick script to run comprehensive test suite
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n{'='*70}")
    print(f"🧪 {description}")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    """Run all test suites"""
    project_root = Path(__file__).parent.parent
    
    print("\n" + "="*70)
    print("🚀 BWW Assistant - Comprehensive Test Suite")
    print("="*70)
    
    all_passed = True
    
    # 1. Critical Tests
    if not run_command(
        "pytest -m critical -v",
        "Running Critical Tests (Must Pass)"
    ):
        all_passed = False
        print("❌ CRITICAL TESTS FAILED!")
        return 1
    
    # 2. Configuration Tests
    if not run_command(
        "pytest tests/test_config.py -v",
        "Running Configuration Tests"
    ):
        all_passed = False
    
    # 3. Database Tests
    if not run_command(
        "pytest tests/test_database.py -v",
        "Running Database Tests"
    ):
        all_passed = False
    
    # 4. Server Tests
    if not run_command(
        "pytest tests/test_server.py -v",
        "Running Server Tests"
    ):
        all_passed = False
    
    # 5. Unit Tests
    if not run_command(
        "pytest tests/unit/ -v",
        "Running Unit Tests (Services)"
    ):
        all_passed = False
    
    # 6. Coverage Report
    print(f"\n{'='*70}")
    print("📊 Generating Coverage Report")
    print(f"{'='*70}")
    
    subprocess.run(
        "pytest --cov=Server --cov=app --cov=database --cov-report=term-missing --cov-report=html",
        shell=True
    )
    
    # Summary
    print(f"\n{'='*70}")
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n📊 Coverage report generated in: htmlcov/index.html")
        print("\n🎉 Project is ready for production!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("="*70)
        print("\n⚠️  Please fix failing tests before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
