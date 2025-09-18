from typing import Annotated, List
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organizer
from app.db.models import User
from app.db.repositories.event import EventRepository
from app.db.session import get_session
from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventCreatedResponse,
)
from app.services import get_event_service
from app.services.event import EventService
from app.utils.hedera import hedera_service

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
@router.post("/organizer/events", response_model=EventCreatedResponse)
async def create_event(
    event_create: EventCreate,
    current_user: Annotated[User, Depends(get_current_organizer)],
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Create a new event and mint NFT collection.
    """
    # Create event with UUID
    event_dict = event_create.model_dump()
    event_id = str(uuid4())
    event_dict["id"] = event_id
    event_dict["organizer_id"] = current_user.id

    # Create NFT collection
    token_id = await hedera_service.create_nft_collection(
        name=event_create.name,
        symbol="TICKET",  # You might want to make this configurable
        supply=event_create.ticket_supply,
        metadata_uri=f"https://api.ticketio.com/events/{event_id}",  # Replace with your metadata URI
    )

    event_dict["token_id"] = token_id

    # Save event to database
    event_repo = EventRepository(db)
    await event_repo.create(event_dict)

    return EventCreatedResponse(event_id=event_id, token_id=token_id)


@router.get("/organizer/events", response_model=List[EventResponse])
async def list_organizer_events(
    current_user: Annotated[User, Depends(get_current_organizer)],
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    List all events created by the current organizer.
    """
    event_repo = EventRepository(db)
    events = await event_repo.get_by_organizer(current_user.id)
    return events
