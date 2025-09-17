from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.db.models.ticket import TicketStatus


class TicketBase(BaseModel):
    event_id: str
    owner_wallet: str
    serial_number: str
    status: TicketStatus = TicketStatus.ACTIVE


class TicketCreate(BaseModel):
    event_id: str
    buyer_wallet: str


class TicketUpdate(BaseModel):
    status: TicketStatus


class TicketInDB(TicketBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketResponse(TicketInDB):
    pass


class TicketPurchaseResponse(BaseModel):
    ticket_id: str
    token_id: str
    serial_number: str
    qr_data: str  # base64 encoded QR code


class TicketVerificationRequest(BaseModel):
    token_id: str
    serial_number: str
    wallet_address: str


class TicketVerificationResponse(BaseModel):
    status: str  # "valid" or "invalid"
    ticket_id: Optional[str] = None
    event_id: Optional[str] = None
    owner_wallet: Optional[str] = None
