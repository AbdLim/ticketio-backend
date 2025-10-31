#!/usr/bin/env python3
"""
Hedera Test Suite - Interactive test runner.
Usage: python -m tests.hedera
"""

import subprocess
import sys
from pathlib import Path


class HederaTestRunner:
    """Interactive test runner for Hedera tests."""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent

        self.tests = {
            "1": ("Basic Connection Test", "test_basic_connection.py"),
            "2": ("Credential Verification", "test_credentials.py"),
            "3": ("Account Balance Check", "test_account_balance.py"),
            "4": ("Account-Key Match", "test_account_key_match.py"),
            "5": ("Minimal Token Creation", "test_minimal_token.py"),
            "6": ("Mock Implementation", "test_mock_implementation.py"),
            "7": ("Full Implementation", "test_full_implementation.py"),
            "8": ("Test Utilities", "utils.py"),
        }

    def show_menu(self):
        """Display the test menu."""
        print("\n" + "=" * 60)
        print("🧪 HEDERA TEST SUITE")
        print("=" * 60)
        print("\nAvailable Tests:")

        for key, (name, _) in self.tests.items():
            print(f"  {key}. {name}")

        print(f"\n  0. Exit")
        print(f"  a. Run All Tests (Interactive)")
        print(f"  r. Run Recommended Sequence")
        print("\n" + "=" * 60)

    def run_test(self, test_file):
        """Run a single test file."""
        test_path = self.test_dir / test_file

        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            return False

        print(f"\n{'='*50}")
        print(f"🧪 Running {test_file}")
        print(f"{'='*50}")

        try:
            result = subprocess.run(
                [sys.executable, str(test_path)], cwd=self.project_root, text=True
            )

            success = result.returncode == 0

            if success:
                print(f"\n✅ {test_file} PASSED")
            else:
                print(f"\n❌ {test_file} FAILED (exit code: {result.returncode})")

            return success

        except Exception as e:
            print(f"\n❌ Error running {test_file}: {e}")
            return False

    def run_all_tests_interactive(self):
        """Run all tests with interactive prompts."""
        print("\n🚀 Running All Tests (Interactive Mode)")
        print("You can skip tests or stop at any point.")

        results = {}

        for key, (name, test_file) in self.tests.items():
            if test_file == "utils.py":  # Skip utilities
                continue

            print(f"\n📋 Next: {name}")
            choice = input("Run this test? (y/n/q to quit): ").lower().strip()

            if choice == "q":
                print("⏹️  Stopping tests...")
                break
            elif choice == "n":
                print(f"⏭️  Skipping {name}")
                results[name] = "skipped"
                continue

            success = self.run_test(test_file)
            results[name] = "passed" if success else "failed"

            if not success:
                continue_choice = (
                    input("\nTest failed. Continue anyway? (y/n): ").lower().strip()
                )
                if continue_choice != "y":
                    break

        self.show_results(results)

    def run_recommended_sequence(self):
        """Run tests in recommended diagnostic order."""
        print("\n🎯 Running Recommended Test Sequence")
        print("This runs tests in the best order for diagnosing issues.")

        # Recommended order for debugging
        recommended_order = [
            ("2", "Credential check first"),
            ("3", "Balance check"),
            ("4", "Account-key match (most important!)"),
            ("1", "Basic connection"),
            ("5", "Token creation"),
            ("6", "Mock implementation (fallback)"),
        ]

        results = {}

        for key, description in recommended_order:
            if key not in self.tests:
                continue

            name, test_file = self.tests[key]
            print(f"\n📋 {description}")
            print(f"Running: {name}")

            success = self.run_test(test_file)
            results[name] = "passed" if success else "failed"

            # Stop on critical failures
            if not success and key in ["2", "4"]:  # Credentials or account-key match
                print(f"\n⚠️  Critical test failed: {name}")
                print("Fix this issue before continuing with other tests.")
                break

        self.show_results(results)

    def show_results(self, results):
        """Show test results summary."""
        if not results:
            return

        print(f"\n{'='*50}")
        print("📊 TEST RESULTS SUMMARY")
        print(f"{'='*50}")

        passed = failed = skipped = 0

        for test_name, status in results.items():
            if status == "passed":
                print(f"✅ PASS  {test_name}")
                passed += 1
            elif status == "failed":
                print(f"❌ FAIL  {test_name}")
                failed += 1
            elif status == "skipped":
                print(f"⏭️  SKIP  {test_name}")
                skipped += 1

        total = passed + failed + skipped
        print(
            f"\n📈 Results: {passed} passed, {failed} failed, {skipped} skipped ({total} total)"
        )

        if failed == 0 and passed > 0:
            print("🎉 All tests passed! Your Hedera integration is working.")
        elif passed > 0:
            print("⚠️  Some tests failed. Check the failed tests above.")
        else:
            print("❌ No tests passed. Check your Hedera configuration.")

    def show_help(self):
        """Show help information."""
        print("\n📖 HELP")
        print("=" * 40)
        print("\n🎯 Recommended first-time sequence:")
        print("  1. Run test 2 (Credential Verification)")
        print("  2. Run test 4 (Account-Key Match) - Most Important!")
        print("  3. Run test 3 (Account Balance)")
        print("  4. Run test 5 (Token Creation)")
        print("  5. Run test 6 (Mock) if real tests fail")

        print("\n🔧 Common Issues:")
        print("  • INVALID_SIGNATURE → Run test 4 (Account-Key Match)")
        print("  • Missing variables → Run test 2 (Credentials)")
        print("  • Low balance → Run test 3 (Balance)")
        print("  • SDK issues → Run test 1 (Basic Connection)")

        print("\n📁 Files:")
        print("  • .env file should have HEDERA_* variables")
        print("  • Use DER ENCODED PRIVATE KEY from Hedera Portal")
        print("  • Account ID format: 0.0.123456")

        print("\n💡 Tips:")
        print("  • Test 6 (Mock) always works for development")
        print("  • Fix real Hedera issues when ready for production")
        print("  • Run 'r' for recommended diagnostic sequence")

    def run(self):
        """Main test runner loop."""
        print("🚀 Hedera Test Suite")
        print("Interactive test runner for Hedera blockchain integration")

        while True:
            self.show_menu()

            choice = input("\nSelect option: ").strip().lower()

            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "a":
                self.run_all_tests_interactive()
            elif choice == "r":
                self.run_recommended_sequence()
            elif choice == "h":
                self.show_help()
            elif choice in self.tests:
                name, test_file = self.tests[choice]
                print(f"\n🧪 Running: {name}")
                self.run_test(test_file)
            else:
                print("❌ Invalid choice. Try again or type 'h' for help.")

            if choice != "0":
                input("\nPress Enter to continue...")


def main():
    """Entry point when running as module."""
    try:
        runner = HederaTestRunner()
        runner.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
