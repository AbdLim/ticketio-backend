#!/usr/bin/env python3
"""
Run all Hedera tests in sequence.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_test(test_file):
    """Run a single test file and return success status."""

    print(f"\n{'='*60}")
    print(f"🧪 Running {test_file}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            [sys.executable, f"tests/hedera/{test_file}"],
            capture_output=False,
            text=True,
            cwd=project_root,
        )

        success = result.returncode == 0

        if success:
            print(f"✅ {test_file} PASSED")
        else:
            print(f"❌ {test_file} FAILED")

        return success

    except Exception as e:
        print(f"❌ {test_file} ERROR: {e}")
        return False


def main():
    """Run all tests in recommended order."""

    print("🚀 Running All Hedera Tests")
    print("This will run tests in the recommended order for debugging")

    # Test sequence in order of importance
    tests = [
        ("test_basic_connection.py", "Basic SDK Connection"),
        ("test_credentials.py", "Credential Verification"),
        ("test_account_balance.py", "Account Balance Check"),
        ("test_account_key_match.py", "Account-Key Match (Critical!)"),
        ("test_minimal_token.py", "Minimal Token Creation"),
        ("test_mock_implementation.py", "Mock Implementation"),
        ("test_full_implementation.py", "Full Implementation"),
    ]

    results = {}

    for test_file, description in tests:
        print(f"\n📋 Next: {description}")
        input("Press Enter to continue (or Ctrl+C to stop)...")

        success = run_test(test_file)
        results[test_file] = success

        if not success and test_file != "test_mock_implementation.py":
            print(f"\n⚠️  {test_file} failed!")
            print("You should fix this issue before continuing.")

            continue_anyway = input("Continue anyway? (y/N): ").lower().strip()
            if continue_anyway != "y":
                break

    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")

    passed = 0
    total = len(results)

    for test_file, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_file}")
        if success:
            passed += 1

    print(f"\n📈 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your Hedera integration is working perfectly.")
    elif results.get("test_mock_implementation.py", False):
        print("🎭 Mock implementation works - you can continue development.")
        print("💡 Fix the real Hedera issues when ready for production.")
    else:
        print("❌ Multiple issues found. Check the failed tests above.")

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
