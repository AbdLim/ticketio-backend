from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_active_user, get_current_staff
from app.db.models import User
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketPurchaseResponse,
    TicketVerificationRequest,
    TicketVerificationResponse,
)
from pydantic import BaseModel
from app.services import get_ticket_service
from app.services.ticket import TicketService

router = APIRouter(prefix="/tickets", tags=["ticket"])


class HbarTicketPurchase(BaseModel):
    event_id: str
    buyer_wallet: str
    payment_transaction_id: str  # Hedera transaction ID


@router.post("/purchase", response_model=TicketPurchaseResponse)
async def purchase_ticket(
    ticket_create: TicketCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    ticket_service: Annotated[TicketService, Depends(get_ticket_service)],
):
    """
    Purchase a ticket for an event.
    """
    return await ticket_service.purchase_ticket(ticket_create)


@router.get("/users/{user_id}/tickets", response_model=List[TicketResponse])
async def list_user_tickets(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    ticket_service: Annotated[TicketService, Depends(get_ticket_service)],
):
    """
    List all tickets owned by a user.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these tickets",
        )

    return await ticket_service.get_owner_tickets(current_user.wallet_address)


@router.post("/purchase-hbar", response_model=TicketPurchaseResponse)
async def purchase_ticket_with_hbar(
    purchase_data: HbarTicketPurchase,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Purchase a ticket with HBAR payment.
    User must send HBAR to organizer first, then provide transaction ID.
    """
    from app.services.hbar_payment import hbar_payment_service
    from app.db.repositories.event import EventRepository
    from app.db.repositories.ticket import TicketRepository
    from app.db.session import get_session

    # Get database session
    async def get_db_session():
        async for session in get_session():
            return session

    db = await get_db_session()

    try:
        # Get event details
        event_repo = EventRepository(db)
        event = await event_repo.get_by_id(purchase_data.event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )

        if not event.token_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event tickets not available yet",
            )

        # Process HBAR payment and create ticket
        ticket_repo = TicketRepository(db)

        result = await hbar_payment_service.purchase_ticket_with_hbar(
            event=event,
            buyer_wallet=purchase_data.buyer_wallet,
            payment_transaction_id=purchase_data.payment_transaction_id,
            ticket_repository=ticket_repo,
            event_repository=event_repo,
        )

        return TicketPurchaseResponse(
            ticket_id=result["ticket_id"],
            token_id=result["token_id"],
            serial_number=result["serial_number"],
            qr_data=result["qr_data"],
            payment_id=result["transaction_id"],
            amount_paid=result["hbar_paid"],
            currency="HBAR",
        )

    finally:
        await db.close()


@router.post("/verify", response_model=TicketVerificationResponse)
async def verify_ticket(
    verification: TicketVerificationRequest,
    current_user: Annotated[User, Depends(get_current_staff)],
    ticket_service: Annotated[TicketService, Depends(get_ticket_service)],
):
    """
    Verify a ticket's validity and mark it as used.
    """
    return await ticket_service.verify_ticket(verification)
