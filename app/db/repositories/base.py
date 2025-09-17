from typing import Generic, Type, TypeVar, Optional
from datetime import datetime, UTC
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession


ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.exec(stmt)
        return result.one_or_none()

    async def get_by_ids(self, ids: list[int]) -> list[ModelType]:
        stmt = select(self.model).where(self.model.id.in_(ids))
        result = await self.session.exec(stmt)
        return result.all()

    async def get_all(self) -> list[ModelType]:
        stmt = select(self.model)
        result = await self.session.exec(stmt)
        return result.all()

    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == obj.id)
        result = await self.session.exec(stmt)
        existing_obj = result.one_or_none()

        if existing_obj:
            for key, value in obj.model_dump(exclude_unset=True).items():
                setattr(existing_obj, key, value)
            await self.session.commit()
            await self.session.refresh(existing_obj)
            return existing_obj
        return None

    async def delete(self, id: int) -> bool:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.exec(stmt)
        existing_obj = result.one_or_none()

        if existing_obj:
            await self.session.delete(existing_obj)
            await self.session.commit()
            return True
        return False

    async def soft_delete(self, id: int) -> bool:
        """Soft delete by setting deleted_at timestamp and is_deleted flag"""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.exec(stmt)
        existing_obj = result.one_or_none()

        if existing_obj:
            existing_obj.deleted_at = datetime.now(UTC)
            existing_obj.is_deleted = True
            await self.session.commit()
            await self.session.refresh(existing_obj)
            return True
        return False
