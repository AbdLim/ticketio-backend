from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = Field(default=None)
    priority: int = Field(1, ge=1, le=5)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=1, le=5)


class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
