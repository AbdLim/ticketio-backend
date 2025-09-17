from typing import Annotated, List
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_current_staff, get_db
from app.db.models import User
from app.db.repositories import EventRepository, TicketRepository
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketPurchaseResponse,
    TicketVerificationRequest,
    TicketVerificationResponse,
)
from app.services.hedera import hedera_service
from app.services.qr import qr_service

router = APIRouter()


@router.post("/tickets/purchase", response_model=TicketPurchaseResponse)
async def purchase_ticket(
    ticket_create: TicketCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Purchase a ticket for an event.
    """
    # Get event details
    event_repo = EventRepository(db)
    event = await event_repo.get_by_id(ticket_create.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    if not event.token_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event tickets not available yet",
        )

    # Mint new NFT ticket
    try:
        serial_number = await hedera_service.mint_nft(
            token_id=event.token_id, metadata=f"Event: {event.name}, Date: {event.date}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mint NFT ticket: {str(e)}",
        )

    # Transfer NFT to buyer
    success = await hedera_service.transfer_nft(
        token_id=event.token_id,
        serial_number=serial_number,
        receiver_id=ticket_create.buyer_wallet,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer NFT ticket",
        )

    # Save ticket in database
    ticket_repo = TicketRepository(db)
    ticket_id = str(uuid4())
    ticket = await ticket_repo.create(
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

    return TicketPurchaseResponse(
        ticket_id=ticket_id,
        token_id=event.token_id,
        serial_number=serial_number,
        qr_data=qr_data,
    )


@router.get("/users/{user_id}/tickets", response_model=List[TicketResponse])
async def list_user_tickets(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    List all tickets owned by a user.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these tickets",
        )

    ticket_repo = TicketRepository(db)
    tickets = await ticket_repo.get_by_owner(current_user.wallet_address)
    return tickets


@router.post("/tickets/verify", response_model=TicketVerificationResponse)
async def verify_ticket(
    verification: TicketVerificationRequest,
    current_user: Annotated[User, Depends(get_current_staff)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
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
    ticket_repo = TicketRepository(db)
    ticket = await ticket_repo.get_by_token_and_serial(
        verification.token_id, verification.serial_number
    )

    if not ticket:
        return TicketVerificationResponse(status="invalid")

    if ticket.status != "active":
        return TicketVerificationResponse(
            status="invalid",
            ticket_id=ticket.id,
            event_id=ticket.event_id,
            owner_wallet=ticket.owner_wallet,
        )

    # Mark ticket as used
    updated_ticket = await ticket_repo.mark_ticket_used(ticket.id)

    return TicketVerificationResponse(
        status="valid",
        ticket_id=updated_ticket.id,
        event_id=updated_ticket.event_id,
        owner_wallet=updated_ticket.owner_wallet,
    )
