from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_organizer
from app.db.models import User
from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventCreatedResponse,
    EventCreateWithPayment,
    EventCreationFeeResponse,
)
from app.services import get_event_service
from app.services.event import EventService

router = APIRouter(tags=["events"])


# Public endpoints
@router.get("/events")
async def list_events(
    event_service: Annotated[EventService, Depends(get_event_service)],
):
    """
    List all active events.
    """
    return await event_service.get_active_events()


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    event_service: Annotated[EventService, Depends(get_event_service)],
):
    """
    Get details of a specific event.
    """
    event = await event_service.get(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return event


# Organizer endpoints
@router.get("/organizer/creation-fee", response_model=EventCreationFeeResponse)
async def get_event_creation_fee():
    """
    Get the current fee required to create an event.
    """
    from app.services.event_payment import event_payment_service

    fee_info = event_payment_service.get_event_creation_fee()
    return EventCreationFeeResponse(
        fee_hbar=fee_info["fee_hbar"],
        platform_wallet=fee_info["platform_wallet"],
        currency=fee_info["currency"],
    )


@router.post("/organizer/events", response_model=EventCreatedResponse)
async def create_event_free(
    event_create: EventCreate,
    current_user: Annotated[User, Depends(get_current_organizer)],
    event_service: Annotated[EventService, Depends(get_event_service)],
):
    """
    Create a new event (FREE - no payment required).
    This is the original endpoint for backward compatibility.
    """
    return await event_service.create_event(event_create, current_user.id)


@router.post("/organizer/events-paid", response_model=EventCreatedResponse)
async def create_event_with_payment(
    event_create: EventCreateWithPayment,
    current_user: Annotated[User, Depends(get_current_organizer)],
    event_service: Annotated[EventService, Depends(get_event_service)],
):
    """
    Create a new event with payment verification (10 HBAR fee).
    Organizer must send HBAR to platform account first.
    """
    from app.services.event_payment import event_payment_service

    # Verify payment before creating event
    payment_verification = await event_payment_service.verify_event_creation_payment(
        organizer_wallet=current_user.wallet_address,
        payment_transaction_id=event_create.payment_transaction_id,
    )

    if not payment_verification["success"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Event creation payment required: {payment_verification.get('error')}",
        )

    # Create the event (convert to regular EventCreate)
    event_data = EventCreate(
        name=event_create.name,
        description=event_create.description,
        location=event_create.location,
        date=event_create.date,
        price_hbar=event_create.price_hbar,
        ticket_supply=event_create.ticket_supply,
    )

    return await event_service.create_event(event_data, current_user.id)


@router.get("/organizer/events", response_model=List[EventResponse])
async def list_organizer_events(
    current_user: Annotated[User, Depends(get_current_organizer)],
    event_service: Annotated[EventService, Depends(get_event_service)],
):
    """
    List all events created by the current organizer.
    """
    return await event_service.get_organizer_events(current_user.id)
