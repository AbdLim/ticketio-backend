from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event
from app.db.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Event)

    async def get_by_organizer(self, organizer_id: str) -> List[Event]:
        """
        Get all events created by a specific organizer.
        """
        query = select(Event).where(Event.organizer_id == organizer_id)
        result = await self.session.exec(query)
        return result.all()

    async def get_by_token_id(self, token_id: str) -> Optional[Event]:
        """
        Get an event by its Hedera token ID.
        """
        query = select(Event).where(Event.token_id == token_id)
        result = await self.session.exec(query)
        return result.first()

    async def get_active_events(self) -> List[Event]:
        """
        Get all active events (events with future dates).
        """
        from datetime import datetime

        query = select(Event).where(Event.date > datetime.utcnow())
        result = await self.session.exec(query)
        return result.all()
