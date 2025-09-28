"""
Event creation payment service for organizers.
"""

import logging
from typing import Dict

from fastapi import HTTPException, status

from app.services.hedera_wallet import hedera_wallet_service

logger = logging.getLogger(__name__)


class EventPaymentService:
    """Handle HBAR payments for event creation."""

    def __init__(self):
        # Platform configuration
        self.EVENT_CREATION_FEE = 10.0  # HBAR fee to create an event
        self.PLATFORM_WALLET = "0.0.platform_account"  # Platform's Hedera account

    async def verify_event_creation_payment(
        self, organizer_wallet: str, payment_transaction_id: str
    ) -> Dict:
        """
        Verify organizer paid the event creation fee.

        Args:
            organizer_wallet: Organizer's Hedera account
            payment_transaction_id: Transaction ID for the payment

        Returns:
            Dict with verification result
        """
        try:
            # Step 1: Check organizer has sufficient balance
            balance_check = await hedera_wallet_service.check_sufficient_balance(
                account_id=organizer_wallet, required_hbar=self.EVENT_CREATION_FEE
            )

            if not balance_check["sufficient"]:
                return {
                    "success": False,
                    "error": f"Insufficient HBAR balance. Required: {self.EVENT_CREATION_FEE} HBAR, "
                    f"Available: {balance_check['current_balance']} HBAR",
                }

            # Step 2: Verify payment transaction
            payment_verified = await self._verify_platform_payment(
                transaction_id=payment_transaction_id,
                expected_amount=self.EVENT_CREATION_FEE,
                sender_account=organizer_wallet,
            )

            if not payment_verified["success"]:
                return {
                    "success": False,
                    "error": f"Payment verification failed: {payment_verified.get('error')}",
                }

            logger.info(
                f"Event creation payment verified: {organizer_wallet} paid {self.EVENT_CREATION_FEE} HBAR"
            )

            return {
                "success": True,
                "amount_paid": self.EVENT_CREATION_FEE,
                "transaction_id": payment_transaction_id,
                "organizer_wallet": organizer_wallet,
            }

        except Exception as e:
            logger.error(f"Event creation payment verification failed: {e}")
            return {"success": False, "error": str(e)}

    async def _verify_platform_payment(
        self, transaction_id: str, expected_amount: float, sender_account: str
    ) -> Dict:
        """
        Verify HBAR payment to platform account.
        """
        try:
            import aiohttp

            # Query transaction from Mirror Node
            mirror_url = f"{hedera_wallet_service.mirror_node_url}/api/v1/transactions/{transaction_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(mirror_url) as response:
                    if response.status == 200:
                        tx_data = await response.json()

                        # Verify transaction details
                        transfers = tx_data.get("transfers", [])

                        # Find HBAR transfer to platform account
                        payment_found = False
                        for transfer in transfers:
                            if (
                                transfer.get("account") == self.PLATFORM_WALLET
                                and transfer.get("amount", 0) > 0
                            ):

                                # Convert tinybars to HBAR
                                received_hbar = transfer["amount"] / 100000000

                                if abs(received_hbar - expected_amount) < 0.01:
                                    payment_found = True
                                    break

                        if payment_found:
                            return {
                                "success": True,
                                "transaction_id": transaction_id,
                                "amount_hbar": expected_amount,
                                "verified": True,
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"Payment not found or amount incorrect",
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"Transaction not found: {transaction_id}",
                        }

        except Exception as e:
            logger.error(f"Platform payment verification failed: {e}")
            return {"success": False, "error": f"Payment verification error: {str(e)}"}

    def get_event_creation_fee(self) -> Dict:
        """Get the current event creation fee."""
        return {
            "fee_hbar": self.EVENT_CREATION_FEE,
            "platform_wallet": self.PLATFORM_WALLET,
            "currency": "HBAR",
        }


# Singleton instance
event_payment_service = EventPaymentService()
