#!/usr/bin/env python3
"""
Basic Hedera SDK connection test.
Tests if the Hedera SDK can be imported and basic operations work.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


async def test_basic_hedera():
    """Test the most basic Hedera operations."""

    print("🔍 Testing Basic Hedera SDK Import...")

    try:
        # Test 1: Can we import the SDK?
        from hedera import Client, AccountId, PrivateKey

        print("✅ Hedera SDK imported successfully")

        # Test 2: Can we parse credentials?
        operator_id = os.getenv("HEDERA_OPERATOR_ID")
        operator_key = os.getenv("HEDERA_OPERATOR_KEY")

        if not operator_id or not operator_key:
            print("❌ Missing HEDERA_OPERATOR_ID or HEDERA_OPERATOR_KEY")
            return False

        account_id = AccountId.fromString(operator_id)
        private_key = PrivateKey.fromString(operator_key)
        print(f"✅ Parsed credentials: {account_id}")

        # Test 3: Can we create a client?
        client = Client.forTestnet()
        client.setOperator(account_id, private_key)
        print("✅ Created Hedera client")

        # Test 4: Can we query account balance?
        from hedera import AccountBalanceQuery

        balance_query = AccountBalanceQuery().setAccountId(account_id)
        balance = balance_query.execute(client)

        print(f"✅ Account balance: {balance.hbars} HBAR")

        if balance.hbars.toTinybars() < 100000000:  # Less than 1 HBAR
            print("⚠️  Low HBAR balance - you might need more for transactions")

        client.close()
        return True

    except ImportError as e:
        print(f"❌ Failed to import Hedera SDK: {e}")
        print("Run: pip install hedera-sdk-py")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Basic Hedera Test\n")
    success = asyncio.run(test_basic_hedera())

    if success:
        print("\n✅ Basic test passed! You can proceed with the full implementation.")
    else:
        print("\n❌ Basic test failed. Fix these issues before proceeding.")
