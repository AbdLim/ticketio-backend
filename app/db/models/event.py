from typing import Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import Field
from sqlalchemy import Column, DateTime, Text, Numeric

from app.db.base import BaseModel


class Event(BaseModel, table=True):
    __tablename__ = "events"

    organizer_id: str = Field(foreign_key="users.id")
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    location: str = Field()
    date: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    token_id: Optional[str] = Field(
        default=None, index=True, unique=True
    )  # Hedera NFT token ID
    metadata_uri: Optional[str] = Field(
        default=None
    )  # IPFS or HTTP URI for event metadata
