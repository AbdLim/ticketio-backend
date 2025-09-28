#!/usr/bin/env python3
"""
Utility functions for Hedera testing.
"""

import os
from pathlib import Path


def create_fresh_account():
    """Create a completely fresh Hedera account."""

    print("🆕 Creating Fresh Hedera Account...")

    try:
        from hedera import PrivateKey

        # Generate completely new credentials
        new_private_key = PrivateKey.generateED25519()
        new_public_key = new_private_key.getPublicKey()

        print("✅ Generated new credentials:")
        print(f"🔑 Private Key: {new_private_key}")
        print(f"🔓 Public Key: {new_public_key}")

        print(f"\n📝 To use this account:")
        print(f"1. Go to https://portal.hedera.com/")
        print(f"2. Create new account with this public key: {new_public_key}")
        print(f"3. Fund the account with testnet HBAR")
        print(f"4. Update your .env file:")
        print(f"   HEDERA_OPERATOR_ID=0.0.NEW_ACCOUNT_ID")
        print(f"   HEDERA_OPERATOR_KEY={new_private_key}")

        return True

    except Exception as e:
        print(f"❌ Failed to generate credentials: {e}")
        return False


def show_key_format_examples():
    """Show examples of both key formats."""

    print("\n📋 Private Key Format Examples:")
    print("\n1️⃣  HEX ENCODED PRIVATE KEY:")
    print("   Format: 64 hex characters")
    print(
        "   Example: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
    )
    print("   Length: 64 characters")

    print("\n2️⃣  DER ENCODED PRIVATE KEY:")
    print("   Format: Starts with '302e020100', longer")
    print(
        "   Example: 302e020100300506032b657004220420a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
    )
    print("   Length: 96+ characters")

    print("\n🎯 RECOMMENDATION:")
    print("   Try DER ENCODED PRIVATE KEY first (the longer one)")
    print("   If that doesn't work, try HEX ENCODED PRIVATE KEY")


def check_environment_setup():
    """Check if all required environment variables are set."""

    required_vars = [
        "HEDERA_NETWORK",
        "HEDERA_OPERATOR_ID",
        "HEDERA_OPERATOR_KEY",
        "HEDERA_MIRROR_NODE_URL",
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("\nAdd these to your .env file:")
        for var in missing_vars:
            if var == "HEDERA_NETWORK":
                print(f"{var}=testnet")
            elif var == "HEDERA_OPERATOR_ID":
                print(f"{var}=0.0.YOUR_ACCOUNT_ID")
            elif var == "HEDERA_OPERATOR_KEY":
                print(f"{var}=YOUR_DER_ENCODED_PRIVATE_KEY")
            elif var == "HEDERA_MIRROR_NODE_URL":
                print(f"{var}=https://testnet.mirrornode.hedera.com")
        return False

    print("✅ All environment variables are set")
    return True


if __name__ == "__main__":
    print("🛠️  Hedera Test Utilities\n")

    print("Available utilities:")
    print("- create_fresh_account()")
    print("- show_key_format_examples()")
    print("- check_environment_setup()")

    check_environment_setup()
    show_key_format_examples()
