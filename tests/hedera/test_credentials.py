#!/usr/bin/env python3
"""
Hedera credentials verification tests.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


def verify_hedera_credentials():
    """Verify Hedera credentials format and basic info."""

    print("🔍 Verifying Hedera Credentials...")

    operator_id = os.getenv("HEDERA_OPERATOR_ID")
    operator_key = os.getenv("HEDERA_OPERATOR_KEY")

    if not operator_id:
        print("❌ HEDERA_OPERATOR_ID not set")
        return False

    if not operator_key:
        print("❌ HEDERA_OPERATOR_KEY not set")
        return False

    # Check Account ID format
    print(f"📋 Account ID: {operator_id}")
    if not operator_id.startswith("0.0."):
        print("❌ Account ID should start with '0.0.'")
        return False

    try:
        parts = operator_id.split(".")
        if len(parts) != 3 or not parts[2].isdigit():
            print("❌ Account ID format should be '0.0.123456'")
            return False
    except:
        print("❌ Invalid Account ID format")
        return False

    # Check Private Key format
    print(f"🔑 Private Key: {operator_key[:10]}...{operator_key[-10:]}")

    if len(operator_key) < 64:
        print("❌ Private key seems too short")
        return False

    # Try to parse with Hedera SDK
    try:
        from hedera import AccountId, PrivateKey

        account_id = AccountId.fromString(operator_id)
        private_key = PrivateKey.fromString(operator_key)

        print(f"✅ Account ID parsed: {account_id}")
        print(f"✅ Private Key parsed successfully")

        # Get the public key to verify
        public_key = private_key.getPublicKey()
        print(f"📋 Public Key: {public_key}")

        return True

    except Exception as e:
        print(f"❌ Failed to parse credentials: {e}")
        return False


def analyze_private_key():
    """Analyze the private key format."""

    print("\n🔍 Analyzing Private Key Format...")

    operator_key = os.getenv("HEDERA_OPERATOR_KEY")

    if not operator_key:
        print("❌ HEDERA_OPERATOR_KEY not set")
        return False

    print(f"🔑 Key: {operator_key[:20]}...{operator_key[-20:]}")
    print(f"📏 Length: {len(operator_key)} characters")

    # Check format
    if operator_key.startswith("302e020100"):
        print("✅ Starts with DER prefix (302e020100) - Good!")
    elif operator_key.startswith("0x"):
        print("⚠️  Starts with 0x - This might be HEX format, not DER")
    else:
        print("❓ Unknown format")

    # Check length
    if len(operator_key) == 96:  # DER encoded ED25519 key
        print("✅ Length matches DER encoded ED25519 key")
    elif len(operator_key) == 64:
        print("⚠️  Length matches raw private key (needs DER encoding)")
    elif len(operator_key) == 66 and operator_key.startswith("0x"):
        print("⚠️  Length matches hex private key (wrong format)")
    else:
        print(f"❓ Unusual length: {len(operator_key)}")

    return True


if __name__ == "__main__":
    print("🚀 Hedera Credential Verification\n")

    success = verify_hedera_credentials()
    analyze_private_key()

    if success:
        print("\n✅ Credentials look valid!")
        print("The issue might be:")
        print("- Account not activated on testnet")
        print("- Insufficient HBAR balance")
        print("- Wrong network (testnet vs mainnet)")
    else:
        print("\n❌ Credential issues found.")
        print("Please check your .env file configuration.")
