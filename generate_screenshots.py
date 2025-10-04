#!/usr/bin/env python3
"""
Screenshot Generation Helper Script
This script provides commands and guidance for capturing screenshots
of the test suite, CI/CD pipeline, and project documentation.
"""

import subprocess
import sys
import os
from datetime import datetime

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_command(description, command):
    """Print a command with description."""
    print(f"\n📋 {description}:")
    print(f"Command: {command}")
    print("-" * 50)

def run_command(command, capture_output=True):
    """Run a command and optionally capture output."""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def main():
    """Main function to generate screenshot guidance."""
    
    print_header("📸 SCREENSHOT GENERATION GUIDE")
    print("This script will help you capture screenshots for your project documentation.")
    print("Run each command below and take screenshots of the output.")
    
    # Test Suite Screenshots
    print_header("🧪 TEST SUITE SCREENSHOTS")
    
    print_command(
        "Test Collection Overview (111 tests)",
        "python -m pytest tests/ --collect-only -q"
    )
    
    print_command(
        "Full Test Execution with Verbose Output",
        "python -m pytest tests/ -v"
    )
    
    print_command(
        "Test Execution with Timing Information",
        "python -m pytest tests/ -v --durations=10"
    )
    
    print_command(
        "Edge Case Tests Only (29 tests)",
        'python -m pytest tests/ -k "invalid or error or failure or missing or wrong or empty" -v'
    )
    
    print_command(
        "Performance Tests with Detailed Timing",
        "python -m pytest tests/test_performance.py -v --durations=0"
    )
    
    # Code Quality Screenshots
    print_header("🔍 CODE QUALITY SCREENSHOTS")
    
    print_command(
        "Black Code Formatting Check",
        "black --check --diff ."
    )
    
    print_command(
        "Import Sorting Check",
        "isort --check-only --diff . --profile black"
    )
    
    print_command(
        "MyPy Type Checking",
        "mypy --ignore-missing-imports app_refactored.py models_refactored.py --no-error-summary"
    )
    
    print_command(
        "Security Scanning with Bandit",
        "bandit -r . -f json"
    )
    
    # Project Structure Screenshots
    print_header("📁 PROJECT STRUCTURE SCREENSHOTS")
    
    print_command(
        "Project Directory Structure",
        "ls -la"
    )
    
    print_command(
        "Test Directory Structure",
        "ls -la tests/"
    )
    
    print_command(
        "GitHub Workflows Structure",
        "ls -la .github/workflows/"
    )
    
    print_command(
        "Documentation Files",
        "ls -la *.md"
    )
    
    # Performance Analysis Screenshots
    print_header("⚡ PERFORMANCE ANALYSIS SCREENSHOTS")
    
    print_command(
        "Performance Analysis Script",
        "python performance_analysis.py"
    )
    
    print_command(
        "App Startup Test",
        "python -c 'from app_refactored import app; print(\"App loaded successfully\")'"
    )
    
    print_command(
        "BookService Performance Test",
        "python -c 'from services import BookService; import time; start=time.time(); books=BookService.get_all_books(); print(f\"Loaded {len(books)} books in {time.time()-start:.4f}s\")'"
    )
    
    # GitHub Actions Screenshots (Manual)
    print_header("🚀 GITHUB ACTIONS SCREENSHOTS (Manual)")
    
    print("\n📋 Manual Screenshots Needed:")
    print("1. Navigate to: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/actions")
    print("2. Screenshot: Pipeline overview showing all workflows")
    print("3. Screenshot: Successful test workflow execution")
    print("4. Screenshot: Security scanning results")
    print("5. Screenshot: Code quality checks")
    print("6. Screenshot: Deployment workflow")
    print("7. Screenshot: Pipeline success with green checkmarks")
    
    # Repository Information
    print_header("🔗 REPOSITORY INFORMATION")
    
    print("Repository URL: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509")
    print("GitHub Actions: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/actions")
    print("Issues: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/issues")
    print("Pull Requests: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/pulls")
    
    # Screenshot Tips
    print_header("💡 SCREENSHOT TIPS")
    
    print("1. Use high resolution (1920x1080 or higher)")
    print("2. Ensure text is clearly readable")
    print("3. Include relevant context and labels")
    print("4. Capture both success and detailed views")
    print("5. Show timestamps and execution times")
    print("6. Use consistent naming: screenshot_description.png")
    print("7. Save screenshots in the 'screenshots/' directory")
    
    print_header("✅ READY TO CAPTURE SCREENSHOTS")
    print("Run the commands above and capture screenshots as indicated.")
    print("All screenshots should be saved in the 'screenshots/' directory.")
    
    # Optional: Run a quick test to show current status
    print_header("🔍 CURRENT PROJECT STATUS")
    
    success, stdout, stderr = run_command("python -m pytest tests/ --collect-only -q")
    if success:
        print("✅ Test suite is ready for screenshot capture")
        print(f"Found {len([line for line in stdout.split('\n') if line.strip()])} tests")
    else:
        print("❌ Test suite has issues - please fix before capturing screenshots")
        print(f"Error: {stderr}")

if __name__ == "__main__":
    main()
