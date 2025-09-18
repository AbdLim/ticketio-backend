from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_wallet(self, wallet_address: str) -> Optional[User]:
        """
        Get a user by their wallet address.
        """
        query = select(User).where(User.wallet_address == wallet_address)
        result = await self.session.exec(query)
        return result.first()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email address.
        """
        query = select(User).where(User.email == email)
        result = await self.session.exec(query)
        return result.first()
