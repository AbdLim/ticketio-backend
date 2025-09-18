from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.event import EventRepository
from app.db.repositories.ticket import TicketRepository
from app.db.session import get_session
from app.services.event import EventService
from app.services.ticket import TicketService


# Dependency injection for Event service
async def get_event_service(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> EventService:
    event_repo = EventRepository(db)
    return EventService(event_repo)


# Dependency injection for Ticket service
async def get_ticket_service(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> TicketService:
    ticket_repo = TicketRepository(db)
    return TicketService(ticket_repo)
