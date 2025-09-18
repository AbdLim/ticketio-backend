from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from app.db.repositories.event import EventRepository
from app.db.models.event import Event
from app.schemas.event import EventCreate, EventUpdate
from app.utils.cache import cache
from app.utils.hedera import hedera_service


class EventService:
    def __init__(self, repository: EventRepository):
        self.repository = repository
        self.cache_prefix = "event:"
        self.list_cache_key = "events:all"

    async def _get_from_cache(self, event_id: str) -> Optional[Event]:
        cached_event = await cache.get(f"{self.cache_prefix}{event_id}")
        if cached_event:
            # Convert string dates back to datetime objects
            if cached_event.get("date"):
                cached_event["date"] = datetime.fromisoformat(cached_event["date"])
            if cached_event.get("created_at"):
                cached_event["created_at"] = datetime.fromisoformat(
                    cached_event["created_at"]
                )
            if cached_event.get("updated_at"):
                cached_event["updated_at"] = datetime.fromisoformat(
                    cached_event["updated_at"]
                )
            if cached_event.get("deleted_at"):
                cached_event["deleted_at"] = datetime.fromisoformat(
                    cached_event["deleted_at"]
                )
            return Event(**cached_event)
        return None

    async def _set_cache(self, event: Event):
        event_dict = event.model_dump()
        # Convert datetime objects to ISO format strings for JSON serialization
        if event_dict.get("date"):
            event_dict["date"] = event_dict["date"].isoformat()
        if event_dict.get("created_at"):
            event_dict["created_at"] = event_dict["created_at"].isoformat()
        if event_dict.get("updated_at"):
            event_dict["updated_at"] = event_dict["updated_at"].isoformat()
        if event_dict.get("deleted_at"):
            event_dict["deleted_at"] = event_dict["deleted_at"].isoformat()
        await cache.set(f"{self.cache_prefix}{event.id}", event_dict)
        await cache.delete(self.list_cache_key)

    async def get(self, event_id: str) -> Optional[Event]:
        # Try cache first
        cached_event = await self._get_from_cache(event_id)
        if cached_event:
            return cached_event

        # If not in cache, get from database
        event = await self.repository.get_by_id(event_id)
        if event:
            await self._set_cache(event)
        return event

    async def get_active_events(self) -> List[Event]:
        # Try cache first
        cached_events = await cache.get(self.list_cache_key)
        if cached_events:
            return [Event(**event) for event in cached_events]

        # If not in cache, get from database
        events = await self.repository.get_active_events()
        if events:
            await cache.set(
                self.list_cache_key, [event.model_dump() for event in events]
            )
        return events

    async def get_organizer_events(self, organizer_id: str) -> List[Event]:
        cache_key = f"events:organizer:{organizer_id}"
        # Try cache first
        cached_events = await cache.get(cache_key)
        if cached_events:
            return [Event(**event) for event in cached_events]

        # If not in cache, get from database
        events = await self.repository.get_by_organizer(organizer_id)
        if events:
            await cache.set(cache_key, [event.model_dump() for event in events])
        return events
