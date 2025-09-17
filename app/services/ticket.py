from typing import List, Optional, Tuple
from uuid import uuid4

from app.db.repositories.ticket import TicketRepository
from app.db.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.utils.cache import Redis
from app.services.hedera import HederaService
from app.services.qr import QRService


class TicketService:
    def __init__(
        self,
        repository: TicketRepository,
        cache: Redis,
        hedera: HederaService,
        qr: QRService,
    ):
        self.repository = repository
        self.cache = cache
        self.hedera = hedera
        self.qr = qr
        self.cache_prefix = "ticket:"
        self.owner_cache_prefix = "tickets:owner:"

    async def _get_from_cache(self, ticket_id: str) -> Optional[Ticket]:
        cached_ticket = await self.cache.get(f"{self.cache_prefix}{ticket_id}")
        if cached_ticket:
            return Ticket(**cached_ticket)
        return None

    async def _set_cache(self, ticket: Ticket):
        ticket_dict = ticket.model_dump()
        await self.cache.set(f"{self.cache_prefix}{ticket.id}", ticket_dict)
        # Invalidate owner's tickets cache
        await self.cache.delete(f"{self.owner_cache_prefix}{ticket.owner_wallet}")

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
        cached_tickets = await self.cache.get(cache_key)
        if cached_tickets:
            return [Ticket(**ticket) for ticket in cached_tickets]

        # If not in cache, get from database
        tickets = await self.repository.get_by_owner(owner_wallet)
        if tickets:
            await self.cache.set(cache_key, [ticket.model_dump() for ticket in tickets])
        return tickets

    async def purchase_ticket(
        self, token_id: str, buyer_wallet: str, event_id: str
    ) -> Tuple[Ticket, str]:
        # Mint new NFT ticket
        serial_number = await self.hedera.mint_nft(
            token_id=token_id, metadata=f"Ticket for event {event_id}"
        )

        # Transfer NFT to buyer
        transfer_success = await self.hedera.transfer_nft(
            token_id=token_id, serial_number=serial_number, receiver_id=buyer_wallet
        )

        if not transfer_success:
            raise Exception("Failed to transfer NFT ticket to buyer")

        # Create ticket record
        ticket_data = {
            "id": str(uuid4()),
            "event_id": event_id,
            "owner_wallet": buyer_wallet,
            "serial_number": serial_number,
            "status": TicketStatus.ACTIVE,
        }

        ticket = await self.repository.create(ticket_data)
        await self._set_cache(ticket)

        # Generate QR code
        qr_data = self.qr.generate_ticket_qr(
            token_id=token_id, serial_number=serial_number, owner_wallet=buyer_wallet
        )

        return ticket, qr_data

    async def verify_ticket(
        self, token_id: str, serial_number: str, wallet_address: str
    ) -> Tuple[bool, Optional[Ticket]]:
        # Verify NFT ownership
        is_valid = await self.hedera.verify_nft_ownership(
            token_id=token_id,
            serial_number=serial_number,
            wallet_address=wallet_address,
        )

        if not is_valid:
            return False, None

        # Get ticket from database
        ticket = await self.repository.get_by_token_and_serial(token_id, serial_number)
        if not ticket or ticket.status != TicketStatus.ACTIVE:
            return False, ticket

        # Mark ticket as used
        ticket = await self.repository.mark_ticket_used(ticket.id)
        if ticket:
            await self._set_cache(ticket)

        return True, ticket
