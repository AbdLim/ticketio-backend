from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: str
    date: datetime
    price: float


class EventCreate(EventBase):
    ticket_supply: int


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[datetime] = None
    price: Optional[float] = None


class EventInDB(EventBase):
    id: str
    organizer_id: str
    token_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EventResponse(EventInDB):
    pass


class EventCreatedResponse(BaseModel):
    event_id: str
    token_id: str
