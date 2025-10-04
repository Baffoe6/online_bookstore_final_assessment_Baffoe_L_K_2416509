#!/usr/bin/env python3
"""
Critical Evaluation Report Screenshot Generator
This script provides specific commands to generate the screenshots needed for the Critical Evaluation Report.
"""

import subprocess
import sys
import os

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_screenshot_instruction(figure_number, description, command):
    """Print screenshot instruction with command."""
    print(f"\n📸 **Figure {figure_number}: {description}**")
    print(f"Command: {command}")
    print(f"Screenshot: screenshots/{description.lower().replace(' ', '_')}.png")
    print("-" * 70)

def main():
    """Main function to generate screenshot instructions."""
    
    print_header("📸 CRITICAL EVALUATION REPORT SCREENSHOTS")
    print("Generate these specific screenshots for your Critical Evaluation Report:")
    
    # Test Suite Screenshots
    print_header("🧪 TEST SUITE SCREENSHOTS")
    
    print_screenshot_instruction(
        1, "Test Suite Overview",
        "python -m pytest tests/ --collect-only -q"
    )
    
    print_screenshot_instruction(
        2, "Test Execution Results",
        "python -m pytest tests/ -v"
    )
    
    print_screenshot_instruction(
        3, "Edge Case Testing",
        'python -m pytest tests/ -k "invalid or error or failure or missing or wrong or empty" -v'
    )
    
    print_screenshot_instruction(
        4, "Performance Testing",
        "python -m pytest tests/test_performance.py -v --durations=5"
    )
    
    # CI/CD Pipeline Screenshots
    print_header("🚀 CI/CD PIPELINE SCREENSHOTS")
    
    print_screenshot_instruction(
        5, "CI/CD Pipeline Overview",
        "Navigate to: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/actions"
    )
    
    print_screenshot_instruction(
        6, "Test Workflow",
        "Navigate to: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/actions and click on a successful test run"
    )
    
    print_screenshot_instruction(
        7, "Code Quality Checks",
        "Navigate to: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/actions and click on code-quality workflow"
    )
    
    print_screenshot_instruction(
        8, "Project Structure",
        "ls -la"
    )
    
    print_screenshot_instruction(
        9, "GitHub Actions Success",
        "Navigate to: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/actions and screenshot the main pipeline view"
    )
    
    # Repository Information
    print_header("🔗 REPOSITORY INFORMATION")
    
    print("\n📋 **Repository Links for Report:**")
    print("- Main Repository: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509")
    print("- GitHub Actions: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/actions")
    print("- Project Documentation: https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509/blob/main/README.md")
    
    # Screenshot Tips
    print_header("💡 SCREENSHOT TIPS")
    
    print("1. Use high resolution (1920x1080 or higher)")
    print("2. Ensure text is clearly readable")
    print("3. Include relevant context and labels")
    print("4. Show timestamps and execution times")
    print("5. Use consistent naming: figure_description.png")
    print("6. Save screenshots in the 'screenshots/' directory")
    print("7. For GitHub Actions screenshots, ensure you're logged in and can see the workflows")
    
    # Quick Test
    print_header("🔍 QUICK VERIFICATION")
    
    try:
        result = subprocess.run("python -m pytest tests/ --collect-only -q", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            test_count = len([line for line in result.stdout.split('\n') if line.strip() and '::' in line])
            print(f"✅ Test suite ready: {test_count} tests found")
            print("✅ Ready to generate screenshots!")
        else:
            print("❌ Test suite has issues - please fix before capturing screenshots")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Error checking test suite: {e}")

if __name__ == "__main__":
    main()
