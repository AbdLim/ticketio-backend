"""
Hedera wallet service for balance checking and wallet operations.
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from decimal import Decimal

from hedera import (
    Client,
    AccountId,
    PrivateKey,
    AccountBalanceQuery,
    AccountInfoQuery,
    Hbar,
)

from app.core.config import Settings

settings = Settings()
logger = logging.getLogger(__name__)


class HederaWalletService:
    """Service for Hedera wallet operations and balance checking."""

    def __init__(self):
        self.network = settings.HEDERA_NETWORK
        self.mirror_node_url = settings.HEDERA_MIRROR_NODE_URL
        self._client = None

        # Exchange rates cache (in production, use Redis with TTL)
        self._exchange_rates = {}
        self._rates_last_updated = None

    def _get_client(self) -> Client:
        """Get Hedera client for queries."""
        if self._client is None:
            if self.network.lower() == "testnet":
                self._client = Client.forTestnet()
            else:
                self._client = Client.forMainnet()
        return self._client

    async def get_account_balance(self, account_id: str) -> Dict:
        """
        Get HBAR balance for a Hedera account.

        Args:
            account_id: Hedera account ID (e.g., "0.0.123456")

        Returns:
            Dict with balance information
        """
        try:
            client = self._get_client()

            # Parse account ID
            hedera_account_id = AccountId.fromString(account_id)

            # Query balance
            balance_query = AccountBalanceQuery().setAccountId(hedera_account_id)
            balance = balance_query.execute(client)

            # Get HBAR balance
            hbar_balance = balance.hbars.toTinybars() / 100000000  # Convert to HBAR

            logger.info(f"Retrieved balance for {account_id}: {hbar_balance} HBAR")

            return {
                "account_id": account_id,
                "hbar_balance": float(hbar_balance),
                "last_updated": datetime.utcnow(),
                "success": True,
            }

        except Exception as e:
            logger.error(f"Failed to get balance for {account_id}: {e}")
            return {
                "account_id": account_id,
                "hbar_balance": 0.0,
                "last_updated": datetime.utcnow(),
                "success": False,
                "error": str(e),
            }

    async def get_account_info(self, account_id: str) -> Dict:
        """
        Get detailed account information.

        Args:
            account_id: Hedera account ID

        Returns:
            Dict with account details
        """
        try:
            client = self._get_client()

            # We need an operator to query account info
            # Use the system operator for queries
            if settings.HEDERA_OPERATOR_ID and settings.HEDERA_OPERATOR_KEY:
                operator_id = AccountId.fromString(settings.HEDERA_OPERATOR_ID)
                operator_key = PrivateKey.fromString(settings.HEDERA_OPERATOR_KEY)
                client.setOperator(operator_id, operator_key)

            hedera_account_id = AccountId.fromString(account_id)

            # Query account info
            account_info_query = AccountInfoQuery().setAccountId(hedera_account_id)
            account_info = account_info_query.execute(client)

            return {
                "account_id": account_id,
                "balance": account_info.balance.toTinybars() / 100000000,
                "key": str(account_info.key),
                "auto_renew_period": (
                    account_info.autoRenewPeriod.seconds
                    if account_info.autoRenewPeriod
                    else None
                ),
                "expiration_time": (
                    str(account_info.expirationTime)
                    if account_info.expirationTime
                    else None
                ),
                "success": True,
            }

        except Exception as e:
            logger.error(f"Failed to get account info for {account_id}: {e}")
            return {"account_id": account_id, "success": False, "error": str(e)}

    async def create_new_hedera_account(
        self, initial_balance_hbar: float = 10.0
    ) -> Dict:
        """
        Create a new Hedera account with initial balance.

        Args:
            initial_balance_hbar: Initial HBAR balance for the account

        Returns:
            Dict with new account details
        """
        try:
            from hedera import AccountCreateTransaction, Hbar

            # Generate new key pair
            new_private_key = PrivateKey.generateED25519()
            new_public_key = new_private_key.getPublicKey()

            # Get client with operator (needed to create accounts)
            client = self._get_client()

            if not settings.HEDERA_OPERATOR_ID or not settings.HEDERA_OPERATOR_KEY:
                raise Exception("Operator credentials required to create accounts")

            operator_id = AccountId.fromString(settings.HEDERA_OPERATOR_ID)
            operator_key = PrivateKey.fromString(settings.HEDERA_OPERATOR_KEY)
            client.setOperator(operator_id, operator_key)

            # Create account transaction
            account_create_tx = (
                AccountCreateTransaction()
                .setKey(new_public_key)
                .setInitialBalance(
                    Hbar.fromTinybars(int(initial_balance_hbar * 100000000))
                )
                .setMaxTransactionFee(Hbar.fromTinybars(200000000))  # 2 HBAR fee
            )

            # Execute transaction
            response = account_create_tx.execute(client)
            receipt = response.getReceipt(client)

            if receipt.status.toString() == "SUCCESS":
                new_account_id = receipt.accountId.toString()

                logger.info(f"Created new Hedera account: {new_account_id}")

                return {
                    "success": True,
                    "account_id": new_account_id,
                    "private_key": new_private_key.toString(),
                    "public_key": new_public_key.toString(),
                    "initial_balance": initial_balance_hbar,
                    "created_at": datetime.utcnow(),
                }
            else:
                raise Exception(f"Account creation failed: {receipt.status}")

        except Exception as e:
            logger.error(f"Failed to create Hedera account: {e}")
            return {"success": False, "error": str(e)}

    async def check_sufficient_balance(
        self, account_id: str, required_hbar: float
    ) -> Dict:
        """
        Check if account has sufficient HBAR balance.

        Args:
            account_id: Hedera account ID
            required_hbar: Required HBAR amount

        Returns:
            Dict with balance check result
        """
        try:
            balance_info = await self.get_account_balance(account_id)

            if not balance_info["success"]:
                return {
                    "sufficient": False,
                    "error": balance_info.get("error", "Failed to check balance"),
                }

            current_balance = balance_info["hbar_balance"]
            sufficient = current_balance >= required_hbar

            return {
                "sufficient": sufficient,
                "current_balance": current_balance,
                "required_balance": required_hbar,
                "difference": current_balance - required_hbar,
            }

        except Exception as e:
            logger.error(f"Balance check failed: {e}")
            return {"sufficient": False, "error": str(e)}

    def close(self):
        """Close the client connection."""
        if self._client:
            self._client.close()
            self._client = None


# Singleton instance
hedera_wallet_service = HederaWalletService()
