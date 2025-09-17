from typing import Optional
from datetime import datetime
from sqlmodel import Field
from sqlalchemy import Column, DateTime

from app.db.base import BaseModel


class Todo(BaseModel, table=True):
    __tablename__ = "todos"

    title: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=True)))
    priority: int = Field(default=1, ge=1, le=5)  # Priority from 1-5
