from typing import List, Optional, Tuple
from uuid import uuid4

from app.db.repositories.ticket import TicketRepository
from app.db.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.utils.cache import cache
from app.utils.hedera import hedera_service
from app.utils.qr import qr_service


class TicketService:
    def __init__(self, repository: TicketRepository):
        self.repository = repository
        self.cache_prefix = "ticket:"
        self.owner_cache_prefix = "tickets:owner:"

    async def _get_from_cache(self, ticket_id: str) -> Optional[Ticket]:
        cached_ticket = await cache.get(f"{self.cache_prefix}{ticket_id}")
        if cached_ticket:
            return Ticket(**cached_ticket)
        return None

    async def _set_cache(self, ticket: Ticket):
        ticket_dict = ticket.model_dump()
        await cache.set(f"{self.cache_prefix}{ticket.id}", ticket_dict)
        # Invalidate owner's tickets cache
        await cache.delete(f"{self.owner_cache_prefix}{ticket.owner_wallet}")

    async def get(self, ticket_id: str) -> Optional[Ticket]:
        # Try cache first
        cached_ticket = await self._get_from_cache(ticket_id)
        if cached_ticket:
            return cached_ticket

        # If not in cache, get from database
        ticket = await self.repository.get_by_id(ticket_id)
        if ticket:
            await self._set_cache(ticket)
        return ticket

    async def get_owner_tickets(self, owner_wallet: str) -> List[Ticket]:
        cache_key = f"{self.owner_cache_prefix}{owner_wallet}"
        # Try cache first
        cached_tickets = await cache.get(cache_key)
        if cached_tickets:
            return [Ticket(**ticket) for ticket in cached_tickets]

        # If not in cache, get from database
        tickets = await self.repository.get_by_owner(owner_wallet)
        if tickets:
            await cache.set(cache_key, [ticket.model_dump() for ticket in tickets])
        return tickets
