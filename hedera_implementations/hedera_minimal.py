"""
Minimal Hedera implementation - start with this if the full version has issues.
"""

import asyncio
import logging
from typing import Optional

from hedera import (
    Client,
    PrivateKey,
    AccountId,
    TokenCreateTransaction,
    TokenType,
    TokenSupplyType,
    Hbar,
    Status,
)

from app.core.config import Settings

settings = Settings()
logger = logging.getLogger(__name__)


class MinimalHederaService:
    """Minimal Hedera service - only essential functions."""

    def __init__(self):
        self.network = settings.HEDERA_NETWORK
        self.operator_id = settings.HEDERA_OPERATOR_ID
        self.operator_key = settings.HEDERA_OPERATOR_KEY
        self._client = None

    def _get_client(self) -> Client:
        """Get Hedera client."""
        if self._client is None:
            # Parse credentials
            operator_account_id = AccountId.from_string(self.operator_id)
            operator_private_key = PrivateKey.from_string(self.operator_key)

            # Create client
            if self.network.lower() == "testnet":
                self._client = Client.for_testnet()
            else:
                self._client = Client.for_mainnet()

            # Set operator
            self._client.set_operator(operator_account_id, operator_private_key)

        return self._client

    async def create_nft_collection(
        self, name: str, symbol: str, supply: int, metadata_uri: str
    ) -> str:
        """Create NFT collection - minimal version."""
        try:
            client = self._get_client()
            operator_account_id = AccountId.from_string(self.operator_id)
            operator_private_key = PrivateKey.from_string(self.operator_key)

            # Create token with minimal settings
            token_create_tx = (
                TokenCreateTransaction()
                .set_token_name(name)
                .set_token_symbol(symbol)
                .set_token_type(TokenType.NON_FUNGIBLE_UNIQUE)
                .set_decimals(0)
                .set_initial_supply(0)
                .set_treasury_account_id(operator_account_id)
                .set_supply_key(operator_private_key)
                .set_admin_key(operator_private_key)
                .set_max_transaction_fee(Hbar(10))  # Conservative fee
            )

            # Execute
            response = await asyncio.to_thread(token_create_tx.execute, client)
            receipt = await asyncio.to_thread(response.get_receipt, client)

            if receipt.status == Status.SUCCESS:
                token_id = str(receipt.token_id)
                logger.info(f"Created token: {token_id}")
                return token_id
            else:
                raise Exception(f"Token creation failed: {receipt.status}")

        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise

    async def mint_nft(self, token_id: str, metadata: str) -> str:
        """Mint NFT - minimal version."""
        try:
            from hedera import TokenMintTransaction

            client = self._get_client()

            # Simple mint
            mint_tx = (
                TokenMintTransaction()
                .set_token_id(token_id)
                .add_metadata(metadata.encode("utf-8"))
                .set_max_transaction_fee(Hbar(5))
            )

            response = await asyncio.to_thread(mint_tx.execute, client)
            receipt = await asyncio.to_thread(response.get_receipt, client)

            if receipt.status == Status.SUCCESS and receipt.serial_numbers:
                serial_number = str(receipt.serial_numbers[0])
                logger.info(f"Minted NFT: {token_id}:{serial_number}")
                return serial_number
            else:
                raise Exception(f"Minting failed: {receipt.status}")

        except Exception as e:
            logger.error(f"Minting error: {e}")
            raise

    async def transfer_nft(
        self, token_id: str, serial_number: str, receiver_id: str
    ) -> bool:
        """Transfer NFT - simplified version."""
        try:
            from hedera import TransferTransaction

            client = self._get_client()
            sender_id = AccountId.from_string(self.operator_id)
            receiver_account_id = AccountId.from_string(receiver_id)

            # Simple transfer
            transfer_tx = (
                TransferTransaction()
                .add_nft_transfer(
                    token_id, int(serial_number), sender_id, receiver_account_id
                )
                .set_max_transaction_fee(Hbar(2))
            )

            response = await asyncio.to_thread(transfer_tx.execute, client)
            receipt = await asyncio.to_thread(response.get_receipt, client)

            success = receipt.status == Status.SUCCESS
            if success:
                logger.info(f"Transferred {token_id}:{serial_number} to {receiver_id}")

            return success

        except Exception as e:
            logger.error(f"Transfer error: {e}")
            return False

    async def verify_nft_ownership(
        self, token_id: str, serial_number: str, wallet_address: str
    ) -> bool:
        """Verify ownership - Mirror Node only for simplicity."""
        try:
            import aiohttp

            url = f"{settings.HEDERA_MIRROR_NODE_URL}/api/v1/tokens/{token_id}/nfts/{serial_number}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        owner = data.get("account_id", "")
                        return owner == wallet_address

            return False

        except Exception as e:
            logger.error(f"Ownership verification error: {e}")
            return False

    def close(self):
        """Close client."""
        if self._client:
            self._client.close()
            self._client = None


# Minimal service instance
minimal_hedera_service = MinimalHederaService()
