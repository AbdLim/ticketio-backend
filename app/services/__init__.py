from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.event import EventRepository
from app.db.repositories.ticket import TicketRepository
from app.services.event import EventService
from app.services.ticket import TicketService
from app.services.hedera import HederaService
from app.services.qr import QRService
from app.utils.cache import Redis
from app.api.deps import get_db

# Initialize core services
hedera_service = HederaService()
qr_service = QRService()


# Dependency injection for Event service
async def get_event_service(
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(Redis),
) -> EventService:
    event_repo = EventRepository(db)
    return EventService(event_repo, cache, hedera_service)


# Dependency injection for Ticket service
async def get_ticket_service(
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(Redis),
) -> TicketService:
    ticket_repo = TicketRepository(db)
    return TicketService(ticket_repo, cache, hedera_service, qr_service)
