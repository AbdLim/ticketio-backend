from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_organizer
from app.db.models import User
from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventCreatedResponse,
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
@router.post("/organizer/events", response_model=EventCreatedResponse)
async def create_event(
    event_create: EventCreate,
    current_user: Annotated[User, Depends(get_current_organizer)],
    event_service: Annotated[EventService, Depends(get_event_service)],
):
    """
    Create a new event and mint NFT collection.
    """
    return await event_service.create_event(event_create, current_user.id)


@router.get("/organizer/events", response_model=List[EventResponse])
async def list_organizer_events(
    current_user: Annotated[User, Depends(get_current_organizer)],
    event_service: Annotated[EventService, Depends(get_event_service)],
):
    """
    List all events created by the current organizer.
    """
    return await event_service.get_organizer_events(current_user.id)
