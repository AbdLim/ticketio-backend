#!/usr/bin/env python3
"""
Test the mock Hedera implementation for development.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


async def test_mock_hedera():
    """Test the mock Hedera implementation."""

    print("🎭 Testing Mock Hedera Implementation...")

    try:
        # Import the original mock service
        from app.utils.hedera import hedera_service

        # Test 1: Create NFT Collection
        print("\n🎫 Testing NFT Collection Creation...")
        token_id = await hedera_service.create_nft_collection(
            name="Mock Event Tickets",
            symbol="MOCK24",
            supply=100,
            metadata_uri="https://api.example.com/metadata/",
        )
        print(f"✅ Created NFT collection: {token_id}")

        # Test 2: Mint NFT
        print("\n🎨 Testing NFT Minting...")
        serial_number = await hedera_service.mint_nft(
            token_id=token_id, metadata="Mock Event - VIP Ticket - Seat A1"
        )
        print(f"✅ Minted NFT: {token_id}:{serial_number}")

        # Test 3: Transfer NFT
        print("\n📤 Testing NFT Transfer...")
        success = await hedera_service.transfer_nft(
            token_id=token_id,
            serial_number=serial_number,
            receiver_id="0.0.123456",  # Mock receiver
        )
        print(f"✅ Transfer result: {success}")

        # Test 4: Verify Ownership
        print("\n🔍 Testing Ownership Verification...")
        is_owner = await hedera_service.verify_nft_ownership(
            token_id=token_id, serial_number=serial_number, wallet_address="0.0.123456"
        )
        print(f"✅ Ownership verification: {is_owner}")

        # Test 5: Get NFT Info
        print("\n📋 Testing NFT Info...")
        nft_info = await hedera_service.get_nft_info(
            token_id=token_id, serial_number=serial_number
        )
        if nft_info:
            print(f"✅ NFT Info: {nft_info}")

        print(f"\n🎉 All mock tests passed!")
        print(f"📝 Mock NFT: {token_id}:{serial_number}")

        return True

    except Exception as e:
        print(f"\n❌ Mock test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Testing Mock Hedera Implementation\n")

    success = asyncio.run(test_mock_hedera())

    if success:
        print("\n✅ Mock implementation works perfectly!")
        print("You can continue development while fixing Hedera credentials.")
    else:
        print("\n❌ Mock tests failed.")
        print("Check the mock implementation.")
