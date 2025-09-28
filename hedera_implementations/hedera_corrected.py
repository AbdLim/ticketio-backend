"""
Corrected Hedera implementation based on actual SDK API.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Optional, List

from hedera import (
    Client,
    PrivateKey,
    AccountId,
    TokenCreateTransaction,
    TokenType,
    TokenSupplyType,
    TokenMintTransaction,
    TransferTransaction,
    TokenNftInfoQuery,
    TokenInfoQuery,
    Hbar,
    Status,
    TokenAssociateTransaction,
    AccountBalanceQuery,
)

from app.core.config import Settings

settings = Settings()
logger = logging.getLogger(__name__)


class CorrectedHederaService:
    def __init__(self):
        self.network = settings.HEDERA_NETWORK
        self.operator_id = settings.HEDERA_OPERATOR_ID
        self.operator_key = settings.HEDERA_OPERATOR_KEY
        self.mirror_node_url = settings.HEDERA_MIRROR_NODE_URL

        # Initialize Hedera client
        self._client = None
        self._operator_private_key = None
        self._operator_account_id = None

    def _get_client(self) -> Client:
        """Get or create Hedera client instance."""
        if self._client is None:
            try:
                # Parse operator credentials (corrected API)
                self._operator_account_id = AccountId.fromString(self.operator_id)
                self._operator_private_key = PrivateKey.fromString(self.operator_key)

                # Create client based on network (corrected API)
                if self.network.lower() == "testnet":
                    self._client = Client.forTestnet()
                elif self.network.lower() == "mainnet":
                    self._client = Client.forMainnet()
                else:
                    # Default to testnet for development
                    self._client = Client.forTestnet()

                # Set operator (corrected API)
                self._client.setOperator(
                    self._operator_account_id, self._operator_private_key
                )

                logger.info(f"Hedera client initialized for {self.network}")

            except Exception as e:
                logger.error(f"Failed to initialize Hedera client: {e}")
                raise Exception(f"Hedera client initialization failed: {e}")

        return self._client

    async def create_nft_collection(
        self,
        name: str,
        symbol: str,
        supply: int,
        metadata_uri: str,
        treasury_account: Optional[str] = None,
    ) -> str:
        """
        Create a new NFT collection on Hedera.
        """
        try:
            client = self._get_client()

            # Use operator account as treasury if not specified
            treasury_id = (
                AccountId.fromString(treasury_account)
                if treasury_account
                else self._operator_account_id
            )

            # Create NFT token (corrected API)
            token_create_tx = (
                TokenCreateTransaction()
                .setTokenName(name)
                .setTokenSymbol(symbol)
                .setTokenType(TokenType.NON_FUNGIBLE_UNIQUE)
                .setDecimals(0)
                .setInitialSupply(0)
                .setTreasuryAccountId(treasury_id)
                .setSupplyType(
                    TokenSupplyType.FINITE if supply > 0 else TokenSupplyType.INFINITE
                )
                .setMaxSupply(supply if supply > 0 else 0)
                .setSupplyKey(self._operator_private_key)
                .setAdminKey(self._operator_private_key)
                .setFreezeDefault(False)
                .setMaxTransactionFee(Hbar.fromTinybars(3000000000))  # 30 HBAR
            )

            # Execute transaction
            token_create_submit = token_create_tx.execute(client)
            token_create_receipt = token_create_submit.getReceipt(client)

            if token_create_receipt.status != Status.SUCCESS:
                raise Exception(f"Token creation failed: {token_create_receipt.status}")

            token_id = str(token_create_receipt.tokenId)
            logger.info(f"Created NFT collection '{name}' with ID: {token_id}")

            return token_id

        except Exception as e:
            logger.error(f"Failed to create NFT collection: {e}")
            raise Exception(f"Failed to create NFT collection: {str(e)}")

    async def mint_nft(
        self, token_id: str, metadata: str, recipient_account: Optional[str] = None
    ) -> str:
        """
        Mint a new NFT from the collection.
        """
        try:
            client = self._get_client()

            # Convert metadata to bytes
            metadata_bytes = metadata.encode("utf-8")

            # Create mint transaction (corrected API)
            mint_tx = (
                TokenMintTransaction()
                .setTokenId(token_id)
                .addMetadata(metadata_bytes)
                .setMaxTransactionFee(Hbar.fromTinybars(2000000000))  # 20 HBAR
            )

            # Execute transaction
            mint_submit = mint_tx.execute(client)
            mint_receipt = mint_submit.getReceipt(client)

            if mint_receipt.status != Status.SUCCESS:
                raise Exception(f"Minting failed: {mint_receipt.status}")

            # Get the serial number from receipt
            serial_numbers = mint_receipt.serials
            if not serial_numbers or len(serial_numbers) == 0:
                raise Exception("No serial number returned from mint")

            serial_number = str(serial_numbers[0])
            logger.info(f"Minted NFT {token_id}:{serial_number}")

            return serial_number

        except Exception as e:
            logger.error(f"Failed to mint NFT: {e}")
            raise Exception(f"Failed to mint NFT: {str(e)}")

    async def transfer_nft(
        self,
        token_id: str,
        serial_number: str,
        receiver_id: str,
        sender_id: Optional[str] = None,
    ) -> bool:
        """
        Transfer an NFT to a new owner.
        """
        try:
            client = self._get_client()

            # Use operator as sender if not specified
            sender_account_id = (
                AccountId.fromString(sender_id)
                if sender_id
                else self._operator_account_id
            )
            receiver_account_id = AccountId.fromString(receiver_id)

            # First, try to associate token with receiver account
            try:
                associate_tx = (
                    TokenAssociateTransaction()
                    .setAccountId(receiver_account_id)
                    .setTokenIds([token_id])
                    .setMaxTransactionFee(Hbar.fromTinybars(500000000))  # 5 HBAR
                )

                # This might fail if already associated, which is fine
                associate_tx.execute(client)
            except Exception:
                # Token might already be associated
                pass

            # Create transfer transaction (corrected API)
            transfer_tx = (
                TransferTransaction()
                .addNftTransfer(
                    token_id, int(serial_number), sender_account_id, receiver_account_id
                )
                .setMaxTransactionFee(Hbar.fromTinybars(500000000))  # 5 HBAR
            )

            # Execute transaction
            transfer_submit = transfer_tx.execute(client)
            transfer_receipt = transfer_submit.getReceipt(client)

            success = transfer_receipt.status == Status.SUCCESS
            if success:
                logger.info(
                    f"Transferred NFT {token_id}:{serial_number} " f"to {receiver_id}"
                )
            else:
                logger.error(f"Transfer failed: {transfer_receipt.status}")

            return success

        except Exception as e:
            logger.error(f"NFT transfer failed: {e}")
            return False

    async def verify_nft_ownership(
        self, token_id: str, serial_number: str, wallet_address: str
    ) -> bool:
        """
        Verify if a wallet owns a specific NFT using Hedera Mirror Node.
        """
        try:
            # Use Mirror Node API for verification
            url = (
                f"{self.mirror_node_url}/api/v1/tokens/"
                f"{token_id}/nfts/{serial_number}"
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        owner = data.get("account_id", "")
                        return owner == wallet_address
                    else:
                        logger.warning(
                            f"Mirror Node returned status: {response.status}"
                        )
                        return False

        except Exception as e:
            logger.error(f"NFT ownership verification failed: {e}")
            return False

    async def get_nft_info(self, token_id: str, serial_number: str) -> Optional[Dict]:
        """
        Get information about a specific NFT using Mirror Node.
        """
        try:
            url = (
                f"{self.mirror_node_url}/api/v1/tokens/"
                f"{token_id}/nfts/{serial_number}"
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "token_id": token_id,
                            "serial_number": serial_number,
                            "owner": data.get("account_id"),
                            "metadata": data.get("metadata"),
                            "created_at": data.get("created_timestamp"),
                            "modified_at": data.get("modified_timestamp"),
                        }
            return None

        except Exception as e:
            logger.error(f"Failed to get NFT info: {e}")
            return None

    def close(self):
        """Close the Hedera client connection."""
        if self._client:
            self._client.close()
            self._client = None


# Corrected service instance
corrected_hedera_service = CorrectedHederaService()
