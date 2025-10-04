"""
Test runner script to execute all test suites with coverage reporting
"""
import subprocess
import sys
import os

def run_tests():
    """Run all test suites and generate coverage report"""
    print("="*60)
    print("ONLINE BOOKSTORE - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Install required packages if not available
    try:
        import coverage
        import pytest
    except ImportError:
        print("Installing required testing packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'coverage', 'pytest'])
        import coverage
        import pytest
    
    # Run tests with coverage
    print("\n1. Running Unit Tests (models.py)...")
    result1 = subprocess.run([
        sys.executable, '-m', 'pytest', 
        'tests/test_models.py', 
        '-v'
    ], capture_output=True, text=True)
    
    print(result1.stdout)
    if result1.stderr:
        print("STDERR:", result1.stderr)
    
    print("\n2. Running Integration Tests (Flask routes)...")
    result2 = subprocess.run([
        sys.executable, '-m', 'pytest', 
        'tests/test_app_integration.py', 
        '-v'
    ], capture_output=True, text=True)
    
    print(result2.stdout)
    if result2.stderr:
        print("STDERR:", result2.stderr)
    
    print("\n3. Running Edge Case and Security Tests...")
    result3 = subprocess.run([
        sys.executable, '-m', 'pytest', 
        'tests/test_edge_cases.py', 
        '-v'
    ], capture_output=True, text=True)
    
    print(result3.stdout)
    if result3.stderr:
        print("STDERR:", result3.stderr)
    
    # Run all tests with coverage report
    print("\n4. Generating Coverage Report...")
    coverage_result = subprocess.run([
        sys.executable, '-m', 'coverage', 'run', 
        '-m', 'pytest', 'tests/', '-v'
    ], capture_output=True, text=True)
    
    # Generate coverage report
    coverage_report = subprocess.run([
        sys.executable, '-m', 'coverage', 'report', 
        '--include=app.py,models.py'
    ], capture_output=True, text=True)
    
    print(coverage_report.stdout)
    
    # Generate HTML coverage report
    subprocess.run([
        sys.executable, '-m', 'coverage', 'html', 
        '--include=app.py,models.py'
    ], capture_output=True, text=True)
    
    print("\nHTML coverage report generated in htmlcov/ directory")
    
    # Summary
    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    print(f"Unit Tests: {'PASS' if result1.returncode == 0 else 'FAIL'}")
    print(f"Integration Tests: {'PASS' if result2.returncode == 0 else 'FAIL'}")
    print(f"Edge Case Tests: {'PASS' if result3.returncode == 0 else 'FAIL'}")
    print(f"Coverage Report: Generated")
    
    return all(r.returncode == 0 for r in [result1, result2, result3])

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)