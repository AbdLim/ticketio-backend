from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.db.repositories.todo import TodoRepository
from app.services.todo import TodoService
from app.utils.cache import get_cache

router = APIRouter(prefix="/todos", tags=["todos"])


async def get_todo_service(
    session: AsyncSession = Depends(get_session), cache=Depends(get_cache)
) -> TodoService:
    repository = TodoRepository(session)
    return TodoService(repository, cache)


@router.post("", response_model=TodoResponse)
async def create_todo(
    todo_data: TodoCreate, service: TodoService = Depends(get_todo_service)
) -> TodoResponse:
    """Create a new todo item"""
    return await service.create(todo_data)


@router.get("", response_model=List[TodoResponse])
async def list_todos(
    completed: bool = Query(None, description="Filter by completion status"),
    priority: int = Query(None, ge=1, le=5, description="Filter by priority"),
    service: TodoService = Depends(get_todo_service),
) -> List[TodoResponse]:
    """List all todos with optional filters"""
    if completed is not None:
        return await service.get_completed()
    elif priority is not None:
        return await service.get_by_priority(priority)
    return await service.get_all()


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int, service: TodoService = Depends(get_todo_service)
) -> TodoResponse:
    """Get a specific todo by ID"""
    todo = await service.get_by_id(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Update a todo item"""
    updated_todo = await service.update(todo_id, todo_data)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo


@router.delete("/{todo_id}", response_model=bool)
async def delete_todo(
    todo_id: int,
    soft: bool = Query(True, description="Use soft delete (default) or hard delete"),
    service: TodoService = Depends(get_todo_service),
) -> bool:
    """Delete a todo item (soft delete by default)"""
    deleted = await service.delete(todo_id, soft=soft)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
    return True


@router.get("/search/{title}", response_model=TodoResponse)
async def search_todo_by_title(
    title: str, service: TodoService = Depends(get_todo_service)
) -> TodoResponse:
    """Search for a todo by title"""
    todo = await service.get_by_title(title)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
