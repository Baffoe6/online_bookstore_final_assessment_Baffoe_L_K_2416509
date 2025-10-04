#!/usr/bin/env python3
"""
Quick Pre-Push CI Check
Fast validation before pushing to GitHub.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


class QuickPrePushCheck:
    """Quick pre-push validation."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.start_time = time.time()

    def run_command(self, command: str) -> tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr."""
        try:
            result = subprocess.run(
                command.split(),
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def print_status(self, test_name: str, success: bool, details: str = ""):
        """Print test status."""
        if success:
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}")
            if details:
                print(f"   {details}")

    def check_formatting(self) -> bool:
        """Quick formatting check."""
        print("🔍 Checking code formatting...")

        # Black check
        success, stdout, stderr = self.run_command(
            "python3.12 -m black --check --diff ."
        )
        if not success:
            self.print_status("Black formatting", False, "Run 'black .' to fix")
            return False

        # isort check
        success, stdout, stderr = self.run_command(
            "python3.12 -m isort --check-only --diff . --profile black"
        )
        if not success:
            self.print_status("Import sorting", False, "Run 'isort .' to fix")
            return False

        self.print_status("Code formatting", True)
        return True

    def check_tests(self) -> bool:
        """Quick test check."""
        print("🧪 Running quick tests...")

        # Run core tests
        success, stdout, stderr = self.run_command(
            "python3.12 -m pytest tests/test_refactored_models.py tests/test_refactored_services.py -x --tb=short"
        )
        if not success:
            self.print_status("Core tests", False)
            return False

        # Run performance tests
        success, stdout, stderr = self.run_command(
            "python3.12 -m pytest tests/test_performance.py -x --tb=short"
        )
        if not success:
            self.print_status("Performance tests", False)
            return False

        self.print_status("Tests", True)
        return True

    def check_app_startup(self) -> bool:
        """Quick app startup check."""
        print("🚀 Checking app startup...")

        # Create temporary startup test file
        startup_test_file = self.project_root / "temp_startup_test.py"
        with open(startup_test_file, "w") as f:
            f.write(
                """import sys
import os
sys.path.insert(0, os.getcwd())
from app_refactored import app
print('App startup OK')
"""
            )

        try:
            success, stdout, stderr = self.run_command(
                f"python3.12 {startup_test_file}"
            )
            if not success:
                self.print_status("App startup", False, f"Error: {stderr}")
                return False

            self.print_status("App startup", True)
            return True
        finally:
            # Clean up temporary file
            if startup_test_file.exists():
                startup_test_file.unlink()

    def run_quick_check(self) -> bool:
        """Run quick pre-push check."""
        print("🚀 Quick Pre-Push CI Check")
        print("=" * 40)

        checks = [
            ("Formatting", self.check_formatting),
            ("Tests", self.check_tests),
            ("App Startup", self.check_app_startup),
        ]

        all_passed = True

        for check_name, check_func in checks:
            try:
                if not check_func():
                    all_passed = False
            except Exception as e:
                self.print_status(check_name, False, str(e))
                all_passed = False

        elapsed = time.time() - self.start_time
        print(f"\n⏱️  Time: {elapsed:.2f}s")

        if all_passed:
            print("\n🎉 Ready to push!")
            return True
        else:
            print("\n❌ Fix issues before pushing!")
            return False


def main():
    """Main function."""
    checker = QuickPrePushCheck()
    success = checker.run_quick_check()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
