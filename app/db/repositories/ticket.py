from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Ticket, TicketStatus
from app.db.repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, db: AsyncSession):
        super().__init__(Ticket, db)

    async def get_by_event(self, event_id: str) -> List[Ticket]:
        """
        Get all tickets for a specific event.
        """
        query = select(Ticket).where(Ticket.event_id == event_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_owner(self, owner_wallet: str) -> List[Ticket]:
        """
        Get all tickets owned by a specific wallet address.
        """
        query = select(Ticket).where(Ticket.owner_wallet == owner_wallet)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_token_and_serial(
        self, token_id: str, serial_number: str
    ) -> Optional[Ticket]:
        """
        Get a ticket by its Hedera token ID and serial number.
        """
        from app.db.models import Event

        query = (
            select(Ticket)
            .join(Event)
            .where(Event.token_id == token_id, Ticket.serial_number == serial_number)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def mark_ticket_used(self, ticket_id: str) -> Optional[Ticket]:
        """
        Mark a ticket as used.
        """
        ticket = await self.get_by_id(ticket_id)
        if ticket:
            ticket.status = TicketStatus.USED
            await self.db.commit()
        return ticket
