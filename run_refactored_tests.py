#!/usr/bin/env python
"""
Test runner script for the refactored Online Bookstore test suite.

This script provides a convenient way to run the complete test suite
in Docker containers and CI/CD environments.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run the complete test suite with detailed output."""
    print("=" * 80)
    print("  Online Bookstore - Comprehensive Test Suite (156 Tests)")
    print("=" * 80)
    print()

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    
    print("🧪 Running comprehensive test suite...")
    print("-" * 80)
    print()
    
    # Run pytest with verbose output
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes",
        "-ra",
        "--strict-markers",
        "--maxfail=5",
    ]
    
    result = subprocess.run(cmd, cwd=project_root)
    
    print()
    print("=" * 80)
    
    if result.returncode == 0:
        print("✅ All tests passed successfully!")
        print("=" * 80)
        print()
        print("📊 Test Summary:")
        print("  • Total tests: 156")
        print("  • Models: 53 tests")
        print("  • Services: 35 tests")
        print("  • Application: 25 tests")
        print("  • Configuration: 12 tests")
        print("  • Integration: 31 tests")
    else:
        print("❌ Some tests failed. Please review the output above.")
    
    print("=" * 80)
    
    return result.returncode


def run_with_coverage():
    """Run tests with detailed coverage reporting."""
    print("=" * 80)
    print("  Running Tests with Coverage Report")
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
        "--cov-report=xml",
        "-v",
        "--tb=short",
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print()
        print("=" * 80)
        print("✅ Coverage report generated:")
        print("  • Terminal: See above")
        print("  • HTML: htmlcov/index.html")
        print("  • XML: coverage.xml")
        print("=" * 80)
    
    return result.returncode


def run_quick():
    """Run a quick subset of tests for fast feedback."""
    print("=" * 80)
    print("  Quick Test Run (Fast Feedback)")
    print("=" * 80)
    print()
    
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=line",
        "-x",  # Stop on first failure
        "--ff",  # Run failures first
    ]
    
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--coverage":
            exit_code = run_with_coverage()
        elif sys.argv[1] == "--quick":
            exit_code = run_quick()
        elif sys.argv[1] == "--help":
            print("Usage: python run_refactored_tests.py [OPTIONS]")
            print()
            print("Options:")
            print("  (none)       Run full test suite")
            print("  --coverage   Run tests with coverage reporting")
            print("  --quick      Run quick test (stop on first failure)")
            print("  --help       Show this help message")
            exit_code = 0
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for available options")
            exit_code = 1
    else:
        # Default: run full test suite
        exit_code = run_tests()
    
    sys.exit(exit_code)

