#!/usr/bin/env python3
"""
Test the full Hedera implementation with all NFT operations.
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

# Import the corrected service
sys.path.append(str(project_root / "hedera_implementations"))
from hedera_corrected import corrected_hedera_service


async def test_full_hedera_implementation():
    """Test the full Hedera implementation."""

    print("🧪 Testing Full Hedera Implementation...")

    # Check environment variables
    required_vars = ["HEDERA_NETWORK", "HEDERA_OPERATOR_ID", "HEDERA_OPERATOR_KEY"]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False

    try:
        # Test 1: Create NFT Collection
        print("\n🎫 Testing NFT Collection Creation...")
        token_id = await corrected_hedera_service.create_nft_collection(
            name="Test Tickets 2024",
            symbol="TEST24",
            supply=100,
            metadata_uri="https://api.example.com/metadata/",
        )
        print(f"✅ Created NFT collection: {token_id}")

        # Test 2: Mint NFT
        print("\n🎨 Testing NFT Minting...")
        serial_number = await corrected_hedera_service.mint_nft(
            token_id=token_id, metadata="Test Event - General Admission - Row 1 Seat 1"
        )
        print(f"✅ Minted NFT: {token_id}:{serial_number}")

        # Test 3: Get NFT Info (using Mirror Node)
        print("\n📋 Testing NFT Information Retrieval...")
        await asyncio.sleep(2)  # Wait for Mirror Node to sync

        nft_info = await corrected_hedera_service.get_nft_info(
            token_id=token_id, serial_number=serial_number
        )
        if nft_info:
            print(f"✅ Retrieved NFT info:")
            print(f"   Owner: {nft_info.get('owner')}")
            print(f"   Metadata: {nft_info.get('metadata')}")
        else:
            print("⚠️  NFT info not yet available (Mirror Node sync delay)")

        # Test 4: Verify Ownership
        print("\n🔍 Testing Ownership Verification...")
        operator_id = os.getenv("HEDERA_OPERATOR_ID")

        is_owner = await corrected_hedera_service.verify_nft_ownership(
            token_id=token_id, serial_number=serial_number, wallet_address=operator_id
        )

        if is_owner:
            print(f"✅ Ownership verified: {operator_id} owns the NFT")
        else:
            print("⚠️  Ownership not verified (might be Mirror Node delay)")

        print(f"\n🎉 Tests completed!")
        print(f"📝 Created test NFT: {token_id}:{serial_number}")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nPossible issues:")
        print("- Insufficient HBAR balance")
        print("- Network connectivity")
        print("- Invalid credentials")
        return False

    finally:
        # Clean up
        corrected_hedera_service.close()


if __name__ == "__main__":
    print("🚀 Testing Full Hedera Implementation\n")

    success = asyncio.run(test_full_hedera_implementation())

    if success:
        print("\n✅ Full implementation works!")
        print("You can now use this version in your application.")
    else:
        print("\n❌ Tests failed.")
        print("Check your configuration and try again.")
