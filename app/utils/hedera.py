from typing import Tuple
from hiero import (
    Client,
    TokenCreateTransaction,
    TokenMintTransaction,
    TokenType,
    TransferTransaction,
)

from app.core.config import Settings

settings = Settings()


class HederaService:
    def __init__(self):
        self.client = Client(
            network=settings.HEDERA_NETWORK,
            operator_id=settings.HEDERA_OPERATOR_ID,
            operator_key=settings.HEDERA_OPERATOR_KEY,
        )

    async def create_nft_collection(
        self, name: str, symbol: str, supply: int, metadata_uri: str
    ) -> str:
        """
        Create a new NFT collection for an event.

        Args:
            name: Name of the NFT collection
            symbol: Symbol for the NFT collection
            supply: Maximum supply of NFTs
            metadata_uri: URI to the token metadata

        Returns:
            str: The Hedera token ID
        """
        transaction = (
            TokenCreateTransaction()
            .set_token_type(TokenType.NON_FUNGIBLE_UNIQUE)
            .set_token_name(name)
            .set_token_symbol(symbol)
            .set_initial_supply(0)
            .set_max_supply(supply)
            .set_treasury(self.client.operator_id)
            .set_supply_type(True)  # Enable supply control
            .set_metadata_uri(metadata_uri)
        )

        response = await self.client.execute_transaction(transaction)
        token_id = response.token_id
        return str(token_id)

    async def mint_nft(self, token_id: str, metadata: str) -> str:
        """
        Mint a new NFT from the collection.

        Args:
            token_id: The Hedera token ID of the collection
            metadata: Metadata for this specific NFT

        Returns:
            str: The serial number of the minted NFT
        """
        transaction = (
            TokenMintTransaction()
            .set_token_id(token_id)
            .set_metadata(metadata.encode())
        )

        response = await self.client.execute_transaction(transaction)
        return str(response.serial_number)

    async def transfer_nft(
        self, token_id: str, serial_number: str, receiver_id: str
    ) -> bool:
        """
        Transfer an NFT to a new owner.

        Args:
            token_id: The Hedera token ID
            serial_number: The NFT's serial number
            receiver_id: The receiver's Hedera account ID

        Returns:
            bool: True if transfer was successful
        """
        transaction = TransferTransaction().add_nft_transfer(
            token_id=token_id,
            serial_number=int(serial_number),
            sender=self.client.operator_id,
            receiver=receiver_id,
        )

        try:
            await self.client.execute_transaction(transaction)
            return True
        except Exception:
            return False

    async def verify_nft_ownership(
        self, token_id: str, serial_number: str, wallet_address: str
    ) -> bool:
        """
        Verify if a wallet owns a specific NFT.

        Args:
            token_id: The Hedera token ID
            serial_number: The NFT's serial number
            wallet_address: The wallet address to check

        Returns:
            bool: True if the wallet owns the NFT
        """
        try:
            # Query the Mirror Node API
            nft_info = await self.client.get_nft_info(token_id, serial_number)
            return nft_info.owner == wallet_address
        except Exception:
            return False

    async def get_nft_info(self, token_id: str, serial_number: str) -> dict:
        """
        Get information about a specific NFT.

        Args:
            token_id: The Hedera token ID
            serial_number: The NFT's serial number

        Returns:
            dict: NFT information including owner, metadata, etc.
        """
        try:
            nft_info = await self.client.get_nft_info(token_id, serial_number)
            return {
                "owner": nft_info.owner,
                "metadata": nft_info.metadata.decode(),
                "created_at": nft_info.created_timestamp,
                "modified_at": nft_info.modified_timestamp,
            }
        except Exception as e:
            raise Exception(f"Failed to get NFT info: {str(e)}")


# Create a singleton instance
hedera_service = HederaService()
