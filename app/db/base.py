# all models will inherit from this base class
# app/db/base.py

from typing import Optional
from datetime import datetime, UTC

from sqlmodel import SQLModel, Field
from sqlalchemy import event


from sqlalchemy import Column, DateTime, Boolean


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True)))
    deleted_at: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True)))
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


class IDMixin(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)


# Common base class for all models
class BaseModel(IDMixin, TimestampMixin, SQLModel):
    pass
