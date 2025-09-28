#!/usr/bin/env python3
"""
Minimal token creation test with detailed error handling.
This is the simplest possible NFT creation to isolate issues.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


def test_minimal_token_creation():
    """Test the most basic token creation possible."""

    print("🧪 Minimal Token Creation Test...")

    try:
        from hedera import (
            Client,
            AccountId,
            PrivateKey,
            TokenCreateTransaction,
            TokenType,
            Hbar,
            Status,
        )

        # Get credentials
        operator_id = os.getenv("HEDERA_OPERATOR_ID")
        operator_key = os.getenv("HEDERA_OPERATOR_KEY")

        # Parse credentials
        account_id = AccountId.fromString(operator_id)
        private_key = PrivateKey.fromString(operator_key)

        print(f"📋 Using Account: {account_id}")

        # Create client
        client = Client.forTestnet()
        client.setOperator(account_id, private_key)

        print("✅ Client created and operator set")

        # Create the simplest possible NFT token
        print("🎫 Creating minimal NFT token...")

        token_create_tx = (
            TokenCreateTransaction()
            .setTokenName("Minimal Test Token")
            .setTokenSymbol("MIN")
            .setTokenType(TokenType.NON_FUNGIBLE_UNIQUE)
            .setDecimals(0)
            .setInitialSupply(0)
            .setTreasuryAccountId(account_id)
            .setSupplyKey(private_key)
            .setMaxTransactionFee(Hbar.fromTinybars(5000000000))  # 50 HBAR max fee
        )

        print("📝 Transaction prepared, executing...")

        # Execute with detailed error handling
        try:
            response = token_create_tx.execute(client)
            print("✅ Transaction submitted, getting receipt...")

            receipt = response.getReceipt(client)
            print(f"📋 Receipt status: {receipt.status}")

            if receipt.status == Status.SUCCESS:
                token_id = str(receipt.tokenId)
                print(f"🎉 SUCCESS! Created token: {token_id}")
                return True
            else:
                print(f"❌ Transaction failed with status: {receipt.status}")
                return False

        except Exception as tx_error:
            print(f"❌ Transaction execution failed: {tx_error}")

            # Try to get more details about the error
            error_str = str(tx_error)
            if "INVALID_SIGNATURE" in error_str:
                print("🔍 INVALID_SIGNATURE error detected")
                print("   This usually means:")
                print("   - Private key doesn't match the account")
                print("   - Account is not properly activated")
                print("   - Wrong network (testnet vs mainnet)")
            elif "INSUFFICIENT_PAYER_BALANCE" in error_str:
                print("🔍 Insufficient balance error")
            elif "INVALID_ACCOUNT_ID" in error_str:
                print("🔍 Invalid account ID error")

            return False

        finally:
            client.close()

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Minimal Token Creation Test\n")

    success = test_minimal_token_creation()

    if success:
        print("\n✅ Minimal test passed!")
        print("Your Hedera setup is working correctly.")
    else:
        print("\n❌ Minimal test failed.")
        print("There's still an issue with the Hedera configuration.")
