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
from app.services import get_ticket_service
from app.services.ticket import TicketService

router = APIRouter(prefix="/tickets", tags=["ticket"])


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
