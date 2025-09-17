from enum import Enum
from sqlmodel import Field
from sqlalchemy import Column, Enum as SQLAlchemyEnum

from app.db.base import BaseModel


class TicketStatus(str, Enum):
    ACTIVE = "active"
    USED = "used"


class Ticket(BaseModel, table=True):
    __tablename__ = "tickets"

    event_id: str = Field(foreign_key="events.id")
    owner_wallet: str = Field(index=True)  # Hedera wallet address
    serial_number: str = Field()  # Hedera NFT serial number
    status: TicketStatus = Field(
        sa_column=Column(SQLAlchemyEnum(TicketStatus)), default=TicketStatus.ACTIVE
    )
