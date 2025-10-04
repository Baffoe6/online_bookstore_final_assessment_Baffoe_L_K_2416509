#!/usr/bin/env python3
"""Script to run tests for the refactored Online Bookstore application."""

import sys
import os
import subprocess

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all tests for the refactored application."""
    print("🧪 Running Refactored Online Bookstore Tests")
    print("=" * 50)
    
    test_files = [
        "tests/test_refactored_models.py",
        "tests/test_refactored_services.py"
    ]
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠️  Test file not found: {test_file}")
            continue
            
        print(f"\n📋 Running {test_file}...")
        print("-" * 30)
        
        try:
            # Run pytest for the specific test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short"
            ], capture_output=True, text=True)
            
            # Parse output for test counts
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "passed" in line and "failed" in line:
                    # Extract test counts
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            passed = int(parts[i-1])
                            total_passed += passed
                        elif part == "failed":
                            failed = int(parts[i-1])
                            total_failed += failed
            
            if result.returncode == 0:
                print(f"✅ {test_file} - All tests passed")
            else:
                print(f"❌ {test_file} - Some tests failed")
                print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                    
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            total_failed += 1
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Total: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed! The refactored code is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Please check the output above.")
        return False

def run_coverage():
    """Run tests with coverage report."""
    print("\n📊 Running Coverage Analysis...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/test_refactored_models.py",
            "tests/test_refactored_services.py",
            "--cov=models_refactored",
            "--cov=services",
            "--cov-report=term-missing",
            "--cov-report=html"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        print("\n📁 HTML coverage report generated in htmlcov/")
        
    except Exception as e:
        print(f"❌ Error running coverage: {e}")

if __name__ == "__main__":
    print("🔧 Refactored Online Bookstore - Test Runner")
    print("=" * 50)
    
    # Check if pytest is available
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest is not installed. Please install it with:")
        print("   pip install pytest pytest-cov")
        sys.exit(1)
    
    # Run tests
    success = run_tests()
    
    # Run coverage if tests passed
    if success:
        run_coverage()
    
    print("\n🏁 Test run completed!")
    
    if not success:
        sys.exit(1)
