from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.repositories.base import BaseRepository
from app.db.models.todo import Todo


class TodoRepository(BaseRepository[Todo]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Todo)

    async def get_by_title(self, title: str) -> Optional[Todo]:
        stmt = select(self.model).where(self.model.title == title)
        result = await self.session.exec(stmt)
        return result.one_or_none()

    async def get_completed(self) -> List[Todo]:
        stmt = select(self.model).where(self.model.completed == True)
        result = await self.session.exec(stmt)
        return result.all()

    async def get_by_priority(self, priority: int) -> List[Todo]:
        stmt = select(self.model).where(self.model.priority == priority)
        result = await self.session.exec(stmt)
        return result.all()
