from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: str
    date: datetime
    price_hbar: float  # Price in HBAR only


class EventCreate(EventBase):
    ticket_supply: int


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[datetime] = None
    price_hbar: Optional[float] = None


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


class EventCreateWithPayment(BaseModel):
    name: str
    description: Optional[str] = None
    location: str
    date: datetime
    price_hbar: float
    ticket_supply: int
    payment_transaction_id: str  # Payment for event creation fee


class EventCreationFeeResponse(BaseModel):
    fee_hbar: float
    platform_wallet: str
    currency: str = "HBAR"
