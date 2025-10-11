#!/usr/bin/env python
"""Test runner script for the Online Bookstore test suite.

This script provides a convenient way to run the complete test suite
and generate detailed reports.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run the complete test suite with coverage reporting."""
    print("=" * 80)
    print("Online Bookstore - Comprehensive Test Suite (111 Tests)")
    print("=" * 80)
    print()

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    
    # Install test requirements if needed
    print("📦 Checking test dependencies...")
    try:
        import pytest
        import pytest_cov
    except ImportError:
        print("⚠️  Installing test dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"],
            check=False
        )

    print("\n🧪 Running test suite...")
    print("-" * 80)
    
    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes",
        "-ra",
    ]
    
    result = subprocess.run(cmd, cwd=project_root)
    
    print()
    print("=" * 80)
    
    if result.returncode == 0:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. Please review the output above.")
    
    print("=" * 80)
    
    return result.returncode


def run_with_coverage():
    """Run tests with detailed coverage reporting."""
    print("=" * 80)
    print("Running Tests with Coverage Report")
    print("=" * 80)
    print()
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v",
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Coverage report generated in htmlcov/index.html")
    
    return result.returncode


def count_tests():
    """Count the total number of tests in the suite."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--collect-only",
        "-q",
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        lines = result.stdout.strip().split("\n")
        last_line = lines[-1] if lines else ""
        print(f"\n📊 Test Count: {last_line}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--coverage":
        exit_code = run_with_coverage()
    elif len(sys.argv) > 1 and sys.argv[1] == "--count":
        count_tests()
        exit_code = 0
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)

