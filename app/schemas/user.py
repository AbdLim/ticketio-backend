from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.db.models.user import UserRole


class UserBase(BaseModel):
    wallet_address: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: UserRole = UserRole.ATTENDEE


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    pass


class UserWithToken(UserResponse):
    token: str


class UserWithBalance(UserResponse):
    hbar_balance: float
    last_balance_check: datetime


class UserWithTokenAndBalance(UserWithBalance):
    token: str
