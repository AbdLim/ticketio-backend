"""
Pure HBAR payment service for ticket purchases.
"""

import logging
from typing import Dict
from uuid import uuid4

from fastapi import HTTPException, status

from app.services.hedera_wallet import hedera_wallet_service
from app.utils.hedera import hedera_service
from app.utils.qr import qr_service

logger = logging.getLogger(__name__)


class HbarPaymentService:
    """Handle HBAR payments for ticket purchases."""

    def __init__(self):
        pass

    async def purchase_ticket_with_hbar(
        self,
        event,
        buyer_wallet: str,
        payment_transaction_id: str,
        ticket_repository,
        event_repository,
    ) -> Dict:
        """
        Purchase ticket with HBAR payment.

        Args:
            event: Event object with price_hbar
            buyer_wallet: Buyer's Hedera account ID
            payment_transaction_id: Hedera transaction ID for payment
            ticket_repository: Ticket repository instance
            event_repository: Event repository instance

        Returns:
            Dict with ticket purchase result
        """
        try:
            # Step 1: Verify buyer has sufficient HBAR balance
            balance_check = await hedera_wallet_service.check_sufficient_balance(
                account_id=buyer_wallet, required_hbar=event.price_hbar
            )

            if not balance_check["sufficient"]:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=f"Insufficient HBAR balance. Required: {event.price_hbar} HBAR, "
                    f"Available: {balance_check['current_balance']} HBAR",
                )

            # Step 2: Verify HBAR payment transaction
            payment_verified = await self._verify_hbar_payment(
                transaction_id=payment_transaction_id,
                expected_amount=event.price_hbar,
                recipient_account=event.organizer_id,  # Organizer receives payment
                sender_account=buyer_wallet,
            )

            if not payment_verified["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Payment verification failed: {payment_verified.get('error')}",
                )

            # Step 3: Mint NFT ticket (after verified payment)
            try:
                serial_number = await hedera_service.mint_nft(
                    token_id=event.token_id,
                    metadata=f"Event: {event.name}, Date: {event.date}, "
                    f"Paid: {event.price_hbar} HBAR, TX: {payment_transaction_id}",
                )
            except Exception as e:
                logger.error(f"NFT minting failed after payment: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create ticket NFT: {str(e)}. "
                    f"Payment was successful but ticket creation failed. "
                    f"Contact support with transaction ID: {payment_transaction_id}",
                )

            # Step 4: Transfer NFT to buyer
            try:
                transfer_success = await hedera_service.transfer_nft(
                    token_id=event.token_id,
                    serial_number=serial_number,
                    receiver_id=buyer_wallet,
                )

                if not transfer_success:
                    raise Exception("NFT transfer returned False")

            except Exception as e:
                logger.error(f"NFT transfer failed after minting: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to transfer ticket NFT: {str(e)}. "
                    f"Ticket was created but transfer failed. "
                    f"Contact support with transaction ID: {payment_transaction_id}",
                )

            # Step 5: Save ticket record in database
            ticket_id = str(uuid4())
            await ticket_repository.create(
                {
                    "id": ticket_id,
                    "event_id": event.id,
                    "owner_wallet": buyer_wallet,
                    "serial_number": serial_number,
                    "status": "ACTIVE",
                }
            )

            # Step 6: Generate QR code for ticket
            qr_data = qr_service.generate_ticket_qr(
                token_id=event.token_id,
                serial_number=serial_number,
                owner_wallet=buyer_wallet,
            )

            logger.info(
                f"Ticket purchased successfully: {ticket_id} for {event.price_hbar} HBAR"
            )

            return {
                "success": True,
                "ticket_id": ticket_id,
                "token_id": event.token_id,
                "serial_number": serial_number,
                "qr_data": qr_data,
                "payment_verified": True,
                "hbar_paid": event.price_hbar,
                "transaction_id": payment_transaction_id,
                "buyer_wallet": buyer_wallet,
            }

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Ticket purchase failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ticket purchase failed: {str(e)}",
            )

    async def _verify_hbar_payment(
        self,
        transaction_id: str,
        expected_amount: float,
        recipient_account: str,
        sender_account: str,
    ) -> Dict:
        """
        Verify HBAR payment transaction on Hedera network.

        Args:
            transaction_id: Hedera transaction ID
            expected_amount: Expected HBAR amount
            recipient_account: Expected recipient account
            sender_account: Expected sender account

        Returns:
            Dict with verification result
        """
        try:
            # Use Hedera Mirror Node to verify transaction
            import aiohttp

            # Query transaction from Mirror Node
            mirror_url = f"{hedera_wallet_service.mirror_node_url}/api/v1/transactions/{transaction_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(mirror_url) as response:
                    if response.status == 200:
                        tx_data = await response.json()

                        # Verify transaction details
                        transfers = tx_data.get("transfers", [])

                        # Find HBAR transfer matching our criteria
                        payment_found = False
                        for transfer in transfers:
                            if (
                                transfer.get("account") == recipient_account
                                and transfer.get("amount", 0) > 0
                            ):

                                # Convert tinybars to HBAR
                                received_hbar = transfer["amount"] / 100000000

                                if (
                                    abs(received_hbar - expected_amount) < 0.01
                                ):  # Allow small rounding differences
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
                                "error": f"Payment amount mismatch or recipient incorrect",
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"Transaction not found: {transaction_id}",
                        }

        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            return {"success": False, "error": f"Payment verification error: {str(e)}"}

    async def get_event_price_hbar(self, event_price_hbar: float) -> Dict:
        """
        Get event price information in HBAR.

        Args:
            event_price_hbar: Event price in HBAR

        Returns:
            Dict with price information
        """
        return {
            "price_hbar": event_price_hbar,
            "currency": "HBAR",
            "network": hedera_wallet_service.network,
        }


# Singleton instance
hbar_payment_service = HbarPaymentService()
