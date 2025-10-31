#!/usr/bin/env python3
"""
Verify that the Account ID and Private Key actually belong together.
This is the most common cause of INVALID_SIGNATURE errors.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


def verify_account_key_match():
    """Check if the account ID and private key belong together."""

    print("🔍 Verifying Account-Key Match...")

    try:
        from hedera import (
            Client,
            AccountId,
            PrivateKey,
            AccountInfoQuery,
            TransactionId,
        )

        # Get credentials
        operator_id = os.getenv("HEDERA_OPERATOR_ID")
        operator_key = os.getenv("HEDERA_OPERATOR_KEY")

        # Parse credentials
        account_id = AccountId.fromString(operator_id)
        private_key = PrivateKey.fromString(operator_key)
        public_key = private_key.getPublicKey()

        print(f"📋 Account ID: {account_id}")
        print(f"🔑 Private Key: {str(private_key)[:20]}...")
        print(f"🔓 Derived Public Key: {str(public_key)[:50]}...")

        # Create client
        client = Client.forTestnet()

        # Query account info WITHOUT setting operator
        # This avoids signature issues
        print("\n🔍 Querying account info...")

        account_info_query = AccountInfoQuery().setAccountId(account_id)

        # We need to set a payment account for the query
        # Let's try using the same account but see what happens
        try:
            client.setOperator(account_id, private_key)
            account_info = account_info_query.execute(client)

            print(f"✅ Account info retrieved successfully!")
            print(f"📋 Account Key: {account_info.key}")
            print(f"📊 Balance: {account_info.balance}")

            # Compare the keys properly
            # Convert both to bytes for accurate comparison
            try:
                # Get the account's public key in bytes
                account_key_bytes = account_info.key.toBytes()
                # Get our derived public key in bytes
                derived_key_bytes = public_key.toBytes()

                print(f"\n🔍 Key Comparison (bytes):")
                print(f"   Account Key: {str(account_key_bytes)[:50]}...")
                print(f"   Derived Key: {str(derived_key_bytes)[:50]}...")

                if account_key_bytes == derived_key_bytes:
                    print("✅ Keys match! Account and private key belong together.")
                    return True
                else:
                    print("❌ Keys don't match! Wrong private key for this account.")
                    print(
                        "💡 You need to use the private key that was used to create this account."
                    )

                    # Show more details for debugging
                    print(f"\n🔍 Detailed Key Analysis:")
                    print(f"   Account Key Type: {type(account_info.key)}")
                    print(f"   Derived Key Type: {type(public_key)}")
                    print(f"   Account Key Length: {len(account_key_bytes)} bytes")
                    print(f"   Derived Key Length: {len(derived_key_bytes)} bytes")

                    return False

            except Exception as key_error:
                print(f"❌ Key comparison failed: {key_error}")
                print("Falling back to string comparison...")

                # Fallback to string comparison
                account_public_key = str(account_info.key)
                derived_public_key = str(public_key)

                print(f"\n🔍 String Key Comparison:")
                print(f"   Account Key: {account_public_key[:50]}...")
                print(f"   Derived Key: {derived_public_key[:50]}...")

                return account_public_key == derived_public_key

        except Exception as query_error:
            print(f"❌ Query failed: {query_error}")

            if "INVALID_SIGNATURE" in str(query_error):
                print("🔍 Still getting INVALID_SIGNATURE on simple query")
                print("   This confirms the account-key mismatch")
                return False
            else:
                print("❓ Different error - might be network or other issue")
                return False

        finally:
            client.close()

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Account-Key Match Verification\n")

    success = verify_account_key_match()

    if success:
        print("\n✅ Account and key match!")
        print("The INVALID_SIGNATURE issue must be something else.")
    else:
        print("\n❌ Account and key don't match!")
        print("Solutions:")
        print(
            "1. Get the correct private key for account",
            os.getenv("HEDERA_OPERATOR_ID"),
        )
        print("2. Or create a new account with the current private key")
        print("3. Double-check you're using DER ENCODED PRIVATE KEY from portal")
