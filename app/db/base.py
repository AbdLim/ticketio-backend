# all models will inherit from this base class
# app/db/base.py

from typing import Optional
from datetime import datetime, UTC
from uuid import uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import event


from sqlalchemy import Column, DateTime


class BaseModel(SQLModel):
    id: str = Field(default_factory=uuid4, primary_key=True)
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(UTC), nullable=True
    )
    updated_at: Optional[datetime] = Field(default=None)
    is_deleted: bool = Field(default=False)


# Hook into before_insert and before_update
@event.listens_for(SQLModel, "before_insert", propagate=True)
def set_created_at(_, __, target):
    if hasattr(target, "created_at") and target.created_at is None:
        target.created_at = datetime.now(UTC)


@event.listens_for(SQLModel, "before_update", propagate=True)
def set_updated_at(_, __, target):
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.now(UTC)
