from typing import List, Optional
from uuid import uuid4

from fastapi import HTTPException, status

from app.db.repositories.ticket import TicketRepository
from app.db.repositories.event import EventRepository
from app.db.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import (
    TicketCreate,
    TicketPurchaseResponse,
    TicketVerificationRequest,
    TicketVerificationResponse,
)
from app.utils.cache import cache
from app.utils.hedera import hedera_service
from app.utils.qr import qr_service


class TicketService:
    def __init__(
        self, ticket_repository: TicketRepository, event_repository: EventRepository
    ):
        self.ticket_repository = ticket_repository
        self.event_repository = event_repository
        self.cache_prefix = "ticket:"
        self.owner_cache_prefix = "tickets:owner:"

    async def _get_from_cache(self, ticket_id: str) -> Optional[Ticket]:
        cached_ticket = await cache.get(f"{self.cache_prefix}{ticket_id}")
        if cached_ticket:
            return Ticket(**cached_ticket)
        return None

    async def _set_cache(self, ticket: Ticket):
        ticket_dict = ticket.model_dump()
        await cache.set(f"{self.cache_prefix}{ticket.id}", ticket_dict)
        # Invalidate owner's tickets cache
        await cache.delete(f"{self.owner_cache_prefix}{ticket.owner_wallet}")

    async def get(self, ticket_id: str) -> Optional[Ticket]:
        # Try cache first
        cached_ticket = await self._get_from_cache(ticket_id)
        if cached_ticket:
            return cached_ticket

        # If not in cache, get from database
        ticket = await self.ticket_repository.get_by_id(ticket_id)
        if ticket:
            await self._set_cache(ticket)
        return ticket

    async def get_owner_tickets(self, owner_wallet: str) -> List[Ticket]:
        cache_key = f"{self.owner_cache_prefix}{owner_wallet}"
        # Try cache first
        cached_tickets = await cache.get(cache_key)
        if cached_tickets:
            return [Ticket(**ticket) for ticket in cached_tickets]

        # If not in cache, get from database
        tickets = await self.ticket_repository.get_by_owner(owner_wallet)
        if tickets:
            await cache.set(cache_key, [ticket.model_dump() for ticket in tickets])
        return tickets

    async def purchase_ticket(
        self, ticket_create: TicketCreate
    ) -> TicketPurchaseResponse:
        """
        Purchase a ticket for an event.
        """
        # Get event details
        event = await self.event_repository.get_by_id(ticket_create.event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )

        if not event.token_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event tickets not available yet",
            )

        # Step 1: Process Payment FIRST
        from app.services.payment import payment_service

        payment_result = await payment_service.process_payment(
            amount=event.price,
            currency="USD",
            payment_method=ticket_create.payment_method,
            metadata={
                "event_id": event.id,
                "event_name": event.name,
                "buyer_wallet": ticket_create.buyer_wallet,
            },
        )

        if not payment_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Payment failed: {payment_result.get('error', 'Unknown error')}",
            )

        payment_id = payment_result["payment_id"]

        # Step 2: Mint NFT ticket (after successful payment)
        try:
            serial_number = await hedera_service.mint_nft(
                token_id=event.token_id,
                metadata=f"Event: {event.name}, Date: {event.date}",
            )
        except Exception as e:
            # Payment succeeded but NFT minting failed - refund the payment
            await payment_service.refund_payment(payment_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mint NFT ticket: {str(e)}. Payment has been refunded.",
            )

        # Step 3: Transfer NFT to buyer
        try:
            success = await hedera_service.transfer_nft(
                token_id=event.token_id,
                serial_number=serial_number,
                receiver_id=ticket_create.buyer_wallet,
            )

            if not success:
                raise Exception("Transfer returned False")

        except Exception as e:
            # NFT minted but transfer failed - refund the payment
            await payment_service.refund_payment(payment_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to transfer NFT ticket: {str(e)}. Payment has been refunded.",
            )

        # Save ticket in database
        ticket_id = str(uuid4())
        await self.ticket_repository.create(
            {
                "id": ticket_id,
                "event_id": event.id,
                "owner_wallet": ticket_create.buyer_wallet,
                "serial_number": serial_number,
            }
        )

        # Generate QR code
        qr_data = qr_service.generate_ticket_qr(
            token_id=event.token_id,
            serial_number=serial_number,
            owner_wallet=ticket_create.buyer_wallet,
        )

        # Invalidate cache
        await cache.delete(f"{self.owner_cache_prefix}{ticket_create.buyer_wallet}")

        return TicketPurchaseResponse(
            ticket_id=ticket_id,
            token_id=event.token_id,
            serial_number=serial_number,
            qr_data=qr_data,
            payment_id=payment_id,
            amount_paid=event.price,
            currency="USD",
        )

    async def verify_ticket(
        self, verification: TicketVerificationRequest
    ) -> TicketVerificationResponse:
        """
        Verify a ticket's validity and mark it as used.
        """
        # Verify NFT ownership on Hedera
        is_valid = await hedera_service.verify_nft_ownership(
            token_id=verification.token_id,
            serial_number=verification.serial_number,
            wallet_address=verification.wallet_address,
        )

        if not is_valid:
            return TicketVerificationResponse(status="invalid")

        # Get ticket from database
        ticket = await self.ticket_repository.get_by_token_and_serial(
            verification.token_id, verification.serial_number
        )

        if not ticket:
            return TicketVerificationResponse(status="invalid")

        if ticket.status != TicketStatus.ACTIVE:
            return TicketVerificationResponse(
                status="invalid",
                ticket_id=ticket.id,
                event_id=ticket.event_id,
                owner_wallet=ticket.owner_wallet,
            )

        # Mark ticket as used
        updated_ticket = await self.ticket_repository.mark_ticket_used(ticket.id)

        # Invalidate cache
        await self._set_cache(updated_ticket)

        return TicketVerificationResponse(
            status="valid",
            ticket_id=updated_ticket.id,
            event_id=updated_ticket.event_id,
            owner_wallet=updated_ticket.owner_wallet,
        )
