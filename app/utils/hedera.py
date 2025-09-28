from typing import Dict, Optional, List
import asyncio
import aiohttp
import logging
from datetime import datetime

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


class HederaService:
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
                # Parse operator credentials
                self._operator_account_id = AccountId.from_string(self.operator_id)
                self._operator_private_key = PrivateKey.from_string(self.operator_key)

                # Create client based on network
                if self.network.lower() == "testnet":
                    self._client = Client.for_testnet()
                elif self.network.lower() == "mainnet":
                    self._client = Client.for_mainnet()
                else:
                    # Default to testnet for development
                    self._client = Client.for_testnet()

                # Set operator
                self._client.set_operator(
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

        Args:
            name: Name of the NFT collection
            symbol: Symbol for the NFT collection
            supply: Maximum supply of NFTs (0 for unlimited)
            metadata_uri: Base URI for token metadata
            treasury_account: Treasury account ID (defaults to operator)

        Returns:
            str: The Hedera token ID (e.g., "0.0.123456")
        """
        try:
            client = self._get_client()

            # Use operator account as treasury if not specified
            treasury_id = (
                AccountId.from_string(treasury_account)
                if treasury_account
                else self._operator_account_id
            )

            # Create NFT token
            token_create_tx = (
                TokenCreateTransaction()
                .set_token_name(name)
                .set_token_symbol(symbol)
                .set_token_type(TokenType.NON_FUNGIBLE_UNIQUE)
                .set_decimals(0)
                .set_initial_supply(0)
                .set_treasury_account_id(treasury_id)
                .set_supply_type(
                    TokenSupplyType.FINITE if supply > 0 else TokenSupplyType.INFINITE
                )
                .set_max_supply(supply if supply > 0 else None)
                .set_supply_key(self._operator_private_key)
                .set_admin_key(self._operator_private_key)
                .set_freeze_default(False)
                .set_max_transaction_fee(Hbar(30))
            )

            # Execute transaction
            token_create_submit = await asyncio.to_thread(
                token_create_tx.execute, client
            )
            token_create_receipt = await asyncio.to_thread(
                token_create_submit.get_receipt, client
            )

            if token_create_receipt.status != Status.SUCCESS:
                raise Exception(f"Token creation failed: {token_create_receipt.status}")

            token_id = str(token_create_receipt.token_id)
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

        Args:
            token_id: The Hedera token ID
            metadata: Metadata for this specific NFT (base64 encoded)
            recipient_account: Account to mint to (defaults to treasury)

        Returns:
            str: The serial number of the minted NFT
        """
        try:
            client = self._get_client()

            # Convert metadata to bytes
            metadata_bytes = metadata.encode("utf-8")

            # Create mint transaction
            mint_tx = (
                TokenMintTransaction()
                .set_token_id(token_id)
                .add_metadata(metadata_bytes)
                .set_max_transaction_fee(Hbar(20))
            )

            # Execute transaction
            mint_submit = await asyncio.to_thread(mint_tx.execute, client)
            mint_receipt = await asyncio.to_thread(mint_submit.get_receipt, client)

            if mint_receipt.status != Status.SUCCESS:
                raise Exception(f"Minting failed: {mint_receipt.status}")

            # Get the serial number from receipt
            serial_numbers = mint_receipt.serial_numbers
            if not serial_numbers:
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

        Args:
            token_id: The Hedera token ID
            serial_number: The NFT serial number
            receiver_id: The receiver's account ID
            sender_id: The sender's account ID (defaults to operator)

        Returns:
            bool: True if transfer was successful
        """
        try:
            client = self._get_client()

            # Use operator as sender if not specified
            sender_account_id = (
                AccountId.from_string(sender_id)
                if sender_id
                else self._operator_account_id
            )
            receiver_account_id = AccountId.from_string(receiver_id)

            # First, associate token with receiver account if needed
            try:
                associate_tx = (
                    TokenAssociateTransaction()
                    .set_account_id(receiver_account_id)
                    .add_token_id(token_id)
                    .set_max_transaction_fee(Hbar(5))
                )

                # This might fail if already associated, which is fine
                await asyncio.to_thread(associate_tx.execute, client)
            except Exception:
                # Token might already be associated
                pass

            # Create transfer transaction
            transfer_tx = (
                TransferTransaction()
                .add_nft_transfer(
                    token_id, int(serial_number), sender_account_id, receiver_account_id
                )
                .set_max_transaction_fee(Hbar(5))
            )

            # Execute transaction
            transfer_submit = await asyncio.to_thread(transfer_tx.execute, client)
            transfer_receipt = await asyncio.to_thread(
                transfer_submit.get_receipt, client
            )

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

        Args:
            token_id: The Hedera token ID
            serial_number: The NFT serial number
            wallet_address: The wallet address to verify

        Returns:
            bool: True if the wallet owns the NFT
        """
        try:
            # First try using the Hedera SDK
            client = self._get_client()

            nft_info_query = (
                TokenNftInfoQuery()
                .set_token_id(token_id)
                .set_serial_number(int(serial_number))
            )

            nft_info = await asyncio.to_thread(nft_info_query.execute, client)

            if nft_info and len(nft_info) > 0:
                owner_account_id = str(nft_info[0].account_id)
                return owner_account_id == wallet_address

        except Exception as e:
            logger.warning(f"SDK ownership check failed: {e}")

        # Fallback to Mirror Node API
        try:
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
        Get information about a specific NFT.

        Args:
            token_id: The Hedera token ID
            serial_number: The NFT serial number

        Returns:
            Optional[Dict]: NFT information including owner and metadata
        """
        try:
            # Try SDK first
            client = self._get_client()

            nft_info_query = (
                TokenNftInfoQuery()
                .set_token_id(token_id)
                .set_serial_number(int(serial_number))
            )

            nft_info = await asyncio.to_thread(nft_info_query.execute, client)

            if nft_info and len(nft_info) > 0:
                info = nft_info[0]
                return {
                    "token_id": token_id,
                    "serial_number": serial_number,
                    "owner": str(info.account_id),
                    "metadata": (
                        info.metadata.decode("utf-8") if info.metadata else None
                    ),
                    "created_at": str(info.creation_time),
                }

        except Exception as e:
            logger.warning(f"SDK NFT info query failed: {e}")

        # Fallback to Mirror Node
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

    async def get_account_nfts(self, account_id: str) -> List[Dict]:
        """
        Get all NFTs owned by an account.

        Args:
            account_id: The Hedera account ID

        Returns:
            List[Dict]: List of NFTs owned by the account
        """
        try:
            url = f"{self.mirror_node_url}/api/v1/accounts/" f"{account_id}/nfts"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("nfts", [])
            return []

        except Exception as e:
            logger.error(f"Failed to get account NFTs: {e}")
            return []

    async def get_token_info(self, token_id: str) -> Optional[Dict]:
        """
        Get information about a token.

        Args:
            token_id: The Hedera token ID

        Returns:
            Optional[Dict]: Token information
        """
        try:
            client = self._get_client()

            token_info_query = TokenInfoQuery().set_token_id(token_id)
            token_info = await asyncio.to_thread(token_info_query.execute, client)

            return {
                "token_id": str(token_info.token_id),
                "name": token_info.name,
                "symbol": token_info.symbol,
                "treasury_account": str(token_info.treasury_account_id),
                "supply_type": str(token_info.supply_type),
                "max_supply": token_info.max_supply,
                "total_supply": token_info.total_supply,
            }

        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            return None

    def close(self):
        """Close the Hedera client connection."""
        if self._client:
            self._client.close()
            self._client = None


# Create a singleton instance
hedera_service = HederaService()
