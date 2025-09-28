#!/usr/bin/env python3
"""
Check Hedera account balance and verify sufficient funds.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


def check_account_balance():
    """Check the HBAR balance of the operator account."""

    print("💰 Checking Account Balance...")

    try:
        from hedera import Client, AccountId, PrivateKey, AccountBalanceQuery

        # Get credentials
        operator_id = os.getenv("HEDERA_OPERATOR_ID")
        operator_key = os.getenv("HEDERA_OPERATOR_KEY")

        if not operator_id or not operator_key:
            print("❌ Missing HEDERA_OPERATOR_ID or HEDERA_OPERATOR_KEY")
            return False

        # Parse credentials
        account_id = AccountId.fromString(operator_id)
        private_key = PrivateKey.fromString(operator_key)

        # Create client
        client = Client.forTestnet()
        client.setOperator(account_id, private_key)

        # Query balance
        balance_query = AccountBalanceQuery().setAccountId(account_id)
        balance = balance_query.execute(client)

        print(f"📋 Account: {operator_id}")
        print(f"💰 Balance: {balance.hbars} HBAR")

        # Convert to tinybars for precise checking
        tinybars = balance.hbars.toTinybars()
        hbar_amount = tinybars / 100000000  # Convert tinybars to HBAR

        print(f"📊 Precise Balance: {hbar_amount} HBAR ({tinybars} tinybars)")

        # Check if sufficient for operations
        if hbar_amount < 1:
            print("⚠️  Low balance! You need at least 1 HBAR for token operations")
            print("💡 Get free testnet HBAR at: https://portal.hedera.com/")
            return False
        elif hbar_amount < 10:
            print("⚠️  Balance is low but might work for basic operations")
            return True
        else:
            print("✅ Sufficient balance for token operations")
            return True

        client.close()

    except Exception as e:
        print(f"❌ Failed to check balance: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Hedera Balance Check\n")

    success = check_account_balance()

    if not success:
        print("\n💡 To get testnet HBAR:")
        print("1. Go to https://portal.hedera.com/")
        print("2. Login with your account")
        print("3. Request testnet HBAR (free)")
        print("4. Wait a few minutes for funding")
