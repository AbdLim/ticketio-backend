# all models will inherit from this base class
# app/db/base.py

from typing import Optional
from datetime import datetime
from uuid import uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import event, Column, DateTime


class BaseModel(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.utcnow())
    updated_at: Optional[datetime] = Field(default=None)
    is_deleted: bool = Field(default=False)


# Hook into before_insert and before_update
@event.listens_for(SQLModel, "before_insert", propagate=True)
def set_created_at(_, __, target):
    if hasattr(target, "created_at") and target.created_at is None:
        target.created_at = datetime.utcnow()  # Use timezone-naive UTC


@event.listens_for(SQLModel, "before_update", propagate=True)
def set_updated_at(_, __, target):
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.utcnow()  # Use timezone-naive UTC
