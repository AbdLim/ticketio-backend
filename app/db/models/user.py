from typing import Optional
from enum import Enum
from sqlmodel import Field
from sqlalchemy import Column, Enum as SQLAlchemyEnum

from app.db.base import BaseModel


class UserRole(str, Enum):
    ATTENDEE = "attendee"
    ORGANIZER = "organizer"
    STAFF = "staff"


class User(BaseModel, table=True):
    __tablename__ = "users"

    name: Optional[str] = Field(default=None, unique=True, index=True)
    email: Optional[str] = Field(default=None, unique=True, index=True)
    wallet_address: str = Field(unique=True, index=True)
    role: UserRole = Field(
        sa_column=Column(SQLAlchemyEnum(UserRole)), default=UserRole.ATTENDEE
    )
