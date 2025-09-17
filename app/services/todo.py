from typing import List, Optional
import json
from datetime import datetime

from app.db.repositories.todo import TodoRepository
from app.db.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate
from app.utils.cache import Redis


class TodoService:
    def __init__(self, repository: TodoRepository, cache: Redis):
        self.repository = repository
        self.cache = cache
        self.cache_prefix = "todo:"
        self.list_cache_key = "todos:all"

    async def _get_from_cache(self, todo_id: int) -> Optional[Todo]:
        cached_todo = await self.cache.get(f"{self.cache_prefix}{todo_id}")
        if cached_todo:
            # Convert string dates back to datetime objects
            if cached_todo.get("due_date"):
                cached_todo["due_date"] = datetime.fromisoformat(
                    cached_todo["due_date"]
                )
            if cached_todo.get("created_at"):
                cached_todo["created_at"] = datetime.fromisoformat(
                    cached_todo["created_at"]
                )
            if cached_todo.get("updated_at"):
                cached_todo["updated_at"] = datetime.fromisoformat(
                    cached_todo["updated_at"]
                )
            if cached_todo.get("deleted_at"):
                cached_todo["deleted_at"] = datetime.fromisoformat(
                    cached_todo["deleted_at"]
                )
            return Todo(**cached_todo)
        return None

    async def _set_cache(self, todo: Todo):
        todo_dict = todo.model_dump()
        # Convert datetime objects to ISO format strings for JSON serialization
        if todo_dict.get("due_date"):
            todo_dict["due_date"] = todo_dict["due_date"].isoformat()
        if todo_dict.get("created_at"):
            todo_dict["created_at"] = todo_dict["created_at"].isoformat()
        if todo_dict.get("updated_at"):
            todo_dict["updated_at"] = todo_dict["updated_at"].isoformat()
        if todo_dict.get("deleted_at"):
            todo_dict["deleted_at"] = todo_dict["deleted_at"].isoformat()
        await self.cache.set(
            f"{self.cache_prefix}{todo.id}",
            todo_dict,  # Redis client will handle JSON encoding
            expire=3600,  # Cache for 1 hour
        )
        await self.cache.delete(self.list_cache_key)  # Invalidate list cache

    async def get_by_id(self, todo_id: int) -> Optional[Todo]:
        # Try to get from cache first
        cached_todo = await self._get_from_cache(todo_id)
        if cached_todo:
            return cached_todo

        # If not in cache, get from database
        todo = await self.repository.get_by_id(todo_id)
        if todo:
            await self._set_cache(todo)
        return todo

    async def get_all(self) -> List[Todo]:
        # Try to get from cache first
        cached_list = await self.cache.get(self.list_cache_key)
        if cached_list:
            todos = []
            for todo_data in cached_list:  # Redis client already decoded the JSON
                # Convert ISO format strings back to datetime objects
                if todo_data.get("due_date"):
                    todo_data["due_date"] = datetime.fromisoformat(
                        todo_data["due_date"]
                    )
                if todo_data.get("created_at"):
                    todo_data["created_at"] = datetime.fromisoformat(
                        todo_data["created_at"]
                    )
                if todo_data.get("updated_at"):
                    todo_data["updated_at"] = datetime.fromisoformat(
                        todo_data["updated_at"]
                    )
                if todo_data.get("deleted_at"):
                    todo_data["deleted_at"] = datetime.fromisoformat(
                        todo_data["deleted_at"]
                    )
                todos.append(Todo(**todo_data))
            return todos

        # If not in cache, get from database
        todos = await self.repository.get_all()
        if todos:
            todos_data = []
            for todo in todos:
                todo_dict = todo.model_dump()
                # Convert datetime objects to ISO format strings
                if todo_dict.get("due_date"):
                    todo_dict["due_date"] = todo_dict["due_date"].isoformat()
                if todo_dict.get("created_at"):
                    todo_dict["created_at"] = todo_dict["created_at"].isoformat()
                if todo_dict.get("updated_at"):
                    todo_dict["updated_at"] = todo_dict["updated_at"].isoformat()
                if todo_dict.get("deleted_at"):
                    todo_dict["deleted_at"] = todo_dict["deleted_at"].isoformat()
                todos_data.append(todo_dict)
            await self.cache.set(
                self.list_cache_key,
                todos_data,  # Redis client will handle JSON encoding
                expire=3600,  # Cache for 1 hour
            )
        return todos

    async def create(self, todo_data: TodoCreate) -> Todo:
        todo = Todo(**todo_data.model_dump())
        created_todo = await self.repository.create(todo)
        await self._set_cache(created_todo)
        return created_todo

    async def update(self, todo_id: int, todo_data: TodoUpdate) -> Optional[Todo]:
        existing_todo = await self.repository.get_by_id(todo_id)
        if not existing_todo:
            return None

        # Update only provided fields
        update_data = todo_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_todo, key, value)

        updated_todo = await self.repository.update(existing_todo)
        if updated_todo:
            await self._set_cache(updated_todo)
        return updated_todo

    async def delete(self, todo_id: int, soft: bool = True) -> bool:
        if soft:
            deleted = await self.repository.soft_delete(todo_id)
        else:
            deleted = await self.repository.delete(todo_id)

        if deleted:
            await self.cache.delete(f"{self.cache_prefix}{todo_id}")
            await self.cache.delete(self.list_cache_key)
        return deleted

    async def get_by_title(self, title: str) -> Optional[Todo]:
        return await self.repository.get_by_title(title)

    async def get_completed(self) -> List[Todo]:
        return await self.repository.get_completed()

    async def get_by_priority(self, priority: int) -> List[Todo]:
        return await self.repository.get_by_priority(priority)
